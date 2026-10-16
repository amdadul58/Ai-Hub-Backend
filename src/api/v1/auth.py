from fastapi import APIRouter, HTTPException
from src.schemas.auth import RegisterRequest, LoginRequest
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


@router.post("/register", status_code=201)
def register(payload: RegisterRequest):
    try:
        return service.register(
            username=payload.username,
            password=payload.password,
            email=payload.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login")
def login(payload: LoginRequest):
    try:
        return service.login(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid username or password.") from exc
