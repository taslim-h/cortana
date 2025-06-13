# backend/app/services/firebase_auth.py
import firebase_admin
from firebase_admin import credentials, auth
from app.config import settings
from fastapi import HTTPException, status
import json
import base64


# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # cred_dict = {
    #     "type": "service_account",
    #     "project_id": settings.FIREBASE_PROJECT_ID,
    #     "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
    #     "client_email": settings.FIREBASE_CLIENT_EMAIL,
    #     "token_uri": "https://oauth2.googleapis.com/token",
    # }
    # cred_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
    decoded_json = base64.b64decode(
        settings.FIREBASE_SERVICE_ACCOUNT_JSON_BASE64).decode()
    cred_dict = json.loads(decoded_json)

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)


async def verify_firebase_token(token: str):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )


async def get_user_info(uid: str):
    """Get user information from Firebase"""
    try:
        user = auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "email_verified": user.email_verified
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {str(e)}"
        )
