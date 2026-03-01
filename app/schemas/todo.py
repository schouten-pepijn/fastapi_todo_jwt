from pydantic import BaseModel, ConfigDict


class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
