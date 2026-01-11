from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import DatabaseError
from schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from api.deps import Current_User_Dependency, DBSession
from services.task_service import (
    create_task,
    fetch_my_tasks,
    fetch_task,
    update_task,
    delete_task,
)

task_router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create(request: TaskCreate, db: DBSession, user: Current_User_Dependency):
    try:
        task = create_task(request, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the task",
        )
    return task


@task_router.get("/", response_model=list[TaskResponse])
def get_my_tasks(db: DBSession, user: Current_User_Dependency):
    try:
        tasks = fetch_my_tasks(db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching tasks",
        )
    return tasks


@task_router.get("/{id}", response_model=TaskResponse)
def get_task(id: str, db: DBSession, user: Current_User_Dependency):
    try:
        task = fetch_task(id, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching task",
        )
    return task


@task_router.put("/{id}", response_model=TaskResponse | dict)
def update(id: str, task: TaskUpdate, db: DBSession, user: Current_User_Dependency):
    try:
        updated_task = update_task(id, task, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating task",
        )
    return updated_task


@task_router.delete("/{id}")
def delete(id: str, db: DBSession, user: Current_User_Dependency):
    try:
        delete_task(id, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting task",
        )

    return {"message": "Task deleted successfully"}
