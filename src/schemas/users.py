from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    email: str | None = Field(default=None, min_length=3, max_length=254)
    is_active: bool | None = None
