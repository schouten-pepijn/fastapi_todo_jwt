# To-Do API (FastAPI + SQLModel + PostgreSQL)

## 1. Configure environment

Copy the template and adjust secrets if needed:

```bash
cp .env.template .env
```

The default `DATABASE_URL` is already configured for local PostgreSQL via Docker:

`postgresql+asyncpg://postgres:postgres@localhost:5433/todo_db`

## 2. Start PostgreSQL

```bash
task db-start
```

Optional: watch DB logs

```bash
task db-logs
```

## 3. Install dependencies

```bash
uv sync --dev
```

## 4. Run migrations

```bash
task db-upgrade
```

## 5. Run the API

```bash
task run-uvicorn
```

Health check:

`GET http://127.0.0.1:8000/health`

Swagger:

`http://127.0.0.1:8000/docs`

## 6. Run tests

```bash
task run-pytest
```

## Useful DB commands

- Stop PostgreSQL container: `task db-stop`
- Remove compose resources: `task db-down`
- Show migration history: `task db-history`
- Show current migration: `task db-current`
