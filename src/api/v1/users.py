from fastapi import APIRouter, Depends, Header, HTTPException

from src.core.security import verify_access_token
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
service = UserService()


def current_user_id(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = verify_access_token(token)

    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(payload["sub"])
    user = service.repository.get(user_id)

    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=401,
            detail="User account is inactive or no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


@router.get("/me")
def get_me(user_id: str = Depends(current_user_id)):
    user = service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User account no longer exists.")

    user.pop("password_hash", None)
    return user
