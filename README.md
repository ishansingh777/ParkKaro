# ParkKaro

"Find. Check. Park."

ParkKaro is an India-focused AI-powered parking intelligence platform.

## Architecture

This is a monorepo containing:
- `apps/`: Next.js applications (`web`, `admin`, `operator`)
- `services/`: Python FastAPI backend modular monolith
- `packages/`: Shared packages and UI components
- `ai/`: AI pipelines for parking rule extraction and recommendations
- `database/`: Database migrations and seeds

## Prerequisites

- **Node.js**: >= 20.0.0
- **pnpm**: >= 9.0.0
- **Python**: 3.11+
- **Docker & Docker Compose**: For PostgreSQL + PostGIS

## Environment Setup

1. Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
2. Install frontend dependencies:
   ```bash
   pnpm install
   ```
3. Setup Python virtual environment for the backend:
   ```bash
   cd services/api
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## Starting the Application

### 1. Database (PostgreSQL + PostGIS)
From the root directory, start the database using Docker:
```bash
docker-compose up -d db
```

### 2. Database Migrations
With the database running, apply Alembic migrations:
```bash
cd services/api
alembic upgrade head
```

### 3. FastAPI Backend
Start the FastAPI application:
```bash
cd services/api
uvicorn app.main:app --reload
```
The API health check will be available at: `http://localhost:8000/api/v1/health`

Alternatively, you can run the backend via Docker:
```bash
docker-compose up -d api
```

### 4. Next.js Frontend
Start the Next.js apps from the root directory:
```bash
pnpm dev
```
