from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import DatabaseError
from ...schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from ...api.deps import Current_User_Dependency, DB_Session
from ...services import task_service

task_router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create(request: TaskCreate, db: DB_Session, user: Current_User_Dependency):
    try:
        task = await task_service.create_task(request, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the task",
        )
    return task.to_dict()


@task_router.get("/", response_model=list[TaskResponse])
async def get_my_tasks(
    db: DB_Session, user: Current_User_Dependency, offset: int = 0, limit: int = 10
):
    try:
        tasks = await task_service.fetch_my_tasks(db, user, offset, limit)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching tasks",
        )
    return [task.to_dict() for task in tasks]


@task_router.get("/{id}", response_model=TaskResponse)
async def get_task(id: str, db: DB_Session, user: Current_User_Dependency):
    try:
        task = await task_service.fetch_task(id, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching task",
        )
    return task.to_dict()


@task_router.put("/{id}", response_model=TaskResponse)
async def update(
    id: str, task: TaskUpdate, db: DB_Session, user: Current_User_Dependency
):
    try:
        updated_task = await task_service.update_task(id, task, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating task",
        )
    return updated_task.to_dict()


@task_router.delete("/{id}")
async def delete(id: str, db: DB_Session, user: Current_User_Dependency):
    try:
        await task_service.delete_task(id, db, user)
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting task",
        )

    return {"message": "Task deleted successfully"}
