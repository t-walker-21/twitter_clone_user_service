from sqlmodel import SQLModel, Field
from datetime import date

class Users(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)  # Primary key that auto-increments
    username: str = Field(index=True, unique=True)   # Unique username
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)      # Unique email
    date_of_birth: date
    password: str
    profile_picture_url: str = Field(default=None, nullable=True)  # Optional profile picture URL
    bio: str = Field(default=None, nullable=True)  # Optional bio field

class Follower(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)  # Primary key
    follower_id: int = Field(foreign_key="users.id")  # References User
    followee_id: int = Field(foreign_key="users.id")   # References User