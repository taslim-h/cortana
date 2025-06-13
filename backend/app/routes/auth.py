# backend/app/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Depends, Header
from app.services.firebase_auth import verify_firebase_token, get_user_info
from app.services.mongodb import get_users_collection
from app.models.user import UserCreate, UserInDB
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    token: str


router = APIRouter()


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = authorization.split(" ")[1]
    decoded_token = await verify_firebase_token(token)

    # Get or create user in MongoDB
    users_collection = get_users_collection()
    user = await users_collection.find_one({"firebase_uid": decoded_token["uid"]})

    if not user:
        # Create new user
        firebase_user = await get_user_info(decoded_token["uid"])
        new_user = UserCreate(
            email=firebase_user["email"],
            firebase_uid=firebase_user["uid"],
            display_name=firebase_user.get("display_name"),
            photo_url=firebase_user.get("photo_url")
        )

        user_dict = new_user.model_dump()
        user_dict["created_at"] = datetime.now(timezone.utc)
        user_dict["updated_at"] = datetime.now(timezone.utc)
        user_dict["calendar_integrated"] = False

        result = await users_collection.insert_one(user_dict)
        user = await users_collection.find_one({"_id": result.inserted_id})

    return UserInDB(**user)


@router.post("/verify")
async def verify_token(request: TokenRequest):
    """Verify Firebase token and return user info"""
    try:
        decoded_token = await verify_firebase_token(request.token)
        user_info = await get_user_info(decoded_token["uid"])

        # Get or create user in MongoDB
        users_collection = get_users_collection()
        user = await users_collection.find_one({"firebase_uid": user_info["uid"]})

        if not user:
            # Create new user
            new_user = UserCreate(
                email=user_info["email"],
                firebase_uid=user_info["uid"],
                display_name=user_info.get("display_name"),
                photo_url=user_info.get("photo_url")
            )

            user_dict = new_user.model_dump()
            user_dict["created_at"] = datetime.now(timezone.utc)
            user_dict["updated_at"] = datetime.now(timezone.utc)
            user_dict["calendar_integrated"] = False

            result = await users_collection.insert_one(user_dict)
            user = await users_collection.find_one({"_id": result.inserted_id})

        # Manually convert ObjectId to string
        if user and "_id" in user:
            user["_id"] = str(user["_id"])

        return {
            "user": UserInDB(**user).model_dump(by_alias=True),
            "firebase_user": user_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me")
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current user information"""
    user_data = current_user.model_dump(by_alias=True)

    # Ensure ObjectId is converted to string
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])

    return user_data


@router.post("/logout")
async def logout():
    """Logout endpoint (handled on client side)"""
    return {"message": "Logout successful"}
