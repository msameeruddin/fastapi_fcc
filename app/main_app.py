from fastapi import FastAPI, APIRouter
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import models
from .database import engine

from .routers.posts import router as posts_router
from .routers.users import router as users_router
from .routers.auth import router as auth_router
from .routers.vote import router as vote_router

models.Base.metadata.create_all(bind=engine)

api_router = APIRouter()

api_router.include_router(router=posts_router)
api_router.include_router(router=users_router)
api_router.include_router(router=auth_router)
api_router.include_router(router=vote_router)

tags_metadata = [
    {
        'name': 'authentication',
        'description': 'Login authentication - operations'
    },
    {
        'name': 'posts',
        'description': 'Post details - operations'
    },
    {
        'name': 'users',
        'description': 'User details - operations'
    },
    {
        'name': 'vote',
        'description': 'Voting details - operations'
    }
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(
    title='FastAPI Course - freeCodeCamp',
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        'docExpansion': 'none'
    },
    middleware=middleware
)

app.include_router(router=api_router)

@app.get('/', tags=['home'])
async def root():
    return {
        'message': 'Hello World'
    }