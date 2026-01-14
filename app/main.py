from api.routes.auth import auth_router
from api.routes.task import task_router
from core.database import Base, engine, SessionLocal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.task_service import delete_completed_or_due_tasks
from contextlib import asynccontextmanager
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


Base.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background task
    task = asyncio.create_task(cleanup_tasks_periodically())
    logger.info("Background task cleanup started")
    yield
    # Shutdown: Cancel background task
    logger.info("Shutting down background task cleanup")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Background task cleanup cancelled successfully")


async def cleanup_tasks_periodically():
    """Periodically delete tasks that are done or past due date"""
    while True:
        try:
            db = SessionLocal()
            try:
                deleted_count = delete_completed_or_due_tasks(db)
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} completed or overdue tasks")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in cleanup_tasks_periodically: {e}")

        # Sleep for 1 hour
        await asyncio.sleep(60 * 60)


app = FastAPI(
    title="Task-Flow API for efficient task management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(task_router)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Task-Flow API. An api to help to manage your daily tasks efficiently."
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

