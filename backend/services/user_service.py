from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorCollection


async def get_or_create_user_by_google_id(
    users_collection: AsyncIOMotorCollection, google_id: str, email: str
) -> dict | None:
    """
    Finds a user by their Google ID. If they don't exist, a new user is created.

    Args:
        users_collection: The Motor collection for users.
        google_id: The user's unique Google 'sub' ID.
        email: The user's email address from Google.

    Returns:
        The user document from the database (dict), or None if creation fails.
    """
    # heck if the user already exists
    user = await users_collection.find_one({"googleId": google_id})
    if user:
        return user

    # If not, create a new user document
    print(f"User with Google ID {google_id} not found. Creating new user.")
    username = email.split("@")[0]
    new_user_doc = {
        "googleId": google_id,
        "email": email,
        "username": username,
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }

    try:
        await users_collection.insert_one(new_user_doc)
        # Retrieve the newly created user to get the _id and confirm creation
        created_user = await users_collection.find_one({"googleId": google_id})
        return created_user
    except Exception as e:
        print(f"Error creating user in database: {e}")
        return None
