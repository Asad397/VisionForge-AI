# VisionForge AI

VisionForge AI is a production-ready AI creative SaaS platform for generating images and videos using configurable AI providers. It is designed to support a real generation pipeline using FastAPI, Celery, Redis, PostgreSQL, and provider adapters.

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + SQLAlchemy + Pydantic
- Queue: Celery + Redis
- Database: PostgreSQL + Alembic
- Storage: Local or S3-compatible abstraction
- Worker: GPU-ready / CPU-ready architecture

## Features

- Real async generation jobs
- Model registry with capabilities
- Credit validation and reservation
- Mock mode for local development
- Provider adapter architecture
- Character system
- Audio and voice generation
- Admin dashboard
- Library, explore, favorites, reports
- Dockerized local setup

## Quick start

```bash
cp .env.example .env

docker compose up --build
```

Then open the frontend and backend.

## Local development

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Worker:

```bash
cd backend
source .venv/bin/activate
celery -A app.worker worker --loglevel=info
```

## Environment

Copy `.env.example` and set your secrets.

## Production

Use Docker Compose for local orchestration, or configure Nginx + Postgres + Redis + app workers for Kubernetes or a VM deployment.
