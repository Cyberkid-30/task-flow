import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api.routes.auth import auth_router
from .api.routes.task import task_router
from .core.config import settings
from .core.database import AsyncSessionLocal, init_db
from .services.task_service import delete_completed_or_due_tasks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration on startup
try:
    settings.validate_config()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise


# Track background task across lifespan
_cleanup_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    await init_db()
    logger.info("Database initialized successfully")

    # Startup: Start background task only if this is the primary instance
    global _cleanup_task
    is_render = os.getenv("RENDER") == "true"
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    is_heroku = os.getenv("DYNO") is not None

    # Only run background task on single-instance or primary instances
    should_run_cleanup = (
        not (is_render or is_railway or is_heroku)
        or os.getenv("RUN_BACKGROUND_TASKS", "true") == "true"
    )

    if should_run_cleanup:
        _cleanup_task = asyncio.create_task(cleanup_tasks_periodically())
        logger.info("Background task cleanup started")
    else:
        logger.info(
            "Background task cleanup skipped (not primary dyno or scaled environment)"
        )

    yield

    # Shutdown: Cancel background task
    if _cleanup_task:
        logger.info("Shutting down background task cleanup")
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            logger.info("Background task cleanup cancelled successfully")


async def cleanup_tasks_periodically():
    """Periodically delete tasks that are done or past due date"""
    # Wait a bit before first run to allow app to fully start
    await asyncio.sleep(5)

    while True:
        try:
            async with AsyncSessionLocal() as db:
                deleted_count = await delete_completed_or_due_tasks(db)
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} completed or overdue tasks")
        except Exception as e:
            logger.error(f"Error in cleanup_tasks_periodically: {e}")

        # Sleep for 1 hour
        try:
            await asyncio.sleep(60 * 60)
        except asyncio.CancelledError:
            break


app = FastAPI(
    title="Task-Flow API for efficient task management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS based on environment
allowed_origins = [
    "https://task-flow-frontend-jade.vercel.app",
    "http://localhost:5173",  # Local development
    "http://localhost:8000",  # Local API
    "https://*.vercel.app",  # Vercel deployments
]

# Allow all origins in development, specific origins in production
if settings.ENVIRONMENT == "DEVELOPMENT":
    allowed_origins = ["*"]
else:
    # Add any additional production origins from environment
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


app.include_router(auth_router)
app.include_router(task_router)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Task-Flow API. An api to help to manage your daily tasks efficiently."
    }


# Health check endpoint with database connectivity test
@app.get("/health")
async def health_check():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "database": "disconnected", "error": str(e)}
