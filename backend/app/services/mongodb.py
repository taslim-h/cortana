# # backend/app/services/mongodb.py
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.config import settings
# from typing import Optional


# class MongoDB:
#     client: Optional[AsyncIOMotorClient] = None
#     database = None


# db = MongoDB()


# async def init_db():
#     """Initialize MongoDB connection"""
#     db.client = AsyncIOMotorClient(settings.MONGODB_URL)
#     db.database = db.client[settings.DATABASE_NAME]

#     # Create indexes
#     await create_indexes()


# async def create_indexes():
#     """Create database indexes for better performance"""
#     # User collection indexes
#     users_collection = db.database["users"]
#     await users_collection.create_index("firebase_uid", unique=True)
#     await users_collection.create_index("email", unique=True)

#     # Meeting collection indexes
#     meetings_collection = db.database["meetings"]
#     await meetings_collection.create_index("user_id")
#     await meetings_collection.create_index([("user_id", 1), ("start_time", -1)])


# async def close_db():
#     """Close MongoDB connection"""
#     if db.client:
#         db.client.close()


# def get_database():
#     """Get database instance"""
#     return db.database

# # Collection getters


# def get_users_collection():
#     return db.database["users"]


# def get_meetings_collection():
#     return db.database["meetings"]

# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo import MongoClient  # Added for sync access
# from app.config import settings
# from typing import Optional

# class MongoDB:
#     client_async: Optional[AsyncIOMotorClient] = None  # Async client
#     client_sync: Optional[MongoClient] = None         # Sync client
#     database_async = None
#     database_sync = None

# db = MongoDB()

# async def init_db():
#     """Initialize MongoDB connections (async and sync)"""
#     db.client_async = AsyncIOMotorClient(settings.MONGODB_URL)
#     db.database_async = db.client_async[settings.DATABASE_NAME]

#     db.client_sync = MongoClient(settings.MONGODB_URL)  # Sync client
#     db.database_sync = db.client_sync[settings.DATABASE_NAME]

#     # Create indexes (using async client)
#     await create_indexes()

# async def create_indexes():
#     """Create database indexes for better performance"""
#     # User collection indexes
#     users_collection = db.database_async["users"]
#     await users_collection.create_index("firebase_uid", unique=True)
#     await users_collection.create_index("email", unique=True)

#     # Meeting collection indexes
#     meetings_collection = db.database_async["meetings"]
#     await meetings_collection.create_index("user_id")
#     await meetings_collection.create_index([("user_id", 1), ("start_time", -1)])

# async def close_db():
#     """Close MongoDB connections"""
#     if db.client_async:
#         db.client_async.close()
#     if db.client_sync:
#         db.client_sync.close()

# # Async collection getters
# def get_database_async():
#     """Get async database instance"""
#     return db.database_async

# def get_users_collection_async():
#     """Get async users collection"""
#     return db.database_async["users"]

# def get_meetings_collection_async():
#     """Get async meetings collection"""
#     return db.database_async["meetings"]

# # Sync collection getters
# def get_database_sync():
#     """Get sync database instance"""
#     return db.database_sync

# def get_users_collection_sync():
#     """Get sync users collection"""
#     return db.database_sync["users"]

# def get_meetings_collection_sync():
#     """Get sync meetings collection"""
#     return db.database_sync["meetings"]


from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.config import settings
from typing import Optional

class MongoDB:
    client_async: Optional[AsyncIOMotorClient] = None
    client_sync: Optional[MongoClient] = None
    database_async = None
    database_sync = None

db = MongoDB()

async def init_db():
    """Initialize MongoDB connections (async and sync)"""
    db.client_async = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database_async = db.client_async[settings.DATABASE_NAME]

    db.client_sync = MongoClient(settings.MONGODB_URL)
    db.database_sync = db.client_sync[settings.DATABASE_NAME]

    # Create indexes
    await create_indexes()

async def create_indexes():
    """Create database indexes for better performance"""
    # User collection indexes
    users_collection = db.database_async["users"]
    await users_collection.create_index("firebase_uid", unique=True)
    await users_collection.create_index("email", unique=True)

    # Meeting collection indexes
    meetings_collection = db.database_async["meetings"]
    await meetings_collection.create_index("user_id")
    await meetings_collection.create_index([("user_id", 1), ("start_time", -1)])

    # Chat collection indexes (new)
    chats_collection = db.database_async["chats"]
    await chats_collection.create_index([("meeting_id", 1), ("timestamp", -1)])

async def close_db():
    """Close MongoDB connections"""
    if db.client_async:
        db.client_async.close()
    if db.client_sync:
        db.client_sync.close()

# Async collection getters
def get_database_async():
    return db.database_async

def get_users_collection_async():
    return db.database_async["users"]

def get_meetings_collection_async():
    return db.database_async["meetings"]

def get_chats_collection_async():
    return db.database_async["chats"]

# Sync collection getters
def get_database_sync():
    return db.database_sync

def get_users_collection_sync():
    return db.database_sync["users"]

def get_meetings_collection_sync():
    return db.database_sync["meetings"]

def get_chats_collection_sync():
    return db.database_sync["chats"]