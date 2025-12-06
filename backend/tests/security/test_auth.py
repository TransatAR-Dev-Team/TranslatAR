from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from security import auth

# --- Tests for Configuration Failures ---


def test_create_access_token_missing_secret(monkeypatch):
    """Test that create_access_token raises RuntimeError if JWT_SECRET_KEY is missing."""
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", None)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY is not configured"):
        auth.create_access_token({"sub": "user123"})


@pytest.mark.asyncio
async def test_get_current_user_missing_secret(monkeypatch):
    """Test that get_current_user raises 500 if JWT_SECRET_KEY is missing."""
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", None)

    # Mock request object needed for get_current_user
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc:
        await auth.get_current_user(mock_request, "some_token")

    assert exc.value.status_code == 500
    assert "Server authentication is not configured" in exc.value.detail


# --- Tests for verify_jwt_token (Websocket Helper) ---


@pytest.mark.asyncio
async def test_verify_jwt_token_success(monkeypatch):
    """Test successful verification returns user ID."""
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", "test-secret")

    token = jwt.encode({"sub": "user_abc"}, "test-secret", algorithm="HS256")
    user_id = await auth.verify_jwt_token(token)

    assert user_id == "user_abc"


@pytest.mark.asyncio
async def test_verify_jwt_token_invalid_token(monkeypatch):
    """Test invalid token returns None (JWTError path)."""
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", "test-secret")

    # Sign with WRONG secret
    token = jwt.encode({"sub": "user_abc"}, "wrong-secret", algorithm="HS256")
    user_id = await auth.verify_jwt_token(token)

    assert user_id is None


@pytest.mark.asyncio
async def test_verify_jwt_token_missing_token_or_secret(monkeypatch):
    """Test returns None if token is empty or secret is missing."""
    # Case 1: Missing Secret
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", None)
    assert await auth.verify_jwt_token("some_token") is None

    # Case 2: Empty Token
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", "test-secret")
    assert await auth.verify_jwt_token("") is None


@pytest.mark.asyncio
async def test_verify_jwt_token_generic_exception(monkeypatch):
    """Test generic exception handling."""
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", "test-secret")

    # Force jwt.decode to raise a generic Exception (not JWTError)
    with patch("jose.jwt.decode", side_effect=Exception("Boom")):
        result = await auth.verify_jwt_token("valid_looking_token")
        assert result is None
