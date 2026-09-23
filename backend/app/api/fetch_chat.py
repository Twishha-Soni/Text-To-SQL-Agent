from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.auth.dependecies import get_current_user
from app.database.models import Chats_Agent, Users_Agent
from app.database.session import get_db

router = APIRouter(prefix= "/fetch_chat", tags=['fetch_chat'])

class ChatSchema(BaseModel):
    id: int
    user_id: int
    name: str
    content: dict[str, Any]
    created_at: datetime
    last_updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/{thread_id}")
def ask_agent(
    thread_id: int,
    current_user: Users_Agent = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = db.query(Chats_Agent).filter(
        thread_id == Chats_Agent.id,
        Chats_Agent.user_id == current_user.id
    ).first()

    if chat is None:
        return HTTPException(
            status_code=404,
            detail="Chat not found."
        )

    detail = ChatSchema.model_validate(chat)

    return chat