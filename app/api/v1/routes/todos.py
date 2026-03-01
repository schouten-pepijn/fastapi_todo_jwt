from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.todo import create_todo, delete_todo, get_todo, update_todo
from app.db.database import get_db
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate

router = APIRouter()


@router.get("/", response_model=list[TodoRead])
async def list_todos(db: AsyncSession = Depends(get_db)):
    result = await db.exec(select(Todo))

    return result.all()


@router.post("/", response_model=TodoRead, status_code=201)
async def create_new(todo_in: TodoCreate, db: AsyncSession = Depends(get_db)):
    todo = Todo(**todo_in.model_dump())

    return await create_todo(db, todo)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo_by_id(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo_by_id(
    todo_id: int, todo_in: TodoUpdate, db: AsyncSession = Depends(get_db)
):
    todo = await get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return await update_todo(db, todo, todo_in)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    await delete_todo(db, todo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
