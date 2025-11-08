import pytest
from bson import ObjectId

from services.user_service import get_or_create_user_by_google_id

# Use the pytest marker for all tests in this file
pytestmark = pytest.mark.asyncio


class MockUserCollection:
    """A mock of Motor's AsyncIOMotorCollection for in-memory testing."""

    def __init__(self):
        # This dictionary will act as our in-memory database
        self._data = {}
        self.insert_one_was_called = False

    async def find_one(self, query: dict):
        """Simulates finding a document."""
        google_id = query.get("googleId")
        # Return a copy to prevent tests from modifying the mock's internal state
        return self._data.get(google_id, {}).copy() or None

    async def insert_one(self, doc: dict):
        """Simulates inserting a new document."""
        self.insert_one_was_called = True
        google_id = doc.get("googleId")
        if google_id in self._data:
            # Simulate a unique index constraint failure
            raise Exception("Duplicate key error")

        # Simulate MongoDB adding an _id
        doc_with_id = {"_id": ObjectId(), **doc}
        self._data[google_id] = doc_with_id

    def reset(self):
        """Resets the mock's state between tests."""
        self._data = {}
        self.insert_one_was_called = False


@pytest.fixture
def mock_users_collection() -> MockUserCollection:
    """Provides a fresh instance of the mock collection for each test."""
    return MockUserCollection()


async def test_get_or_create_user_returns_existing_user(mock_users_collection):
    """
    Tests that if a user with the given Google ID already exists,
    the function returns that user and does not attempt to create a new one.
    """
    # Arrange: Pre-populate the mock database with an existing user
    existing_user_id = ObjectId()
    existing_user_google_id = "existing_google_id_123"
    mock_users_collection._data[existing_user_google_id] = {
        "_id": existing_user_id,
        "googleId": existing_user_google_id,
        "email": "existing@test.com",
        "username": "existing",
    }

    # Act: Call the service function
    result = await get_or_create_user_by_google_id(
        users_collection=mock_users_collection,
        google_id=existing_user_google_id,
        email="irrelevant@email.com",  # Email should be ignored if user exists
    )

    # Assert: Check that the correct user was returned and no new user was created
    assert result is not None
    assert result["_id"] == existing_user_id
    assert result["googleId"] == existing_user_google_id
    assert (
        not mock_users_collection.insert_one_was_called
    ), "insert_one should not have been called for an existing user"


async def test_get_or_create_user_creates_new_user(mock_users_collection):
    """
    Tests that if a user does not exist, a new one is created with the
    correct details and then returned.
    """
    # Arrange: Define the new user's details
    new_user_google_id = "new_google_id_456"
    new_user_email = "newuser@test.com"

    # Act: Call the service function with a non-existent user
    result = await get_or_create_user_by_google_id(
        users_collection=mock_users_collection,
        google_id=new_user_google_id,
        email=new_user_email,
    )

    # Assert: Check that a new user was created and returned with the correct fields
    assert result is not None
    assert (
        mock_users_collection.insert_one_was_called
    ), "insert_one should have been called for a new user"

    # Verify the returned data
    assert "_id" in result
    assert result["googleId"] == new_user_google_id
    assert result["email"] == new_user_email
    assert result["username"] == "newuser"  # Check that username is derived correctly
    assert "createdAt" in result
    assert "updatedAt" in result


async def test_get_or_create_user_handles_db_error_on_create(mock_users_collection):
    """
    Tests that if the database fails during insertion, the function
    handles the exception gracefully and returns None.
    """

    # Arrange: Configure the mock to fail on insertion
    async def fail_insert(*args, **kwargs):
        raise Exception("Simulated database connection error")

    mock_users_collection.insert_one = fail_insert

    # Act: Call the service function
    result = await get_or_create_user_by_google_id(
        users_collection=mock_users_collection,
        google_id="any_id",
        email="any@email.com",
    )

    # Assert: The function should return None as it failed to create the user
    assert result is None
