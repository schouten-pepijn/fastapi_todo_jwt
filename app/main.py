from fastapi import FastAPI

from app.api.v1.routes import authentication, todos
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(
    authentication.router,
    prefix="/api/v1",
)

app.include_router(
    todos.router,
    prefix="/api/v1/todos",
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
