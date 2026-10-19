# AI Hub Backend

FastAPI backend for AI services and workflows.

## Features
- REST API and OpenAPI documentation
- PostgreSQL database
- Authentication and conversation history
- RAG document search
- Machine learning and deep learning APIs
- Vision, speech, translation and multimodal AI
- Agent workflows, automation approvals and MLOps

## Setup (Windows PowerShell)

Install dependencies:

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Run tests:

    .\.venv\Scripts\python.exe -m pytest -q

Start the API:

    .\.venv\Scripts\python.exe -m uvicorn main:app --reload

Open API documentation at http://127.0.0.1:8000/docs

## Local models
The local LLM remains unloaded until a compatible model is configured.
Large models are not downloaded automatically.

## Security
Keep .env private. Configure strong secrets and secure database credentials before deployment.
