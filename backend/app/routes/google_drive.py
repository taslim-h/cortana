# # backend/app/routes/google_drive.py
# from pydantic import BaseModel
# from fastapi import APIRouter, HTTPException, status, Depends, Query
# from app.models.user import UserInDB
# from app.routes.auth import get_current_user
# from app.services.mongodb import get_meetings_collection
# from app.services.google_services import (
#     get_google_auth_flow,
#     get_credentials_from_token,
#     get_drive_service,
#     refresh_google_token
# )
# from bson import ObjectId
# from datetime import datetime, timezone
# import re

# router = APIRouter()

# class DriveCallbackRequest(BaseModel):
#     code: str
#     redirect_uri: str

# class LinkFolderRequest(BaseModel):
#     folder_id: str
#     folder_name: str
#     folder_url: str
#     access_token: dict

# @router.post("/authorize")
# async def authorize_drive(
#     current_user: UserInDB = Depends(get_current_user),
#     redirect_uri: str = Query(default=None)
# ):
#     """Get Google Drive authorization URL for picker"""
#     # Support both old callback and new picker callback
#     if not redirect_uri:
#         redirect_uri = "http://localhost:3000/drive-picker-callback.html"
    
#     print(f"Drive authorize - Using redirect_uri: {redirect_uri}")

#     flow = get_google_auth_flow(redirect_uri)
#     auth_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true',
#         prompt='select_account consent',  # Force account selection
#         state=current_user.firebase_uid
#     )

#     print(f"Generated auth URL: {auth_url[:100]}...")
#     return {"auth_url": auth_url}

# @router.post("/callback")
# async def drive_callback(
#     request: DriveCallbackRequest,
#     current_user: UserInDB = Depends(get_current_user)
# ):
#     """Handle Google Drive OAuth callback"""
#     try:
#         print(f"Drive callback - Code: {request.code[:20]}..., Redirect URI: {request.redirect_uri}")

#         flow = get_google_auth_flow(request.redirect_uri)
#         flow.fetch_token(code=request.code)

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
#         print(f"Drive callback error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Failed to authorize: {str(e)}"
#         )

# @router.post("/meetings/{meeting_id}/link-folder")
# async def link_drive_folder(
#     meeting_id: str,
#     request: LinkFolderRequest,
#     current_user: UserInDB = Depends(get_current_user)
# ):
#     """Link Google Drive folder to a meeting using picker data"""
#     meetings_collection = get_meetings_collection()

#     if not ObjectId.is_valid(meeting_id):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid meeting ID"
#         )

#     # Verify access to folder using the provided token
#     try:
#         credentials = get_credentials_from_token(request.access_token)
#         service = await get_drive_service(credentials)

#         # Verify we can access the folder
#         folder = service.files().get(
#             fileId=request.folder_id,
#             fields="id,name,mimeType,webViewLink"
#         ).execute()

#         # Update meeting with folder info
#         result = await meetings_collection.update_one(
#             {
#                 "_id": ObjectId(meeting_id),
#                 "user_id": current_user.firebase_uid
#             },
#             {
#                 "$set": {
#                     "drive_folder_id": request.folder_id,
#                     "drive_folder_name": request.folder_name,
#                     "drive_folder_link": request.folder_url,  # Keep for compatibility
#                     "drive_access_token": request.access_token,
#                     "updated_at": datetime.now(timezone.utc)
#                 }
#             }
#         )

#         if result.matched_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Meeting not found"
#             )

#         return {
#             "message": "Folder linked successfully",
#             "folder_name": folder.get("name", request.folder_name),
#             "folder_id": request.folder_id,
#             "folder_url": folder.get("webViewLink", request.folder_url)
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Drive folder link error: {str(e)}")
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

#     if not meeting.get("drive_folder_id"):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No Google Drive folder linked to this meeting"
#         )

#     if not meeting.get("drive_access_token"):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Drive access not authorized. Please re-link the folder."
#         )

#     try:
#         credentials = get_credentials_from_token(meeting["drive_access_token"])

#         # Try to refresh token if expired
#         if credentials.expired and credentials.refresh_token:
#             new_tokens = await refresh_google_token(credentials)
#             if new_tokens:
#                 # Update stored tokens
#                 await meetings_collection.update_one(
#                     {"_id": ObjectId(meeting_id)},
#                     {"$set": {"drive_access_token": new_tokens}}
#                 )
#                 credentials = get_credentials_from_token(new_tokens)

#         service = await get_drive_service(credentials)

#         # Get folder contents
#         results = service.files().list(
#             q=f"'{meeting['drive_folder_id']}' in parents and trashed=false",
#             pageSize=100,
#             fields="files(id, name, mimeType, modifiedTime, size, webViewLink, iconLink)"
#         ).execute()

#         files = results.get('files', [])

