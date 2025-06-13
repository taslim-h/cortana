# # backend/app/routes/google_drive.py
# from fastapi import APIRouter, HTTPException, status, Depends, Query
# from app.models.user import UserInDB
# from app.routes.auth import get_current_user
# from app.services.mongodb import get_meetings_collection
# from app.services.google_services import (
#     get_google_auth_flow,
#     get_credentials_from_token,
#     get_drive_service
# )
# from bson import ObjectId
# import re

# router = APIRouter()


# def extract_folder_id(url: str) -> str:
#     """Extract folder ID from Google Drive URL"""
#     patterns = [
#         r"folders/([a-zA-Z0-9-_]+)",
#         r"id=([a-zA-Z0-9-_]+)",
#     ]

#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             return match.group(1)

#     raise ValueError("Invalid Google Drive folder URL")


# @router.post("/authorize")
# async def authorize_drive(
#     current_user: UserInDB = Depends(get_current_user),
#     redirect_uri: str = Query(default=None)
# ):
#     """Get Google Drive authorization URL"""
#     flow = get_google_auth_flow(redirect_uri)
#     auth_url, _ = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true',
#         prompt='consent'
#     )
#     return {"auth_url": auth_url}


# @router.post("/callback")
# async def drive_callback(
#     code: str,
#     current_user: UserInDB = Depends(get_current_user),
#     redirect_uri: str = Query(default=None)
# ):
#     """Handle Google Drive OAuth callback"""
#     try:
#         flow = get_google_auth_flow(redirect_uri)
#         flow.fetch_token(code=code)

#         credentials = flow.credentials
#         token_dict = {
#             "access_token": credentials.token,
#             "refresh_token": credentials.refresh_token,
#             "token_uri": credentials.token_uri,
#             "client_id": credentials.client_id,
#             "client_secret": credentials.client_secret,
#             "scopes": credentials.scopes
#         }

#         return {"message": "Authorization successful", "token": token_dict}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Failed to authorize: {str(e)}"
#         )


# @router.post("/meetings/{meeting_id}/link-folder")
# async def link_drive_folder(
#     meeting_id: str,
#     folder_url: str,
#     access_token: dict,
#     current_user: UserInDB = Depends(get_current_user)
# ):
#     """Link Google Drive folder to a meeting"""
#     meetings_collection = get_meetings_collection()

#     if not ObjectId.is_valid(meeting_id):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid meeting ID"
#         )

#     # Extract folder ID
#     try:
#         folder_id = extract_folder_id(folder_url)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid Google Drive folder URL"
#         )

#     # Verify access to folder
#     try:
#         credentials = get_credentials_from_token(access_token)
#         service = await get_drive_service(credentials)

#         # Test access by getting folder metadata
#         folder = service.files().get(fileId=folder_id).execute()

#         # Update meeting with folder link and access token
#         await meetings_collection.update_one(
#             {
#                 "_id": ObjectId(meeting_id),
#                 "user_id": current_user.firebase_uid
#             },
#             {
#                 "$set": {
#                     "drive_folder_link": folder_url,
#                     "drive_folder_id": folder_id,
#                     "drive_access_token": access_token,
#                     "updated_at": datetime.utcnow()
#                 }
#             }
#         )

#         return {
#             "message": "Folder linked successfully",
#             "folder_name": folder.get("name", "Unknown")
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Failed to access folder: {str(e)}"
#         )


# @router.get("/meetings/{meeting_id}/folder-contents")
# async def get_folder_contents(
#     meeting_id: str,
#     current_user: UserInDB = Depends(get_current_user)
# ):
#     """Get contents of linked Google Drive folder"""
#     meetings_collection = get_meetings_collection()

#     if not ObjectId.is_valid(meeting_id):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid meeting ID"
#         )

#     meeting = await meetings_collection.find_one({
#         "_id": ObjectId(meeting_id),
#         "user_id": current_user.firebase_uid
#     })

#     if not meeting:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Meeting not found"
#         )

#     if not meeting.get("drive_folder_id") or not meeting.get("drive_access_token"):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No Google Drive folder linked to this meeting"
#         )

#     try:
#         credentials = get_credentials_from_token(meeting["drive_access_token"])
#         service = await get_drive_service(credentials)

#         # Get folder contents
#         results = service.files().list(
#             q=f"'{meeting['drive_folder_id']}' in parents",
#             pageSize=100,
#             fields="files(id, name, mimeType, modifiedTime, size, webViewLink)"
#         ).execute()

#         files = results.get('files', [])

#         return {
#             "folder_id": meeting["drive_folder_id"],
#             "files": files
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Failed to retrieve folder contents: {str(e)}"
#         )

# backend/app/routes/google_drive.py
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import UserInDB
from app.routes.auth import get_current_user
from app.services.mongodb import get_meetings_collection
from app.services.google_services import (
    get_google_auth_flow,
    get_credentials_from_token,
    get_drive_service,
    refresh_google_token
)
from bson import ObjectId
from datetime import datetime, timezone
import re


class LinkDriveFolderRequest(BaseModel):
    folder_url: str
    access_token: dict


router = APIRouter()


