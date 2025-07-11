# from datetime import datetime, timezone
# from app.services.mongodb import get_chats_collection_async
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# async def save_chat_message(meeting_id: str, user_message: str, ai_response: str):
#     chats_collection = get_chats_collection_async()
#     chat_doc = {
#         "meeting_id": meeting_id,
#         "user_message": user_message,
#         "ai_response": ai_response,
#         "timestamp": datetime.now(timezone.utc)
#     }
#     await chats_collection.insert_one(chat_doc)
#     logger.info(f"Saved chat message for meeting {meeting_id}")
from datetime import datetime, timezone
from app.services.mongodb import get_meetings_collection_async, get_chats_collection_async
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def save_chat_message(meeting_id: str, user_message: str, ai_response: str):
    """
    Save a chat message, updating the meeting's chat_history with a limit and the chats collection.
    """
    try:
        # Convert meeting_id to ObjectId if necessary
        try:
            meeting_obj_id = ObjectId(meeting_id)
        except Exception:
            meeting_obj_id = meeting_id  # fallback if already string or invalid

        # Get collections
        meetings_collection = get_meetings_collection_async()
        chats_collection = get_chats_collection_async()

        # Prepare chat document
        chat_doc = {
            "meeting_id": meeting_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": datetime.now(timezone.utc)
        }

        # Update meetings collection with chat history using pipeline to limit size
        new_chat = {
            "user_query": user_message,
            "response": ai_response,
            "timestamp": datetime.now(timezone.utc)
        }
        await meetings_collection.update_one(
            {"_id": meeting_obj_id},
            [
                {"$set": {"chat_history": {"$concatArrays": [{"$ifNull": ["$chat_history", []]}, [new_chat]]}}},
                {"$set": {"chat_history": {"$slice": ["$chat_history", -10]}}}
            ],
            upsert=False
        )

        # Save to chats collection for full audit log
        await chats_collection.insert_one(chat_doc)

        logger.info(f"Saved chat message for meeting {meeting_id}")
    except Exception as e:
        logger.error(f"Failed to save chat message for meeting {meeting_id}: {str(e)}", exc_info=True)
        raise