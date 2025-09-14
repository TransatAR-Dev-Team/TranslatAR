from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio

app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@router.get("/data")
def read_data():
    """Returns a simple JSON response."""
    return {"message": "Hello from the FastAPI backend!"}

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongodb:27017")
database = client.helloworld_db
message_collection = database.get_collection("messages")

@router.get("/db-hello")
async def read_db_hello():
    """
    Fetches a greeting from the database.
    If the greeting doesn't exist, it creates one.
    """
    greeting = await message_collection.find_one({"type": "greeting"})
    if not greeting:
        # If no document is found, create one for the first time
        await message_collection.insert_one(
            {"type": "greeting", "message": "Hello from MongoDB!"}
        )
        greeting = await message_collection.find_one({"type": "greeting"})

    return {"message": greeting["message"]}


app.include_router(router, prefix="/api")
