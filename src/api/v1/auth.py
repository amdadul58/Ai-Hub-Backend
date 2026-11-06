from fastapi import APIRouter, HTTPException
from src.schemas.auth import RegisterRequest, LoginRequest, GoogleLoginRequest
from src.services.google_auth_service import GoogleAuthService

google_auth_service = GoogleAuthService()
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


@router.post("/google")
def google_login(payload: GoogleLoginRequest):
    try:
        return google_auth_service.login(payload.id_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

