import os
from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, Request, status
from pymongo.errors import DuplicateKeyError

router = APIRouter()
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")


def serialize_user(doc: dict) -> dict:
    if not doc:
        return {}
    result = {
        "googleId": doc.get("googleId"),
        "email": doc.get("email"),
        "username": doc.get("username"),
        "createdAt": doc.get("createdAt").isoformat() if doc.get("createdAt") else None,
        "updatedAt": doc.get("updatedAt").isoformat() if doc.get("updatedAt") else None,
    }

    if "_id" in doc:
        result["_id"] = str(doc["_id"])
    return result


@router.post("/google/login")
async def google_login(
    googleId: str | None = Body(default=None),
    email: str | None = Body(default=None),
    request: Request = None,
):
    if not googleId or not googleId.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Missing required fields (googleId, email)"},
        )
    if not email or not email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Missing required fields (googleId, email)"},
        )

    if "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Missing required fields (googleId, email)"},
        )

    db = request.app.state.db
    users = db[USERS_COLLECTION]

    existing = await users.find_one({"googleId": googleId})
    if existing:
        from fastapi.responses import JSONResponse

        return JSONResponse(content=serialize_user(existing), status_code=status.HTTP_200_OK)

    username = email.split("@")[0]

    doc = {
        "googleId": googleId,
        "email": email,
        "username": username,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }

    try:
        result = await users.insert_one(doc)
        created = await users.find_one({"_id": result.inserted_id})

        from fastapi.responses import JSONResponse

        return JSONResponse(content=serialize_user(created), status_code=status.HTTP_201_CREATED)
    except DuplicateKeyError as e:
        key = getattr(e, "details", {}).get("keyValue", {})
        key_value = {}
        if "googleId" in key:
            key_value = {"googleId": key["googleId"]}
        elif "email" in key:
            key_value = {"email": key["email"]}

        if key_value:
            conflicting_user = await users.find_one(key_value)
            if conflicting_user:
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    content=serialize_user(conflicting_user), status_code=status.HTTP_200_OK
                )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate googleId or email (user already exists)",
        ) from e

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login process",
        ) from ex
