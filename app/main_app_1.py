import psycopg2
import time

from psycopg2.extras import RealDictCursor
from typing import Optional
from fastapi import (
    FastAPI, Depends, Response, status, HTTPException
)
from pydantic import BaseModel

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='fastapi_db',
            user='postgres',
            password='postgres',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print('Database connection was successful!')
        
        break
    except Exception as e:
        print('Database connection failed!')
        print(str(e))

        time.sleep(2)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[float] = None

@app.get('/')
async def root():
    return {
        'message': "Hello World"
    }

@app.get('/fetch')
async def get_posts(id: Optional[int] = None):
    if not id:
        query = '''SELECT * FROM posts'''
        cursor.execute(query=query)
        posts_data = cursor.fetchall()

        return {
            'data': posts_data
        }
    
    try:
        id = str(id)
        query = '''SELECT * FROM posts WHERE id = %s'''
        cursor.execute(query=query, vars=(id))
        posts_data = cursor.fetchone()
        
        return {
            'data': posts_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id: {id} was not found'
        )

@app.post('/add', status_code=status.HTTP_201_CREATED)
async def create_post(cp: Post = Depends()):    
    query = '''INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *'''
    
    cursor.execute(query=query, vars=(cp.title, cp.content, cp.published))
    new_post = cursor.fetchone()
    conn.commit()

    return {
        'data': new_post
    }

@app.put('/update')
async def update_post(id: int, up: Post = Depends()):
    id = str(id)
    query = '''UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *'''
    
    cursor.execute(query=query, vars=(up.title, up.content, up.published, id))
    updated_post = cursor.fetchone()
    conn.commit()

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id: {id} was not found'
        )

    return {
        'data': updated_post
    }

@app.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    try:
        id = str(id)
        query = '''DELETE FROM posts WHERE id = %s RETURNING *'''
        
        cursor.execute(query=query, vars=(id))
        deleted_post = cursor.fetchone()
        conn.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id: {id} was not found'
        )