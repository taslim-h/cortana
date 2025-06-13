# # backend/app/models/user.py
# from pydantic import BaseModel, EmailStr, Field
# from typing import Optional, List
# from datetime import datetime
# from bson import ObjectId


# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")


# class UserBase(BaseModel):
#     email: EmailStr
#     firebase_uid: str
#     display_name: Optional[str] = None
#     photo_url: Optional[str] = None


# class UserCreate(UserBase):
#     pass


# class UserInDB(UserBase):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     google_tokens: Optional[dict] = None
#     calendar_integrated: bool = False

#     class Config:
#         allow_population_by_field_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}


# backend/app/models/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        return core_schema.json_or_python_schema(
            python_schema=core_schema.any_schema(),
            json_schema=core_schema.str_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string"}

    # Add  method to ensure string conversion
    def __str__(self):
        return str(super())


class UserBase(BaseModel):
    email: EmailStr
    firebase_uid: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    google_tokens: Optional[dict] = None
    calendar_integrated: bool = False

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
    }
