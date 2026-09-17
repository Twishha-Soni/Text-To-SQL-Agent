from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token
from app.db.models import Users_Texttosql_App
from app.db.session import get_db

router = APIRouter(tags=['login'])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'

@router.post("/login", response_model=TokenResponse)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(Users_Texttosql_App).filter(Users_Texttosql_App.username == form_data.username).first()

    verified, updated_hash_pass = verify_password(form_data.password, user.hashed_password)

    if not user or not verified:
        raise HTTPException(status_code=401, detail='Invalid username or password')

    if updated_hash_pass:
        user.hashed_password = updated_hash_pass
        db.commit()
        db.refresh(user)

    token = create_access_token(user_id=user.id, username=user.username)
    return TokenResponse(access_token=token)