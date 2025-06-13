# backend/app/services/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from typing import Optional


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = MongoDB()


async def init_db():
    """Initialize MongoDB connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]

    # Create indexes
    await create_indexes()


async def create_indexes():
    """Create database indexes for better performance"""
    # User collection indexes
    users_collection = db.database["users"]
    await users_collection.create_index("firebase_uid", unique=True)
    await users_collection.create_index("email", unique=True)

    # Meeting collection indexes
    meetings_collection = db.database["meetings"]
    await meetings_collection.create_index("user_id")
    await meetings_collection.create_index([("user_id", 1), ("start_time", -1)])


async def close_db():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()


def get_database():
    """Get database instance"""
    return db.database

# Collection getters


def get_users_collection():
    return db.database["users"]


def get_meetings_collection():
    return db.database["meetings"]
