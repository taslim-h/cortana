# backend/app/routes/meetings.py
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.meeting import MeetingCreate, MeetingUpdate, MeetingInDB
from app.models.user import UserInDB
from app.routes.auth import get_current_user
from app.services.mongodb import get_meetings_collection_async
from app.services.meeting_service import check_meeting_collision
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import Field

router = APIRouter()


@router.post("/", response_model=MeetingInDB)
async def create_meeting(
    meeting: MeetingCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new meeting"""
    meetings_collection = get_meetings_collection_async()

    # Check for collisions
    collision = await check_meeting_collision(
        current_user.firebase_uid,
        meeting.start_time,
        meeting.end_time
    )

    if collision:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Meeting time conflicts with existing meeting",
                "conflicting_meeting": {
                    "title": collision["title"],
                    "start_time": collision["start_time"].isoformat(),
                    "end_time": collision["end_time"].isoformat()
                }
            }
        )

    # Create meeting
    meeting_dict = meeting.model_dump()
    meeting_dict["user_id"] = current_user.firebase_uid
    meeting_dict["created_at"] = datetime.now(timezone.utc)
    meeting_dict["updated_at"] = datetime.now(timezone.utc)

    result = await meetings_collection.insert_one(meeting_dict)
    created_meeting = await meetings_collection.find_one({"_id": result.inserted_id})

    return MeetingInDB(**created_meeting)


@router.get("/", response_model=List[MeetingInDB])
async def get_meetings(
    current_user: UserInDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all meetings for the current user"""
    meetings_collection = get_meetings_collection_async()

    cursor = meetings_collection.find(
        {"user_id": current_user.firebase_uid}
    ).sort("start_time", -1).skip(skip).limit(limit)

    meetings = await cursor.to_list(length=limit)
    return [MeetingInDB(**meeting) for meeting in meetings]


@router.get("/{meeting_id}", response_model=MeetingInDB)
async def get_meeting(
    meeting_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific meeting"""
    meetings_collection = get_meetings_collection_async()

    if not ObjectId.is_valid(meeting_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meeting ID"
        )

    meeting = await meetings_collection.find_one({
        "_id": ObjectId(meeting_id),
        "user_id": current_user.firebase_uid
    })

    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return MeetingInDB(**meeting)


@router.put("/{meeting_id}", response_model=MeetingInDB)
async def update_meeting(
    meeting_id: str,
    meeting_update: MeetingUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update a meeting"""
    meetings_collection = get_meetings_collection_async()

    if not ObjectId.is_valid(meeting_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meeting ID"
        )

    # Get existing meeting
    existing_meeting = await meetings_collection.find_one({
        "_id": ObjectId(meeting_id),
        "user_id": current_user.firebase_uid
    })

    if not existing_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # Check for collisions if time is being updated
    update_dict = meeting_update.model_dump(exclude_unset=True)

    if "start_time" in update_dict or "end_time" in update_dict:
        start_time = update_dict.get(
            "start_time", existing_meeting["start_time"])
        end_time = update_dict.get("end_time", existing_meeting["end_time"])

        collision = await check_meeting_collision(
            current_user.firebase_uid,
            start_time,
            end_time,
            exclude_meeting_id=meeting_id
        )

        if collision:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Meeting time conflicts with existing meeting",
                    "conflicting_meeting": {
                        "title": collision["title"],
                        "start_time": collision["start_time"].isoformat(),
                        "end_time": collision["end_time"].isoformat()
                    }
                }
            )

    # Update meeting
    update_dict["updated_at"] = datetime.now(timezone.utc)

    await meetings_collection.update_one(
        {"_id": ObjectId(meeting_id)},
        {"$set": update_dict}
    )

    updated_meeting = await meetings_collection.find_one({"_id": ObjectId(meeting_id)})
    return MeetingInDB(**updated_meeting)


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a meeting"""
    meetings_collection = get_meetings_collection_async()

    if not ObjectId.is_valid(meeting_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meeting ID"
        )

    result = await meetings_collection.delete_one({
        "_id": ObjectId(meeting_id),
        "user_id": current_user.firebase_uid
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return {"message": "Meeting deleted successfully"}
