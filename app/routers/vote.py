from typing import Optional, List, Union
from fastapi import (
    APIRouter, Depends, status, HTTPException
)
from sqlalchemy.orm import Session

from .. import models
from ..database import engine, get_db
from ..schemas import Vote
from ..oauth2 import get_current_user

router = APIRouter(
    # prefix='/vote',
    tags=['vote'],
    responses={
        404: {'description': 'Not found'}
    }
)

@router.post('/vote', status_code=status.HTTP_201_CREATED)
async def vote(
    vote: Vote = Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)):

    post_data = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote.post_id} does not exist"
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already voted on post {vote.post_id}"
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        
        message = {
            'message': 'Successfully added vote'
        }
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote does not exist"
            )
        
        vote_query.delete(synchronize_session=False)
        db.commit()

        message = {
            'message': 'Successfully deleted vote'
        }
    
    return message