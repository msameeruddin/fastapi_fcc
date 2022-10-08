from fastapi import (
    APIRouter, Depends, status, HTTPException
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models
from ..database import engine, get_db
from ..schemas import Token
from ..utils import verify_password
from ..oauth2 import create_access_token

router = APIRouter(
    # prefix='/auth',
    tags=['authentication'],
    responses={
        404: {'description': 'Not found'}
    }
)

@router.post('/login', response_model=Token)
async def login(user_login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_details = db.query(models.User).filter(models.User.email == user_login.username).first()

    if not user_details:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid credentials'
        )
    
    if not verify_password(plain_passwd=user_login.password, hashed_passwd=user_details.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Incorrect password'
        )
    
    # create token
    # return token
    access_token = create_access_token(data={'user_id': user_details.id})
    
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }