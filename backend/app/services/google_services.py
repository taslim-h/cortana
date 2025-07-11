# # backend/app/services/google_services.py
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from app.config import settings
# import json
# from langchain.docstore.document import Document
# import os
# import PyPDF2

# # SCOPES = [
# #     'https://www.googleapis.com/auth/drive.readonly',
# #     'https://www.googleapis.com/auth/drive.metadata.readonly',
# #     'https://www.googleapis.com/auth/calendar.readonly'
# # ]

# SCOPES = [
#     "https://www.googleapis.com/auth/calendar.readonly",
#     "https://www.googleapis.com/auth/drive.readonly",
#     "https://www.googleapis.com/auth/drive.metadata.readonly",
#     "https://www.googleapis.com/auth/userinfo.profile",
#     "https://www.googleapis.com/auth/userinfo.email",
#     "https://www.googleapis.com/auth/tasks.readonly",  # <-- Add this
#     "openid"
# ]


# def get_google_auth_flow(redirect_uri: str = None):
#     """Create Google OAuth2 flow"""
#     # Always use the exact same redirect URI
#     if not redirect_uri:
#         redirect_uri = "http://localhost:3000/drive-callback.html"

#     print(f"Creating auth flow with redirect_uri: {redirect_uri}")

#     client_config = {
#         "web": {
#             "client_id": settings.GOOGLE_CLIENT_ID,
#             "client_secret": settings.GOOGLE_CLIENT_SECRET,
#             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "redirect_uris": [redirect_uri]
#         }
#     }

#     flow = Flow.from_client_config(
#         client_config,
#         scopes=SCOPES,
#         redirect_uri=redirect_uri
#     )

#     return flow


# def get_credentials_from_token(token_dict: dict) -> Credentials:
#     """Create credentials from token dictionary"""
#     return Credentials(
#         token=token_dict.get("access_token"),
#         refresh_token=token_dict.get("refresh_token"),
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=settings.GOOGLE_CLIENT_ID,
#         client_secret=settings.GOOGLE_CLIENT_SECRET,
#         scopes=SCOPES
#     )


# async def get_drive_service(credentials: Credentials):
#     """Get Google Drive service"""
#     return build('drive', 'v3', credentials=credentials)


# async def get_calendar_service(credentials: Credentials):
#     """Get Google Calendar service"""
#     return build('calendar', 'v3', credentials=credentials)


# async def refresh_google_token(credentials: Credentials) -> dict:
#     """Refresh Google access token"""
#     if credentials.expired and credentials.refresh_token:
#         credentials.refresh(Request())
#         return {
#             "access_token": credentials.token,
#             "refresh_token": credentials.refresh_token,
#             "token_uri": credentials.token_uri,
#             "client_id": credentials.client_id,
#             "client_secret": credentials.client_secret,
#             "scopes": credentials.scopes
#         }
#     return None


# #  new function for drive file indexing

# def get_drive_service_db(drive_access_token):
#     credentials = Credentials(
#         token=drive_access_token["access_token"],
#         refresh_token=drive_access_token["refresh_token"],
#         token_uri=drive_access_token["token_uri"],
#         client_id=drive_access_token["client_id"],
#         client_secret=drive_access_token["client_secret"]
#     )
#     return build("drive", "v3", credentials=credentials)

# def save_drive_documents(drive_service, folder_id, meeting_id):
#     if not os.path.exists("temp_docs"):
#         os.makedirs("temp_docs")
#     meeting_dir = f"temp_docs/{meeting_id}"
#     if not os.path.exists(meeting_dir):
#         os.makedirs(meeting_dir)
    
#     documents = []
#     results = drive_service.files().list(q=f"'{folder_id}' in parents").execute()
#     files = results.get("files", [])
#     for file in files:
#         if file["mimeType"] == "application/pdf":
#             request = drive_service.files().get_media(fileId=file["id"])
#             file_path = f"{meeting_dir}/{file['id']}.pdf"
#             fh = open(file_path, "wb")
#             request.execute().download(fh)
#             fh.close()
#             with open(file_path, "rb") as f:
#                 pdf_reader = PyPDF2.PdfReader(f)
#                 text = ""
#                 for page in pdf_reader.pages:
#                     extracted_text = page.extract_text()
#                     if extracted_text:
#                         text += extracted_text + "\n"
#                 if text:
#                     documents.append(Document(page_content=text, metadata={"file_id": file["id"], "file_path": file_path}))
#             # Optional: Remove temp file after processing
#             # os.remove(file_path)
#     return documents

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import settings
# import json
from langchain.docstore.document import Document
import os
import logging

# from langchain.schema import Document



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/tasks.readonly",
    "openid"
]

def get_google_auth_flow(redirect_uri: str = None):
    """Create Google OAuth2 flow"""
    if not redirect_uri:
        redirect_uri = "http://localhost:3000/drive-callback.html"
    logger.info(f"Creating auth flow with redirect_uri: {redirect_uri}")

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow

def get_credentials_from_token(token_dict: dict) -> Credentials:
    """Create credentials from token dictionary"""
    return Credentials(
        token=token_dict.get("access_token"),
        refresh_token=token_dict.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )

async def get_drive_service(credentials: Credentials):
    """Get Google Drive service (async)"""
    logger.info("Building async Drive service")
    return build('drive', 'v3', credentials=credentials)

