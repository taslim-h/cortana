from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.mongodb import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app():
    app = FastAPI(title="Meeting Assistant API",
                  version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import routers AFTER app & middleware initialized
    from app.routes import auth, meetings, google_drive, google_calendar

    app.include_router(auth.router, prefix="/api/auth",
                       tags=["Authentication"])
    app.include_router(
        meetings.router, prefix="/api/meetings", tags=["Meetings"])
    app.include_router(google_drive.router,
                       prefix="/api/drive", tags=["Google Drive"])
    app.include_router(google_calendar.router,
                       prefix="/api/calendar", tags=["Google Calendar"])

    @app.get("/")
    async def root():
        return {"message": "Meeting Assistant API is running"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app
