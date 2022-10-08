from typing import Optional, List, Union
from fastapi import (
    APIRouter, Depends, Response, status, HTTPException
)
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models
from ..database import engine, get_db
from ..schemas import (
    PostCreate, PostUpdate, PostResponse, PostOut
)
from ..oauth2 import get_current_user

router = APIRouter(
    prefix='/posts',
    tags=['posts'],
    responses={
        404: {'description': 'Not found'}
    }
)

@router.get('/fetch', response_model=Union[List[PostOut], PostOut])
async def get_posts(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    limit: int = 10,
    skip: int = 2,
    search: Optional[str] = ''):

    if not id:
        # posts_data = db.query(models.Post)\
        #     .filter(models.Post.title.contains(other=search))\
        #     .limit(limit=limit)\
        #     .offset(offset=skip).all()
        
        posts_data = db.query(models.Post, func.count(models.Vote.post_id).label('votes'))\
            .join(models.Vote, (models.Vote.post_id == models.Post.id), isouter=True)\
            .group_by(models.Post.id)\
            .filter(models.Post.title.contains(other=search))\
            .limit(limit=limit)\
            .offset(offset=skip).all()
        
    else:
        # posts_data = db.query(models.Post).filter(models.Post.id == id).first()
        posts_data = db.query(models.Post, func.count(models.Vote.post_id).label('votes'))\
            .join(models.Vote, (models.Vote.post_id == models.Post.id), isouter=True)\
            .group_by(models.Post.id)\
            .filter(models.Post.id == id).first()
    
    if not posts_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id: {id} was not found'
        )
    
    return posts_data

@router.post('/add', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(
    cp: PostCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)):

    # print(current_user.id)
    new_post = models.Post(owner_id=current_user.id, **cp.dict())
    
    db.add(instance=new_post)
    db.commit()
    db.refresh(instance=new_post)
    
    return new_post

@router.put('/update', response_model=PostResponse)
async def update_post(
    id: int,
    up: PostUpdate = Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_data = post_query.first()

    if not post_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id: {id} was not found'
        )
    
    if (post_data.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to perform requested action'
        )
    
    post_query.update(up.dict(), synchronize_session=False)
    db.commit()
    updated_post = post_query.first()
    
    return updated_post

@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_data = post_query.first()
    
    if not post_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id: {id} was not found'
        )
    
    if (post_data.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to perform requested action'
        )
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)