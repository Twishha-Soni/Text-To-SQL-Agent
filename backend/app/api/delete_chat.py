from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependecies import get_current_user
from app.database.models import Chats_Agent, Users_Agent
from app.database.session import get_db

router = APIRouter(prefix= "/chat", tags=['delete_chat'])

@router.delete("/{thread_id}")
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

    db.delete(chat)
    db.commit()

    return {'success': 'Chat deleted successfully.'}