async def get_calendar_service(credentials: Credentials):
    """Get Google Calendar service"""
    return build('calendar', 'v3', credentials=credentials)

async def refresh_google_token(credentials: Credentials) -> dict:
    """Refresh Google access token"""
    if credentials.expired and credentials.refresh_token:
        logger.info("Refreshing expired access token")
        credentials.refresh(Request())
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
    return None

def get_drive_service_db(drive_access_token):
    """Get synchronous Google Drive service with token refresh"""
    credentials = Credentials(
        token=drive_access_token["access_token"],
        refresh_token=drive_access_token["refresh_token"],
        token_uri=drive_access_token["token_uri"],
        client_id=drive_access_token["client_id"],
        client_secret=drive_access_token["client_secret"]
    )
    if credentials.expired and credentials.refresh_token:
        logger.info("Refreshing token before Drive service creation")
        credentials.refresh(Request())
    return build("drive", "v3", credentials=credentials)

# def save_drive_documents(drive_service, folder_id, meeting_id):
#     """Save and process Drive documents, returning LangChain Documents"""
#     if not os.path.exists("temp_docs"):
#         os.makedirs("temp_docs")
#     meeting_dir = f"temp_docs/{meeting_id}"
#     if not os.path.exists(meeting_dir):
#         os.makedirs(meeting_dir)
    
#     documents = []
#     try:
#         logger.info(f"Listing files in folder {folder_id} for meeting {meeting_id}")
#         results = drive_service.files().list(q=f"'{folder_id}' in parents").execute()
#         files = results.get("files", [])
#         logger.info(f"Found {len(files)} files in folder {folder_id}")
#         for file in files:
#             if file["mimeType"] == "application/pdf":
#                 file_path = f"{meeting_dir}/{file['id']}.pdf"
#                 try:
#                     logger.info(f"Downloading PDF {file['id']} for meeting {meeting_id}")
#                     request = drive_service.files().get_media(fileId=file["id"])
#                     with open(file_path, "wb") as fh:
#                         # Correctly download the file content
#                         fh.write(request.execute())  # Write the bytes directly
#                     logger.info(f"Extracting text from {file_path}")
#                     with open(file_path, "rb") as f:
#                         pdf_reader = PyPDF2.PdfReader(f)
#                         text = ""
#                         for page in pdf_reader.pages:
#                             extracted_text = page.extract_text()
#                             if extracted_text:
#                                 text += extracted_text + "\n"
#                         if text:
#                             documents.append(Document(page_content=text, metadata={"file_id": file["id"], "file_path": file_path}))
#                     # Optional: Clean up temp file
#                     # os.remove(file_path)
#                 except Exception as e:
#                     logger.error(f"Failed to process PDF {file['id']} for meeting {meeting_id}: {str(e)}")
#         logger.info(f"Processed {len(documents)} documents for meeting {meeting_id}")
#     except HttpError as e:
#         logger.error(f"Drive API error for folder {folder_id}, meeting {meeting_id}: {str(e)}")
#     except Exception as e:
#         logger.error(f"Unexpected error in save_drive_documents for meeting {meeting_id}: {str(e)}")
#     return documents


from PyPDF2 import PdfReader  # Only needed if keeping PDF fallback

# Assuming logger is imported or defined elsewhere
# logger = logging.getLogger(__name__)

def save_drive_documents(drive_service, folder_id, meeting_id):
    """Save and process Drive documents, returning LangChain Documents with file paths."""
    if not os.path.exists("temp_docs"):
        os.makedirs("temp_docs")
    meeting_dir = f"temp_docs/{meeting_id}"
    if not os.path.exists(meeting_dir):
        os.makedirs(meeting_dir)
    
    documents = []
    try:
        logger.info(f"Listing files in folder {folder_id} for meeting {meeting_id}")
        results = drive_service.files().list(q=f"'{folder_id}' in parents").execute()
        files = results.get("files", [])
        logger.info(f"Found {len(files)} files in folder {folder_id}")
        for file in files:
            # Map MIME types to file extensions (simplified mapping)
            mime_to_ext = {
                "application/pdf": ".pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                "text/html": ".html",
                "text/markdown": ".md",
                "text/plain": ".txt"
            }
            ext = mime_to_ext.get(file["mimeType"], None)
            if not ext:
                logger.warning(f"Unsupported MIME type {file['mimeType']} for file {file['id']}")
                continue

            file_path = f"{meeting_dir}/{file['id']}{ext}"
            try:
                logger.info(f"Downloading {ext[1:]} {file['id']} for meeting {meeting_id}")
                request = drive_service.files().get_media(fileId=file["id"])
                with open(file_path, "wb") as fh:
                    fh.write(request.execute())  # Write the bytes directly
                logger.info(f"Downloaded to {file_path}")
                documents.append(Document(page_content="", metadata={"file_id": file["id"], "file_path": file_path}))
            except Exception as e:
                logger.error(f"Failed to download {ext[1:]} {file['id']} for meeting {meeting_id}: {str(e)}")
        logger.info(f"Processed {len(documents)} documents for meeting {meeting_id}")
    except HttpError as e:
        logger.error(f"Drive API error for folder {folder_id}, meeting {meeting_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in save_drive_documents for meeting {meeting_id}: {str(e)}")
    return documents