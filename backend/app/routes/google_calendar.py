# backend/app/routes/google_calendar.py
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import UserInDB
from app.routes.auth import get_current_user
from app.services.mongodb import get_users_collection
from app.services.google_services import (
    get_google_auth_flow,
    get_credentials_from_token,
    get_calendar_service,
    refresh_google_token
)
from datetime import datetime, timedelta, timezone
import pytz

router = APIRouter()


class CalendarCallbackRequest(BaseModel):
    code: str
    redirect_uri: str


@router.post("/authorize")
async def authorize_calendar(
    current_user: UserInDB = Depends(get_current_user),
    redirect_uri: str = Query(default=None)
):
    """Get Google Calendar authorization URL"""
    # Force the redirect URI to be consistent
    redirect_uri = redirect_uri or "http://localhost:3000/calendar-callback.html"
    print(f"Calendar authorize - Using redirect_uri: {redirect_uri}")

    flow = get_google_auth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account consent',  # Force account selection
        state=current_user.firebase_uid
    )
    return {"auth_url": auth_url}


@router.post("/callback")
async def calendar_callback(
    request: CalendarCallbackRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Handle Google Calendar OAuth callback"""
    try:
        print(
            f"Calendar callback - Code: {request.code[:20]}..., Redirect URI: {request.redirect_uri}")

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

        # Save tokens to user profile
        users_collection = get_users_collection()
        await users_collection.update_one(
            {"firebase_uid": current_user.firebase_uid},
            {
                "$set": {
                    "google_tokens": token_dict,
                    "calendar_integrated": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        return {"message": "Calendar integration successful"}
    except Exception as e:
        print(f"Calendar callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to integrate calendar: {str(e)}"
        )


@router.get("/events")
async def get_calendar_events(
    current_user: UserInDB = Depends(get_current_user),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get calendar events for the next N days"""
    users_collection = get_users_collection()
    user = await users_collection.find_one({"firebase_uid": current_user.firebase_uid})

    if not user.get("google_tokens"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar not integrated"
        )

    try:
        credentials = get_credentials_from_token(user["google_tokens"])

        # Refresh token if expired
        if credentials.expired:
            new_tokens = await refresh_google_token(credentials)
            if new_tokens:
                await users_collection.update_one(
                    {"firebase_uid": current_user.firebase_uid},
                    {"$set": {"google_tokens": new_tokens}}
                )

        service = await get_calendar_service(credentials)

        # Get events
        now = datetime.now(timezone.utc).isoformat()
        end_time = (datetime.now(timezone.utc) +
                    timedelta(days=days)).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_time,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Format events
        formatted_events = []
        for event in events:
            formatted_event = {
                "id": event['id'],
                "title": event.get('summary', 'No title'),
                "description": event.get('description', ''),
                "location": event.get('location', ''),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "all_day": 'date' in event['start'],
                "status": event.get('status', 'confirmed'),
                "html_link": event.get('htmlLink', '')
            }
            formatted_events.append(formatted_event)

        return {
            "events": formatted_events,
            "count": len(formatted_events)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve calendar events: {str(e)}"
        )


@router.get("/tasks")
async def get_calendar_tasks(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get tasks from Google Tasks API"""
    users_collection = get_users_collection()
    user = await users_collection.find_one({"firebase_uid": current_user.firebase_uid})

    if not user.get("google_tokens"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar not integrated"
        )

    try:
        credentials = get_credentials_from_token(user["google_tokens"])
        from googleapiclient.discovery import build
        service = build('tasks', 'v1', credentials=credentials)

        # Get all task lists
        tasklists_result = service.tasklists().list(maxResults=10).execute()
        tasklists = tasklists_result.get('items', [])

        all_tasks = []
        for tasklist in tasklists:
            tasks_result = service.tasks().list(
                tasklist=tasklist['id']).execute()
            tasks = tasks_result.get('items', [])
            for task in tasks:
                all_tasks.append({
                    "id": task.get('id'),
                    "title": task.get('title'),
                    "notes": task.get('notes', ''),
                    "status": task.get('status'),
                    "due": task.get('due'),
                    "completed": task.get('completed'),
                    "tasklist": tasklist.get('title')
                })

        return {
            "tasks": all_tasks,
            "message": f"Fetched {len(all_tasks)} tasks"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.delete("/disconnect")
async def disconnect_calendar(
    current_user: UserInDB = Depends(get_current_user)
):
    """Disconnect Google Calendar integration"""
    users_collection = get_users_collection()

    await users_collection.update_one(
        {"firebase_uid": current_user.firebase_uid},
        {
            "$unset": {"google_tokens": ""},
            "$set": {
                "calendar_integrated": False,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return {"message": "Calendar disconnected successfully"}