def extract_folder_id(url: str) -> str:
    """Extract folder ID from Google Drive URL"""
    patterns = [
        r"folders/([a-zA-Z0-9-_]+)",
        r"id=([a-zA-Z0-9-_]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Invalid Google Drive folder URL")


@router.post("/authorize")
async def authorize_drive(
    current_user: UserInDB = Depends(get_current_user),
    redirect_uri: str = Query(default=None)
):
    """Get Google Drive authorization URL"""
    # Force the redirect URI to be consistent
    redirect_uri = redirect_uri or "http://localhost:3000/drive-callback.html"
    print(f"Drive authorize - Using redirect_uri: {redirect_uri}")

    flow = get_google_auth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account consent',  # Force account selection
        state=current_user.firebase_uid  # Pass user ID in state
    )

    print(f"Generated auth URL: {auth_url[:100]}...")
    return {"auth_url": auth_url}


class DriveCallbackRequest(BaseModel):
    code: str
    redirect_uri: str


@router.post("/callback")
async def drive_callback(
    request: DriveCallbackRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Handle Google Drive OAuth callback"""
    try:
        print(
            f"Drive callback - Code: {request.code[:20]}..., Redirect URI: {request.redirect_uri}")

        flow = get_google_auth_flow(request.redirect_uri)
        flow.fetch_token(code=request.code)

        credentials = flow.credentials
        token_dict = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

        return {"message": "Authorization successful", "token": token_dict}
    except Exception as e:
        print(f"Drive callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authorize: {str(e)}"
        )


@router.post("/meetings/{meeting_id}/link-folder")
async def link_drive_folder(
    meeting_id: str,
    request: LinkDriveFolderRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    folder_url = request.folder_url
    access_token = request.access_token
    """Link Google Drive folder to a meeting"""
    meetings_collection = get_meetings_collection()

    if not ObjectId.is_valid(meeting_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meeting ID"
        )

    # Extract folder ID
    try:
        folder_id = extract_folder_id(folder_url)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google Drive folder URL"
        )

    # Verify access to folder
    try:
        credentials = get_credentials_from_token(access_token)
        service = await get_drive_service(credentials)

        # Test access by getting folder metadata
        folder = service.files().get(fileId=folder_id, fields="id,name,mimeType").execute()

        # Update meeting with folder link and access token
        result = await meetings_collection.update_one(
            {
                "_id": ObjectId(meeting_id),
                "user_id": current_user.firebase_uid
            },
            {
                "$set": {
                    "drive_folder_link": folder_url,
                    "drive_folder_id": folder_id,
                    "drive_access_token": access_token,
                    "drive_account_email": None,  # We'll add this if we can get it
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )

        return {
            "message": "Folder linked successfully",
            "folder_name": folder.get("name", "Unknown"),
            "folder_id": folder_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Drive folder link error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to access folder: {str(e)}"
        )


@router.get("/meetings/{meeting_id}/folder-contents")
async def get_folder_contents(
    meeting_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get contents of linked Google Drive folder"""
    meetings_collection = get_meetings_collection()

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

    if not meeting.get("drive_folder_id") or not meeting.get("drive_access_token"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Google Drive folder linked to this meeting"
        )

     # Check for drive access token
    if not meeting.get("drive_access_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Drive access not authorized for this meeting. Please re-link the folder."
        )

    try:
        credentials = get_credentials_from_token(meeting["drive_access_token"])

        # Try to refresh token if expired
        if credentials.expired and credentials.refresh_token:
            new_tokens = await refresh_google_token(credentials)
            if new_tokens:
                # Update stored tokens
                await meetings_collection.update_one(
                    {"_id": ObjectId(meeting_id)},
                    {"$set": {"drive_access_token": new_tokens}}
                )
                credentials = get_credentials_from_token(new_tokens)

        service = await get_drive_service(credentials)

        # Get folder contents
        results = service.files().list(
            q=f"'{meeting['drive_folder_id']}' in parents and trashed=false",
            pageSize=100,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink, iconLink)"
        ).execute()

        files = results.get('files', [])

        return {
            "folder_id": meeting["drive_folder_id"],
            "files": files
        }
    except Exception as e:
        # Log the actual error for debugging
        print(f"Drive API Error: {str(e)}")

        # Check if it's an authentication error
        if "invalid_grant" in str(e) or "Token has been expired or revoked" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google Drive authorization has expired. Please re-authorize access."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve folder contents: {str(e)}"
            )


@router.get("/meetings/{meeting_id}/check-folder")
async def check_folder_status(
    meeting_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Check the status of a linked Google Drive folder"""
    meetings_collection = get_meetings_collection()

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

    status_info = {
        "has_folder_link": bool(meeting.get("drive_folder_link")),
        "has_folder_id": bool(meeting.get("drive_folder_id")),
        "has_access_token": bool(meeting.get("drive_access_token")),
        "folder_url": meeting.get("drive_folder_link", "Not set"),
        "folder_id": meeting.get("drive_folder_id", "Not extracted")
    }

    if meeting.get("drive_access_token"):
        try:
            credentials = get_credentials_from_token(
                meeting["drive_access_token"])
            status_info["token_expired"] = credentials.expired
            status_info["has_refresh_token"] = bool(credentials.refresh_token)
        except Exception as e:
            status_info["token_error"] = str(e)

    return status_info
