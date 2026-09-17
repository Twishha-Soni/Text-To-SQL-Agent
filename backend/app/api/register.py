from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.hashing import hash_password
from app.db.models import Users_Texttosql_App
from app.db.session import get_db

router = APIRouter(tags=['register'])

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {'from_attributes': True}

@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Users_Texttosql_App).filter(Users_Texttosql_App.username == payload.username).first()

    if existing:
        raise HTTPException(status_code=400, detail='Username already taken.')

    new_user = Users_Texttosql_App(
        username=payload.username,
        hashed_password=hash_password(payload.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user