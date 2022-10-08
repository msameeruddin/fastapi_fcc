from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

username = settings.database_username
password = settings.database_password
hostname = settings.database_hostname
port = settings.database_port
database_name = settings.database_name

# URL format - 'postgresql://<username>:<password>@<ip-address/hostname>:<port>/<database_name>'
SQLALCHEMY_DATABASE_URL = f'postgresql://{username}:{password}@{hostname}:{port}/{database_name}'

engine = create_engine(url=SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# create a dependency
# getting a session towards our database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()