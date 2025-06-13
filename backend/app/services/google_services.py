# backend/app/services/google_services.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.config import settings
import json

# SCOPES = [
#     'https://www.googleapis.com/auth/drive.readonly',
#     'https://www.googleapis.com/auth/drive.metadata.readonly',
#     'https://www.googleapis.com/auth/calendar.readonly'
# ]

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/tasks.readonly",  # <-- Add this
    "openid"
]


def get_google_auth_flow(redirect_uri: str = None):
    """Create Google OAuth2 flow"""
    # Always use the exact same redirect URI
    if not redirect_uri:
        redirect_uri = "http://localhost:3000/drive-callback.html"

    print(f"Creating auth flow with redirect_uri: {redirect_uri}")

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
    """Get Google Drive service"""
    return build('drive', 'v3', credentials=credentials)


async def get_calendar_service(credentials: Credentials):
    """Get Google Calendar service"""
    return build('calendar', 'v3', credentials=credentials)


async def refresh_google_token(credentials: Credentials) -> dict:
    """Refresh Google access token"""
    if credentials.expired and credentials.refresh_token:
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
