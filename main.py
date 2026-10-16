from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_router
from src.core.middleware import RequestContextMiddleware

app = FastAPI(
    title="AI Hub",
    description=(
        "Enterprise AI Platform with "
        "Traffic Intelligence, Vision, Speech, Translation "
        "and Multimodal AI"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def home():
    return {
        "app": "AI Hub",
        "status": "running",
        "message": "Welcome to AI Hub Backend",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "AI Hub",
        "version": "1.0.0",
    }
