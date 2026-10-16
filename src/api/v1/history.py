from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.v1.users import current_user_id
from src.database.session import database_connection
from src.services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["Conversation History"])
service = HistoryService()


class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=200)


class MessageCreate(BaseModel):
    role: str = Field(default="user", pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=50000)


def owned_conversation(conversation_id, user_id):
    with database_connection() as db:
        row = db.execute(
            "SELECT id FROM conversations WHERE id = %s AND user_id = %s",
            (int(conversation_id), int(user_id)),
        ).fetchone()
    return row is not None


@router.post("/conversations", status_code=201)
def create_conversation(
    payload: ConversationCreate,
    user_id: str = Depends(current_user_id),
):
    try:
        return service.create_conversation(payload.title, int(user_id))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not create conversation.") from exc


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    user_id: str = Depends(current_user_id),
):
    if not owned_conversation(conversation_id, user_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return service.get_messages(conversation_id)


@router.post("/conversations/{conversation_id}/messages", status_code=201)
def add_message(
    conversation_id: int,
    payload: MessageCreate,
    user_id: str = Depends(current_user_id),
):
    if not owned_conversation(conversation_id, user_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")

    try:
        return service.add_message(conversation_id, payload.role, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
