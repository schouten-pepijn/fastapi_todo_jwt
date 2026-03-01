from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.todo import Todo
from app.schemas.todo import TodoUpdate


async def get_todo(session: AsyncSession, todo_id: int) -> Todo | None:
    return await session.get(Todo, todo_id)


async def create_todo(session: AsyncSession, todo: Todo) -> Todo:
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


async def update_todo(
    session: AsyncSession, todo: Todo, todo_in: TodoUpdate
) -> Todo:
    update_data = todo_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


async def delete_todo(session: AsyncSession, todo: Todo) -> None:
    await session.delete(todo)
    await session.commit()
