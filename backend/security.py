"""
Security module: Handles JWT signing, verification and Google ID Token verification
Uses JWKS for local verification to avoid calling Google API on every request
"""
import os
import jwt
import time
import httpx
from typing import Dict, Optional
from fastapi import HTTPException
from datetime import datetime, timedelta
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)

# JWKS cache (stores public keys in memory)
_jwks_cache: Optional[Dict] = None
_jwks_cache_time: Optional[datetime] = None
JWKS_CACHE_DURATION = timedelta(minutes=15)  # Cache for 15 minutes
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"


class JWTManager:
    """Application JWT manager class"""
    
    @staticmethod
    def get_secret() -> str:
        """Get JWT secret from environment variables"""
        secret = os.getenv("JWT_SECRET")
        if not secret:
            raise ValueError("JWT_SECRET environment variable not set")
        return secret
    
    @staticmethod
    def get_expire_minutes() -> int:
        """Get JWT expiration time in minutes from environment variables"""
        return int(os.getenv("JWT_EXPIRE_MIN", "1440"))  # Default 24 hours
    
    @staticmethod
    def create_token(user_id: str, email: str, name: str) -> str:
        """
        Create application JWT token
        
        Args:
            user_id: User ID
            email: User email
            name: User name
        
        Returns:
            JWT token string
        """
        secret = JWTManager.get_secret()
        expire_minutes = JWTManager.get_expire_minutes()
        
        payload = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "iat": int(time.time()),  # Issued at time
            "exp": int(time.time()) + (expire_minutes * 60)  # Expiration time
        }
        
        return jwt.encode(payload, secret, algorithm="HS256")
    
    @staticmethod
    def verify_token(token: str) -> Dict:
        """
        Verify application JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload
        
        Raises:
            HTTPException: If token is invalid or expired
        """
        secret = JWTManager.get_secret()
        
        try:
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


def _decode_base64_url(value: str) -> bytes:
    """Decode base64url encoded value"""
    value += '=' * (4 - len(value) % 4)  # Add padding
    return base64.urlsafe_b64decode(value)


def _jwks_to_pem(jwks_key: Dict) -> str:
    """Convert JWK to PEM format for verification"""
    # Extract modulus and exponent
    n = _decode_base64_url(jwks_key['n'])
    e = _decode_base64_url(jwks_key['e'])
    
    # Create RSA public key
    e_int = int.from_bytes(e, 'big')
    n_int = int.from_bytes(n, 'big')
    
    public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key(default_backend())
    
    # Serialize to PEM
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return pem.decode('utf-8')


class GoogleIDTokenVerifier:
    """Google ID Token verifier using JWKS local verification"""
    
    @staticmethod
    async def _fetch_jwks() -> Dict:
        """
        Fetch JWKS from Google (cached for 15 minutes)
        
        Returns:
            JWKS dictionary
        """
        global _jwks_cache, _jwks_cache_time
        
        now = datetime.now()
        
        # Return cached JWKS if still valid
        if _jwks_cache and _jwks_cache_time:
            if (now - _jwks_cache_time) < JWKS_CACHE_DURATION:
                logger.debug("Using cached JWKS")
                return _jwks_cache
        
        # Fetch new JWKS
        try:
            logger.info("Fetching JWKS from Google")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(GOOGLE_JWKS_URL)
                response.raise_for_status()
                _jwks_cache = response.json()
                _jwks_cache_time = now
                logger.info("JWKS cache refreshed")
                return _jwks_cache
        except httpx.TimeoutException:
            logger.error("Timeout fetching JWKS")
            raise HTTPException(status_code=503, detail="Failed to fetch Google public keys (timeout)")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching JWKS: {e.response.status_code}")
            raise HTTPException(status_code=503, detail="Failed to fetch Google public keys")
        except Exception as e:
            logger.error(f"Error fetching JWKS: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch Google public keys: {str(e)}")
    
    @staticmethod
    async def verify_id_token(id_token: str) -> Dict:
        """
        Verify Google ID Token using local JWKS validation
        
        This method:
        1. Fetches and caches Google's public keys (JWKS)
        2. Decodes the ID token header to get the key ID (kid)
        3. Verifies the signature using the corresponding public key
        4. Validates audience, expiration, and other claims
        
        Args:
            id_token: Google ID Token
        
        Returns:
            User claims dictionary
        
        Raises:
            HTTPException: If verification fails
        """
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not google_client_id:
            raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not configured")
        
        try:
            # Decode token header to get kid
            try:
                unverified_header = jwt.get_unverified_header(id_token)
                kid = unverified_header.get("kid")
                if not kid:
                    raise HTTPException(status_code=401, detail="Token missing kid in header")
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Invalid token header: {str(e)}")
            
            # Fetch JWKS (cached)
            jwks = await GoogleIDTokenVerifier._fetch_jwks()
            
            # Find the matching key
            key = None
            for jwks_key in jwks.get("keys", []):
                if jwks_key.get("kid") == kid:
                    key = jwks_key
                    break
            
            if not key:
                # Clear cache and try once more
                logger.warning(f"Key {kid} not found in JWKS cache, refreshing...")
                _jwks_cache = None
                _jwks_cache_time = None
                jwks = await GoogleIDTokenVerifier._fetch_jwks()
                for jwks_key in jwks.get("keys", []):
                    if jwks_key.get("kid") == kid:
                        key = jwks_key
                        break
                
                if not key:
                    raise HTTPException(status_code=401, detail=f"Public key {kid} not found")
            
            # Convert JWK to PEM for verification
            public_key_pem = _jwks_to_pem(key)
            
            # Verify the token signature and claims
            try:
                decoded = jwt.decode(
                    id_token,
                    public_key_pem,
                    algorithms=["RS256"],
                    audience=google_client_id,
                    options={"verify_signature": True, "verify_exp": True, "verify_aud": True}
                )
                
                # Verify required fields
                if "email" not in decoded:
                    raise HTTPException(status_code=400, detail="Token missing email claim")
                
                logger.info(f"Successfully verified ID token for user: {decoded.get('email')}")
                return decoded
                
            except jwt.ExpiredSignatureError:
                logger.warning("Token expired")
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.InvalidAudienceError:
                logger.warning("Token audience mismatch")
                raise HTTPException(status_code=403, detail="Token audience mismatch")
            except jwt.InvalidSignatureError:
                logger.warning("Invalid token signature")
                raise HTTPException(status_code=401, detail="Invalid token signature")
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid token: {e}")
                raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

