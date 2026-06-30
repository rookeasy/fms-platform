# FMS Platform

Repository foundation and frontend application shell for the FMS Platform.

This repository currently includes FMS-0007 Phase 1 through Phase 5 only. Frontend/backend integration is intentionally out of scope.

## Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL
- Local infrastructure: Docker Compose

## Project Structure

```text
frontend/        Next.js application shell
backend/         FastAPI application and database migration setup
infrastructure/  Local development services
docs/            Project documentation
```

## Prerequisites

- Node.js 20+
- Python 3.12+
- Docker Desktop

## Setup

Copy environment files:

```powershell
Copy-Item frontend\.env.example frontend\.env.local
Copy-Item backend\.env.example backend\.env
Copy-Item infrastructure\.env.example infrastructure\.env
```

Start PostgreSQL:

```powershell
docker compose --env-file infrastructure\.env -f infrastructure\docker-compose.yml up -d
```

Install and run the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed_reference_data
uvicorn app.main:app --reload
```

Install and run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Local URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend health check: http://localhost:8000/health
- Backend API v1 placeholder routes: http://localhost:8000/api/v1/buildings
- API docs: http://localhost:8000/docs

## Testing

Backend:

```powershell
cd backend
pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run typecheck
```

## Current Scope

- Phase 1: repository foundation
- Phase 2: frontend application shell using mock data only
- Phase 3: backend application shell using placeholder API route groups
- Phase 4: MVP database models, Alembic migration, and reference-data seed script
- Phase 5: core domain services and CRUD APIs for organizations, users, roles, buildings, and building contacts

No business modules or backend-connected frontend workflows have been built yet.