#         return {
#             "folder_id": meeting["drive_folder_id"],
#             "folder_name": meeting.get("drive_folder_name", "Unknown"),
#             "files": files
#         }
#     except Exception as e:
#         print(f"Drive API Error: {str(e)}")
        
#         if "invalid_grant" in str(e) or "Token has been expired or revoked" in str(e):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Google Drive authorization has expired. Please re-link the folder."
#             )
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Failed to retrieve folder contents: {str(e)}"
#             )

# @router.delete("/meetings/{meeting_id}/unlink-folder")
# async def unlink_drive_folder(
#     meeting_id: str,
#     current_user: UserInDB = Depends(get_current_user)
# ):
#     """Remove Google Drive folder from a meeting"""
#     meetings_collection = get_meetings_collection()

#     if not ObjectId.is_valid(meeting_id):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid meeting ID"
#         )

#     result = await meetings_collection.update_one(
#         {
#             "_id": ObjectId(meeting_id),
#             "user_id": current_user.firebase_uid
#         },
#         {
#             "$unset": {
#                 "drive_folder_id": "",
#                 "drive_folder_name": "",
#                 "drive_folder_link": "",
#                 "drive_access_token": ""
#             },
#             "$set": {
#                 "updated_at": datetime.now(timezone.utc)
#             }
#         }
#     )

#     if result.matched_count == 0:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Meeting not found"
#         )

#     return {"message": "Folder unlinked successfully"}

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

router = APIRouter()

class DriveCallbackRequest(BaseModel):
    code: str
    redirect_uri: str

class LinkFolderRequest(BaseModel):
    folder_id: str
    folder_name: str
    folder_url: str
    access_token: dict

@router.post("/authorize")
async def authorize_drive(
    current_user: UserInDB = Depends(get_current_user),
    redirect_uri: str = Query(default=None)
):
    """Get Google Drive authorization URL for picker"""
    # Support both old callback and new picker callback
    if not redirect_uri:
        redirect_uri = "http://localhost:3000/drive-picker-callback.html"
    
    print(f"Drive authorize - Using redirect_uri: {redirect_uri}")

    flow = get_google_auth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account consent',  # Force account selection
        state=current_user.firebase_uid
    )

    print(f"Generated auth URL: {auth_url[:100]}...")
    return {"auth_url": auth_url}

@router.post("/callback")
async def drive_callback(
    request: DriveCallbackRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Handle Google Drive OAuth callback"""
    try:
        print(f"Drive callback - Code: {request.code[:20]}..., Redirect URI: {request.redirect_uri}")

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
    request: LinkFolderRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Link Google Drive folder to a meeting using picker data"""
    meetings_collection = get_meetings_collection()

    if not ObjectId.is_valid(meeting_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meeting ID"
        )

    # Verify access to folder using the provided token
    try:
        credentials = get_credentials_from_token(request.access_token)
        service = await get_drive_service(credentials)

        # Verify we can access the folder
        folder = service.files().get(
            fileId=request.folder_id,
            fields="id,name,mimeType,webViewLink"
        ).execute()

        # Update meeting with folder info
        result = await meetings_collection.update_one(
            {
                "_id": ObjectId(meeting_id),
                "user_id": current_user.firebase_uid
            },
            {
                "$set": {
                    "drive_folder_id": request.folder_id,
                    "drive_folder_name": request.folder_name,
                    "drive_folder_link": request.folder_url,  # Keep for compatibility
                    "drive_access_token": request.access_token,
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
            "folder_name": folder.get("name", request.folder_name),
            "folder_id": request.folder_id,
            "folder_url": folder.get("webViewLink", request.folder_url)
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

    if not meeting.get("drive_folder_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Google Drive folder linked to this meeting"
        )

    if not meeting.get("drive_access_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Drive access not authorized. Please re-link the folder."
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
            "folder_name": meeting.get("drive_folder_name", "Unknown"),
            "files": files
        }
    except Exception as e:
        print(f"Drive API Error: {str(e)}")
        
        if "invalid_grant" in str(e) or "Token has been expired or revoked" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google Drive authorization has expired. Please re-link the folder."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve folder contents: {str(e)}"
            )

@router.delete("/meetings/{meeting_id}/unlink-folder")
async def unlink_drive_folder(
    meeting_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Remove Google Drive folder from a meeting"""
    meetings_collection = get_meetings_collection()

    if not ObjectId.is_valid(meeting_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meeting ID"
        )

    result = await meetings_collection.update_one(
        {
            "_id": ObjectId(meeting_id),
            "user_id": current_user.firebase_uid
        },
        {
            "$unset": {
                "drive_folder_id": "",
                "drive_folder_name": "",
                "drive_folder_link": "",
                "drive_access_token": ""
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return {"message": "Folder unlinked successfully"}