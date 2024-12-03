import os
from sqlmodel import SQLModel, create_engine, Session
from .models import User

SQL_URL_STRING = os.environ.get("SQL_URL_STRING", "sqlite:///./test.db")
engine = create_engine(SQL_URL_STRING)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session