"""Conversation session management API routes"""

from fastapi import APIRouter, Depends, HTTPException, Request

from models.conversation import (
    ConversationDetailResponse,
    ConversationListResponse,
    StartConversationRequest,
)
from security.auth import get_current_user
from services.conversation_service import ConversationService

router = APIRouter()


def get_conversation_service(request: Request) -> ConversationService:
    """Create ConversationService instance"""
    return ConversationService(request.app.state.db)


@router.post("/start")
async def start_conversation(
    body: StartConversationRequest,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    """Start a new conversation session

    Returns:
        conversation_id: ID of the created conversation
    """
    user_id = str(current_user["_id"])

    conversation_id = await service.start_conversation(
        user_id=user_id,
        source_lang=body.source_lang,
        target_lang=body.target_lang,
    )

    return {"conversation_id": conversation_id}


@router.post("/{conversation_id}/end")
async def end_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    """End a conversation session

    Args:
        conversation_id: ID of the conversation to end
    """
    success = await service.end_conversation(conversation_id)

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "ended", "conversation_id": conversation_id}


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    """Get conversation details (including all translations)

    Args:
        conversation_id: ID of the conversation to retrieve

    Returns:
        conversation: Conversation info
        translations: List of translations
    """
    user_id = str(current_user["_id"])

    result = await service.get_conversation_with_translations(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return result


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    """Get user's conversation list

    Args:
        limit: Maximum number of results (default: 20)

    Returns:
        conversations: List of conversations
    """
    user_id = str(current_user["_id"])

    conversations = await service.get_user_conversations(
        user_id=user_id,
        limit=limit,
    )

    return {"conversations": conversations}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    """Delete a conversation

    Args:
        conversation_id: ID of the conversation to delete
    """
    user_id = str(current_user["_id"])

    success = await service.delete_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "deleted", "conversation_id": conversation_id}
