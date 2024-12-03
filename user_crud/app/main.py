# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from db.db_connection import get_session
from db.models import User
from datetime import datetime

app = FastAPI()

@app.post("/users/", status_code=201)
def create_user(user: User, session: Session = Depends(get_session)):
    # Check if the username or email already exists
    existing_user = session.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    format_string = "%Y-%m-%d"
    user.date_of_birth = datetime.strptime(user.date_of_birth, format_string)

    session.add(user)
    session.commit()
    session.refresh(user)

    return {'success': True}

@app.get("/users/")
def get_users(session: Session = Depends(get_session)):

    statement = select(User)
    results = session.exec(statement)
    response = []
    for result in results:
        response.append({'id': result.id,
                         'first_name': result.first_name,
                         'last_name': result.last_name,
                         'username': result.username,
                         'date_of_birth': result.date_of_birth,
                         'email': result.email})
        
    return {'users': response}


@app.delete("/users/{user_id}")
def get_users(user_id: int, session: Session = Depends(get_session)):

    statement = select(User).where(User.id == user_id)
    results = session.exec(statement)
    user = results.one()
    session.delete(user)
    session.commit()
        
    return {'success': True}

@app.post("/login/")
def get_users(email_address: str, password:str, session: Session = Depends(get_session)):

    statement = select(User).where(User.email == email_address).where(User.password == password)

    try:
        session.exec(statement).one()

    except:
        raise HTTPException(status_code=403, detail="Invalid Credentials. Please try again")

    # Create JWT Token 

    return {'jwt_token': '12345'}