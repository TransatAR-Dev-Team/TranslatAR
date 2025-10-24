"""
Database client for TranslatAR backend
Handles MongoDB operations for user management and other data
"""

import os
from pymongo import MongoClient
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseClient:
    """MongoDB client for TranslatAR backend"""
    
    def __init__(self):
        """Initialize database connection"""
        self.database_url = os.getenv("DATABASE_URL", "mongodb://mongodb:27017")
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.database_url)
            self.db = self.client.translatar
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def create_or_update_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user or update existing user based on email
        
        Args:
            user_info: Dictionary containing user information
                - email: User's email address (required)
                - name: User's display name
                - picture: User's profile picture URL
                - sub: Google user ID
        
        Returns:
            Dictionary containing the user document with _id
        """
        try:
            email = user_info.get("email")
            if not email:
                raise ValueError("Email is required for user creation/update")
            
            # Check if user already exists
            existing_user = self.db.users.find_one({"email": email})
            
            if existing_user:
                # Update existing user
                update_data = {
                    "name": user_info.get("name", existing_user.get("name", "")),
                    "picture": user_info.get("picture", existing_user.get("picture", "")),
                    "sub": user_info.get("sub", existing_user.get("sub", "")),
                    "last_login": user_info.get("last_login")
                }
                
                # Remove None values
                update_data = {k: v for k, v in update_data.items() if v is not None}
                
                result = self.db.users.update_one(
                    {"email": email},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    logger.info(f"Updated user: {email}")
                    # Return updated user
                    return self.db.users.find_one({"email": email})
                else:
                    logger.info(f"No changes needed for user: {email}")
                    return existing_user
            else:
                # Create new user
                user_doc = {
                    "email": email,
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture", ""),
                    "sub": user_info.get("sub", ""),
                    "created_at": user_info.get("created_at"),
                    "last_login": user_info.get("last_login")
                }
                
                # Remove None values
                user_doc = {k: v for k, v in user_doc.items() if v is not None}
                
                result = self.db.users.insert_one(user_doc)
                user_doc["_id"] = result.inserted_id
                
                logger.info(f"Created new user: {email}")
                return user_doc
                
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User's unique identifier
        
        Returns:
            User document or None if not found
        """
        try:
            from bson import ObjectId
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email
        
        Args:
            email: User's email address
        
        Returns:
            User document or None if not found
        """
        try:
            user = self.db.users.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID
        
        Args:
            user_id: User's unique identifier
        
        Returns:
            True if user was deleted, False otherwise
        """
        try:
            from bson import ObjectId
            result = self.db.users.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def get_all_users(self, limit: int = 100) -> list:
        """
        Get all users with optional limit
        
        Args:
            limit: Maximum number of users to return
        
        Returns:
            List of user documents
        """
        try:
            users = list(self.db.users.find().limit(limit))
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def create_user_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """
        Create a user session
        
        Args:
            user_id: User's unique identifier
            session_data: Session information
        
        Returns:
            Session ID
        """
        try:
            from bson import ObjectId
            session_doc = {
                "user_id": ObjectId(user_id),
                "session_data": session_data,
                "created_at": session_data.get("created_at"),
                "expires_at": session_data.get("expires_at")
            }
            
            result = self.db.sessions.insert_one(session_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            raise
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user session by session ID
        
        Args:
            session_id: Session's unique identifier
        
        Returns:
            Session document or None if not found
        """
        try:
            from bson import ObjectId
            session = self.db.sessions.find_one({"_id": ObjectId(session_id)})
            return session
        except Exception as e:
            logger.error(f"Error getting user session {session_id}: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
