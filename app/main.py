import logging
from datetime import datetime, timezone

import models  # noqa: F401
from api.routes.auth import auth_router
from api.routes.task import task_router
from core.database import Base, SessionLocal, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from models.task_model import Task
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

Base.metadata.create_all(engine)


def schedule_task_cleanup(app: FastAPI) -> None:
    @repeat_every(seconds=60, wait_first=True)
    def delete_expired_tasks() -> None:
        logger.info("Running scheduled task cleanup...")

        db: Session = SessionLocal()
        try:
            today = datetime.now(timezone.utc).date()

            expired_tasks = db.query(Task).filter(Task.due_date < today).all()

            if not expired_tasks:
                logger.info("No expired tasks found.")
                return

            logger.info("Found %s expired tasks.", len(expired_tasks))

            for task in expired_tasks:
                logger.info("Deleting task %s - %s", task.id, task.title)
                db.delete(task)

            db.commit()
            logger.info("Expired tasks cleanup completed.")

        except Exception:
            db.rollback()
            logger.exception("Task cleanup failed")

        finally:
            db.close()


app = FastAPI(title="Task-Flow API for efficient task management", version="1.0.0")

schedule_task_cleanup(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schedule the task cleanup job

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


# Rather check tasks for their due dates and update their status to done so they get deleted automatically.
