from sqlmodel import SQLModel, Field
from datetime import date

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)  # Primary key
    username: str = Field(index=True, unique=True)   # Unique username
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)      # Unique email
    date_of_birth: date
    password: str

class Follower(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)  # Primary key
    follower_id: int = Field(foreign_key="user.id")  # References User
    followee_id: int = Field(foreign_key="user.id")   # References User