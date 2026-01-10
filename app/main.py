from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from api.routes.auth import auth_router
from api.routes.task import task_router
from fastapi_utils.tasks import repeat_every
from datetime import datetime
from models.task_model import Task
import models  # noqa: F401


app = FastAPI(title="Task-Flow API for efficient task management", version="1.0.0")
Base.metadata.create_all(engine)


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


def schedule_task_cleanup(app):
    @app.on_event("startup")
    @repeat_every(seconds=86400)  # Run once a day
    def delete_expired_tasks():
        with (
            app.state.db_session() as db
        ):  # Assuming `db_session` is set up in app state
            expired_tasks = (
                db.query(Task).filter(Task.due_date < datetime.now().date()).all()
            )
            for task in expired_tasks:
                db.delete(task)
            db.commit()
