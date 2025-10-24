from pymongo import MongoClient
from datetime import datetime

class DatabaseClient:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["translatar_db"]
        self.users = self.db["users"]

    def create_or_update_user(self, profile):
        """Create or update a user based on Google profile information."""
        existing = self.users.find_one({"google_id": profile["id"]})
        if existing:
            self.users.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "email": profile["email"], 
                    "name": profile.get("name", ""),
                    "picture": profile.get("picture", ""),
                    "last_login": datetime.utcnow()
                }}
            )
            return existing
        else:
            new_user = {
                "google_id": profile["id"],
                "email": profile["email"],
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
            result = self.users.insert_one(new_user)
            new_user["_id"] = result.inserted_id
            return new_user
    
    def get_user_by_id(self, user_id):
        """Get user by MongoDB ObjectId."""
        from bson import ObjectId
        return self.users.find_one({"_id": ObjectId(user_id)})
    
    def get_user_by_google_id(self, google_id):
        """Get user by Google ID."""
        return self.users.find_one({"google_id": google_id})

