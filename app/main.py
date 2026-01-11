from api.routes.auth import auth_router
from api.routes.task import task_router
from core.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging


Base.metadata.create_all(engine)


app = FastAPI(title="Task-Flow API for efficient task management", version="1.0.0")

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


# Rather check tasks for their due dates and update their status to done so they get deleted automatically.
