# AI Hub Backend

AI Hub is a FastAPI backend project for an extensible AI platform. The codebase includes API modules for machine learning, deep learning, LLMs, RAG, vision, speech, translation, multimodal processing, traffic intelligence, automation, agents, and MLOps.

## Current project status

This repository contains API routes and supporting modules for multiple AI capabilities. The existence of a route does not guarantee that a real model is installed or inference is fully implemented. Check each module's dependencies, model files, and tests before using it in production.

## Requirements

- Python 3.12 or a compatible Python version
- PowerShell on Windows, or a compatible shell
- Git (optional)
- Docker Desktop (optional, for container deployment)

Install the dependencies declared in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

## Run locally on Windows

Activate the project's virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Set a strong secret for authentication:

```powershell
$env:AI_HUB_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Start the API:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open the interactive API documentation at `http://127.0.0.1:8000/docs`.

Health endpoints:

- `GET /`
- `GET /health`

The API router is mounted under `/api/v1`.

## Environment configuration

`.env.example` documents supported settings. Copy it to `.env` if you need a reference, then replace the example secret with a unique random value.

The application currently reads environment variables through Python code. Do not assume that a `.env` file is automatically loaded; set variables in the shell or configure a dotenv loader explicitly if needed.

Important variables:

- `AI_HUB_SECRET_KEY`: required by the token-signing code; use a random secret of at least 32 characters.
- `AI_HUB_DATABASE_PATH`: optional SQLite database path.
- `AI_HUB_UPLOAD_DIR`: optional upload directory.
- `APP_NAME`, `APP_VERSION`, `HOST`, `PORT`, `DEBUG`: application settings.

Never commit secrets, private uploads, or production database files.

## Run tests

Install the test tools and any dependencies needed by the modules under test. Then run:

```powershell
python -m pytest -q
```

Use temporary database and upload paths in tests. Do not run tests against production data.

## Docker

Build and start the API using Docker Compose:

```powershell
$env:AI_HUB_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up --build
```

The container exposes port 8000. Persistent artifacts, uploads, data, and logs use named Docker volumes.

The Docker image installs only dependencies declared in `requirements.txt`. AI model weights are not downloaded automatically, and optional model-specific packages may need to be installed separately.

## Project layout

- `main.py`: FastAPI application entry point.
- `src/api/v1/`: versioned API routes.
- `src/core/`: application configuration, security, middleware, and logging.
- `src/database/`: SQLite session, schema, models, and repositories.
- `src/machine_learning/`: ML algorithms, preprocessing, training, evaluation, and inference.
- `src/deep_learning/`: deep-learning helpers.
- `src/llm/`: language-model utilities.
- `src/rag/` and `src/vector_db/`: retrieval and vector-search components.
- `src/vision/`, `src/speech/`, `src/translation/`: modality-specific utilities.
- `src/agents/`, `src/automation/`, `src/orchestration/`: agent and workflow components.
- `src/mlops/`: model tracking, monitoring, versioning, and pipeline helpers.
- `config/`: compatibility configuration helpers.
- `tests/`: API, security, unit, and integration tests.

## Production readiness

Before deployment, verify authentication and authorization, input validation, upload limits, CORS origins, database initialization and migrations, logging, model loading, inference quality, resource limits, and automated tests. Do not expose a development server directly to the public internet.
