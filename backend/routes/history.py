from fastapi import APIRouter, HTTPException, Request
from security.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_history(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Retrieves the translation records for the authenticated user.
    """
    try:
        translations_collection = request.app.state.db.get_collection("translations")
        
        # Filter by userId
        user_id = str(current_user["_id"])
        history_cursor = translations_collection.find({"userId": user_id}).sort("timestamp", -1).limit(50)

        history_list = []
        async for doc in history_cursor:
            doc["_id"] = str(doc["_id"])
            history_list.append(doc)

        return {"history": history_list}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve history from database: {e}"
        ) from e
