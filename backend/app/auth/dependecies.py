from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.db.models import Users_Texttosql_App
from app.db.session import get_db

CREDENTIALS_ERROR = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/login')

def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> Users_Texttosql_App:
    payload = decode_access_token(token)
    if payload is None:
        raise CREDENTIALS_ERROR

    user_id = payload.get('sub')
    if user_id is None:
        raise CREDENTIALS_ERROR

    user = db.query(Users_Texttosql_App).filter(Users_Texttosql_App.id == int(user_id)).first()
    if user is None:
        return CREDENTIALS_ERROR

    return user