from pydantic import BaseModel
from datetime import datetime

class TwitterUserRegistration(BaseModel):

    username: str
    first_name: str
    last_name: str
    email_address: str
    date_of_birth: datetime
    password: str

class TwitterUserLogin(BaseModel):

    email_address: str
    password: str