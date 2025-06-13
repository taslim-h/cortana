# # backend/app/models/meeting.py
# from pydantic import BaseModel, Field, validator
# from typing import Optional
# from datetime import datetime, timezone
# from bson import ObjectId
# from .user import PyObjectId


# class MeetingBase(BaseModel):
#     title: str
#     start_time: datetime
#     end_time: datetime
#     meeting_link: Optional[str] = None
#     drive_folder_link: Optional[str] = None
#     description: Optional[str] = None


# class MeetingCreate(MeetingBase):
#     pass


# class MeetingUpdate(BaseModel):
#     title: Optional[str] = None
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] = None
#     meeting_link: Optional[str] = None
#     drive_folder_link: Optional[str] = None
#     description: Optional[str] = None


# class MeetingInDB(MeetingBase):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     user_id: str
#     created_at: datetime = Field(
#         default_factory=lambda: datetime.now(timezone.utc))
#     updated_at: datetime = Field(
#         default_factory=lambda: datetime.now(timezone.utc))
#     drive_access_token: Optional[dict] = None

#     @validator('end_time')
#     def end_time_must_be_after_start_time(cls, v, values):
#         if 'start_time' in values and v <= values['start_time']:
#             raise ValueError('end_time must be after start_time')
#         return v

#     class Config:
#         validate_by_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}

# backend/app/models/meeting.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from .user import PyObjectId


class MeetingBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    meeting_link: Optional[str] = None
    drive_folder_link: Optional[str] = None
    description: Optional[str] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    meeting_link: Optional[str] = None
    drive_folder_link: Optional[str] = None
    description: Optional[str] = None


class MeetingInDB(MeetingBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    drive_access_token: Optional[dict] = None

    @field_validator('end_time')
    def end_time_must_be_after_start_time(cls, v, info):
        start_time = info.data.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('end_time must be after start_time')
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
