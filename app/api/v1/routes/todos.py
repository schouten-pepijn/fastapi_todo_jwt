from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from app.crud.todo import create_todo, delete_todo, get_todo, update_todo
from app.db.database import get_session
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
from app.api.deps.authentication import get_current_user

router = APIRouter()


def _require_user_id(user: User) -> int:
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID was not generated",
        )
    return user.id


@router.get("/", response_model=List[TodoRead])
async def list_todos(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_id = _require_user_id(current_user)
    result = await session.exec(select(Todo).where(Todo.owner_id == user_id))

    return result.all()


@router.post("/", response_model=TodoRead, status_code=201)
async def create_new(
    todo_in: TodoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_id = _require_user_id(current_user)
    todo = Todo(**todo_in.model_dump(), owner_id=user_id)

    return await create_todo(session, todo)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo_by_id(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_id = _require_user_id(current_user)
    todo = await get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this todo"
        )

    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo_by_id(
    todo_id: int,
    todo_in: TodoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_id = _require_user_id(current_user)
    todo = await get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this todo"
        )

    return await update_todo(session, todo, todo_in)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_id = _require_user_id(current_user)
    todo = await get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this todo"
        )

    await delete_todo(session, todo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
