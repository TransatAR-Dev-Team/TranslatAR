from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class Conversation(BaseModel):
    """Model representing a conversation session"""

    id: Optional[str] = None
    userId: str
    title: Optional[str] = None
    source_lang: str
    target_lang: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool = True
    translation_count: int = 0


class ConversationTranslation(BaseModel):
    """Individual translation item within a conversation"""

    conversation_id: str
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    userId: str
    timestamp: datetime
    sequence_number: int


class StartConversationRequest(BaseModel):
    """Request to start a new conversation"""

    source_lang: str = "en"
    target_lang: str = "es"


class ConversationListResponse(BaseModel):
    """Response containing list of conversations"""

    conversations: List[dict]


class ConversationDetailResponse(BaseModel):
    """Response containing conversation details"""

    conversation: dict
    translations: List[dict]
