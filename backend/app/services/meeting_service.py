# backend/app/services/meeting_service.py
from app.services.mongodb import get_meetings_collection_async
from datetime import datetime
from typing import Optional
from bson import ObjectId


async def check_meeting_collision(
    user_id: str,
    start_time: datetime,
    end_time: datetime,
    exclude_meeting_id: Optional[str] = None
) -> Optional[dict]:
    """Check if a meeting time conflicts with existing meetings"""
    meetings_collection = get_meetings_collection_async()

    # Build query
    query = {
        "user_id": user_id,
        "$or": [
            # New meeting starts during existing meeting
            {
                "start_time": {"$lte": start_time},
                "end_time": {"$gt": start_time}
            },
            # New meeting ends during existing meeting
            {
                "start_time": {"$lt": end_time},
                "end_time": {"$gte": end_time}
            },
            # New meeting completely encompasses existing meeting
            {
                "start_time": {"$gte": start_time},
                "end_time": {"$lte": end_time}
            }
        ]
    }

    # Exclude current meeting if updating
    if exclude_meeting_id:
        query["_id"] = {"$ne": ObjectId(exclude_meeting_id)}

    conflicting_meeting = await meetings_collection.find_one(query)
    return conflicting_meeting
