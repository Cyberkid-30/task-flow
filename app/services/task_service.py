from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.task_model import Task, TaskStatus
from schemas.task_schema import TaskCreate, TaskUpdate
from schemas.user_schema import UserResponse
from fastapi import HTTPException, status
from datetime import datetime


def create_task(task: TaskCreate, db: Session, user: UserResponse):
    existing_task = db.query(Task).filter(Task.title == task.title).first()
    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task with this title already exists",
        )

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        owner_id=user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


def fetch_my_tasks(db: Session, user: UserResponse):
    db_tasks = db.query(Task).filter(Task.owner_id == user.id).all()
    return db_tasks


def fetch_task(id: str, db: Session, user: UserResponse):
    db_task = db.query(Task).filter(Task.id == id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if db_task.owner_id != user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    return db_task


def update_task(id: str, task: TaskUpdate, db: Session, user: UserResponse):
    task_query = db.query(Task).filter(Task.id == id)
    db_task = task_query.first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if db_task.owner_id != user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    task_query.update(task.model_dump(), synchronize_session=False)  # type: ignore
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(id: str, db: Session, user: UserResponse):
    db_task = fetch_task(id, db, user)
    db.delete(db_task)
    db.commit()


def delete_completed_or_due_tasks(db: Session):
    """Delete tasks that are marked as done or have passed their due date

    Returns:
        int: Number of tasks deleted
    """
    tasks_to_delete = (
        db.query(Task)
        .filter(
            or_(Task.status == TaskStatus.done, Task.due_date <= datetime.now().date())
        )
        .all()
    )

    count = len(tasks_to_delete)
    for task in tasks_to_delete:
        db.delete(task)

    db.commit()
    return count
