import os
from sqlmodel import SQLModel, create_engine, Session
from .models import Users, Follower

SQL_URL_STRING = os.environ.get("SQL_URL_STRING")
if SQL_URL_STRING is None:
    raise ValueError("SQL_URL_STRING environment variable not set")
else:
    print(f"SQL_URL_STRING: {SQL_URL_STRING}")
engine = create_engine(SQL_URL_STRING)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session