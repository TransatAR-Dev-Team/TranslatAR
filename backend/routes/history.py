from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("")
async def get_history(request: Request):
    """
    Retrieves the translation records from the database.
    """
    try:
        translations_collection = request.app.state.db.get_collection("translations")

        history_cursor = translations_collection.find({}).sort("timestamp", -1).limit(50)

        history_list = []
        async for doc in history_cursor:
            doc["_id"] = str(doc["_id"])
            history_list.append(doc)

        return {"history": history_list}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve history from database: {e}"
        ) from e
