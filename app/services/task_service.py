from sqlalchemy.orm import Session
from models.task_model import Task
from schemas.task_schema import TaskCreate, TaskUpdate
from schemas.user_schema import UserResponse
from fastapi import HTTPException, status


def create_task(task: TaskCreate, db: Session, user: UserResponse):
    existing_task = db.query(Task).filter(Task.title == task.title).first()
    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task with this title already exists",
        )

    new_task = Task(title=task.title, description=task.description, owner_id=user.id)
    db.add(new_task)
    db.commit()

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
    db_task = db.query(Task).filter(Task.id == id)
    if not db_task.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if db_task.first().owner_id != user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    db_task.update(
        {
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
        }
    )
    db.commit()
    db.refresh(db_task.first())


def delete_task(id: str, db: Session, user: UserResponse):
    db_task = fetch_task(id, db, user)
    db.delete(db_task)
    db.commit()
