"""Conversation session management service"""

import logging
from datetime import UTC, datetime
from typing import Any, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class ConversationService:
    """Service class for managing conversation sessions"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversations = db.get_collection("conversations")
        self.translations = db.get_collection("translations")

    async def start_conversation(
        self,
        user_id: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """Start a new conversation session

        Args:
            user_id: User ID
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            ID of the created conversation
        """
        conversation = {
            "userId": user_id,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "started_at": datetime.now(UTC),
            "ended_at": None,
            "is_active": True,
            "translation_count": 0,
        }
        result = await self.conversations.insert_one(conversation)
        conversation_id = str(result.inserted_id)
        logger.info(f"Started new conversation: {conversation_id} for user: {user_id}")
        return conversation_id

    async def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation session

        Args:
            conversation_id: ID of the conversation to end

        Returns:
            Success status
        """
        try:
            result = await self.conversations.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": {"ended_at": datetime.now(UTC), "is_active": False}},
            )
            if result.modified_count > 0:
                logger.info(f"Ended conversation: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to end conversation {conversation_id}: {e}")
            return False

    async def get_active_conversation(self, user_id: str) -> Optional[str]:
        """Get user's active conversation

        Args:
            user_id: User ID

        Returns:
            Active conversation ID or None
        """
        conversation = await self.conversations.find_one(
            {"userId": user_id, "is_active": True},
            sort=[("started_at", -1)],
        )
        if conversation:
            return str(conversation["_id"])
        return None

    async def add_translation_to_conversation(
        self,
        conversation_id: str,
        original_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Add translation to a conversation

        Args:
            conversation_id: Conversation ID
            original_text: Original text
            translated_text: Translated text
            source_lang: Source language
            target_lang: Target language
            user_id: User ID

        Returns:
            Saved translation document
        """
        # Get current translation count for this conversation
        count = await self.translations.count_documents(
            {"conversation_id": conversation_id}
        )

        translation = {
            "conversation_id": conversation_id,
            "original_text": original_text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "userId": user_id,
            "timestamp": datetime.now(UTC),
            "sequence_number": count + 1,
        }

        await self.translations.insert_one(translation)

        # Update conversation translation count
        await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$inc": {"translation_count": 1}},
        )

        logger.info(
            f"Added translation #{count + 1} to conversation {conversation_id}"
        )
        return translation

    async def get_conversation_with_translations(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Get conversation with all translations

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for permission check, optional)

        Returns:
            Conversation info and translation list, or None
        """
        query: dict[str, Any] = {"_id": ObjectId(conversation_id)}
        if user_id:
            query["userId"] = user_id

        conversation = await self.conversations.find_one(query)
        if not conversation:
            return None

        conversation["_id"] = str(conversation["_id"])

        translations: List[dict[str, Any]] = []
        cursor = self.translations.find(
            {"conversation_id": conversation_id}
        ).sort("sequence_number", 1)

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            translations.append(doc)

        return {"conversation": conversation, "translations": translations}

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        include_active: bool = True,
    ) -> List[dict[str, Any]]:
        """Get all conversations for a user

        Args:
            user_id: User ID
            limit: Maximum number of results
            include_active: Whether to include active conversations

        Returns:
            List of conversations
        """
        query: dict[str, Any] = {"userId": user_id}
        if not include_active:
            query["is_active"] = False

        cursor = (
            self.conversations.find(query).sort("started_at", -1).limit(limit)
        )

        conversations: List[dict[str, Any]] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            conversations.append(doc)

        return conversations

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """Delete conversation (including translations)

        Args:
            conversation_id: ID of conversation to delete
            user_id: User ID (for permission check)

        Returns:
            Success status
        """
        # Verify conversation ownership
        conversation = await self.conversations.find_one(
            {"_id": ObjectId(conversation_id), "userId": user_id}
        )
        if not conversation:
            return False

        # Delete related translations
        await self.translations.delete_many({"conversation_id": conversation_id})

        # Delete conversation
        result = await self.conversations.delete_one(
            {"_id": ObjectId(conversation_id)}
        )

        if result.deleted_count > 0:
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        return False
