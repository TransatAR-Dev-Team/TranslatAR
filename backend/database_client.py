"""
Async Database Client using Motor (Motor is async wrapper for PyMongo)
This ensures all database operations are non-blocking and work with async/await.
"""
import motor.motor_asyncio
from datetime import datetime
from typing import Optional, Dict
from bson import ObjectId

class DatabaseClient:
    """
    Async database client for user management.
    All methods use motor (async PyMongo) to avoid blocking the event loop.
    """
    
    def __init__(self, uri: str):
        """Initialize async MongoDB client."""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client["translatar_db"]
        self.users = self.db["users"]
    
    async def create_or_update_user(self, profile: Dict) -> Dict:
        """
        Create or update a user based on Google profile information.
        
        Args:
            profile: Dict with keys: google_id, email, name, picture
        
        Returns:
            Dict representing the user document
        """
        google_id = profile.get("google_id")
        if not google_id:
            raise ValueError("Profile missing google_id")
        
        # Check if user exists
        existing = await self.users.find_one({"google_id": google_id})
        
        if existing:
            # Update existing user
            update_data = {
                "email": profile.get("email", ""),
                "name": profile.get("name", ""),
                "picture": profile.get("picture", ""),
                "last_login": datetime.utcnow()
            }
            await self.users.update_one(
                {"_id": existing["_id"]},
                {"$set": update_data}
            )
            return existing
        else:
            # Create new user
            new_user = {
                "google_id": google_id,
                "email": profile.get("email", ""),
                "name": profile.get("name", ""),
                "picture": profile.get("picture", ""),
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
                "settings": {
                    "source_language": "en",
                    "target_language": "es",
                    "subtitle_font_size": 18,
                    "subtitle_color": "#FFFFFF"
                }
            }
            result = await self.users.insert_one(new_user)
            new_user["_id"] = result.inserted_id
            return new_user
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by MongoDB ObjectId.
        
        Args:
            user_id: String representation of MongoDB ObjectId
        
        Returns:
            User document or None
        """
        try:
            return await self.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict]:
        """
        Get user by Google ID.
        
        Args:
            google_id: Google user ID
        
        Returns:
            User document or None
        """
        return await self.users.find_one({"google_id": google_id})
