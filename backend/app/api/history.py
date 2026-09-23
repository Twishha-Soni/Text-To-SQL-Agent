from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.models import Chats_Agent, Users_Agent
from app.database.session import get_db
from app.auth.dependecies import get_current_user

router = APIRouter(tags=['history'])

@router.get("/history")
def get_history(current_user: Users_Agent = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = (
        db.query(Chats_Agent)
        .filter(Chats_Agent.user_id == current_user.id)
        .order_by(Chats_Agent.created_at.desc())
        .all()
    )

    chats = [
        {
            'id': c.id,
            'user_id': c.user_id,
            'name': c.name,
            'content': c.content,
            'created_at': c.created_at,
            'last_updatd_at': c.last_updated_at
        }
        for c in chats
    ]

    return chats