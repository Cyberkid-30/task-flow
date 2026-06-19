from ..core.database import AsyncSession
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import selectinload
from ..models.task_model import Task, TaskStatus
from ..schemas.task_schema import TaskCreate, TaskUpdate
from ..schemas.user_schema import UserResponse
from fastapi import HTTPException, status
from datetime import datetime


async def create_task(task: TaskCreate, db: AsyncSession, user: UserResponse):
    result = await db.execute(
        select(Task).where(and_(Task.title == task.title, Task.owner_id == user.id))
    )
    existing_task = result.scalar_one_or_none()
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
    await db.commit()
    await db.refresh(new_task)

    result = await db.execute(
        select(Task).options(selectinload(Task.owner)).where(Task.id == new_task.id)
    )
    return result.scalar_one()


async def fetch_my_tasks(
    db: AsyncSession, user: UserResponse, offset: int = 0, limit: int = 10
):
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.owner))
        .where(Task.owner_id == user.id)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    db_tasks = result.scalars().all()
    return db_tasks


async def fetch_task(id: str, db: AsyncSession, user: UserResponse):
    result = await db.execute(
        select(Task).options(selectinload(Task.owner)).where(Task.id == id)
    )
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if db_task.owner_id != user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    return db_task


async def update_task(id: str, task: TaskUpdate, db: AsyncSession, user: UserResponse):
    result = await db.execute(
        select(Task).options(selectinload(Task.owner)).where(Task.id == id)
    )
    db_task = result.scalar_one_or_none()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if db_task.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(id: str, db: AsyncSession, user: UserResponse):
    db_task = await fetch_task(id, db, user)
    await db.delete(db_task)
    await db.commit()


async def delete_completed_or_due_tasks(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(Task).where(
            and_(
                Task.owner_id == user_id,
                or_(
                    Task.status == TaskStatus.done,
                    Task.due_date <= datetime.now().date(),
                ),
            )
        )
    )

    tasks_to_delete = result.scalars().all()

    count = len(tasks_to_delete)
    for task in tasks_to_delete:
        await db.delete(task)

    await db.commit()
    return count
