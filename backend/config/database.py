import os

import motor.motor_asyncio
from pymongo.database import Database

MONGO_DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://mongodb:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DATABASE_URL)

db: Database = client.translatar_db
