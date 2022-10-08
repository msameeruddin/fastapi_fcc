from typing import Optional, List, Union
from fastapi import (
    APIRouter, Depends, status, HTTPException
)
from sqlalchemy.orm import Session

from .. import models
from ..database import engine, get_db
from ..schemas import (
    UserCreate, UserResponse
)
from ..utils import hash_passwd

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={
        404: {'description': 'Not found'}
    }
)

@router.get('/fetch', response_model=Union[List[UserResponse], UserResponse])
async def get_users(id: Optional[int] = None, db: Session = Depends(get_db)):
    if not id:
        users_data = db.query(models.User).all()
    else:
        users_data = db.query(models.User).filter(models.User.id == id).first()
    
    if not users_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id: {id} was not found'
        )
    
    return users_data

@router.post('/add', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(cu: UserCreate = Depends(), db: Session = Depends(get_db)):
    try:
        # hash the password - cu.password
        h_passwd = hash_passwd(secret=cu.password)
        cu.password = h_passwd

        new_user = models.User(**cu.dict())

        db.add(instance=new_user)
        db.commit()
        db.refresh(instance=new_user)

        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Requires unique email address'
        )

# @router.put('/update')
# async def update_user():
#     return {}

# @router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user():
#     return Response(status_code=status.HTTP_204_NO_CONTENT)