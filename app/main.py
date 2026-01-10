from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from api.routes.auth import auth_router
import models  # noqa: F401


app = FastAPI()
Base.metadata.create_all(engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Task-Flow API"}


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
