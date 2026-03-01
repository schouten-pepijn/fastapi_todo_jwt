from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.todo import Todo
from app.schemas.todo import TodoUpdate


async def get_todos(session: AsyncSession, owner_id: int) -> list[Todo]:
    result = await session.exec(select(Todo).where(Todo.owner_id == owner_id))
    return list(result.all())


async def get_todo(session: AsyncSession, todo_id: int, owner_id: int) -> Todo | None:
    result = await session.exec(
        select(Todo).where(Todo.id == todo_id, Todo.owner_id == owner_id)
    )
    return result.one_or_none()


async def create_todo(session: AsyncSession, todo: Todo) -> Todo:
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


async def update_todo(session: AsyncSession, todo: Todo, todo_in: TodoUpdate) -> Todo:
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
