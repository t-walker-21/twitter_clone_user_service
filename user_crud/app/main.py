# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from db.db_connection import get_session
from db.models import User, Follower
from datetime import datetime
import jwt

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    
    if token is None:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_info = jwt.decode(jwt=token, key="secret", algorithms=["HS256",])
    return user_info  # In a real application, you would return a user object

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
def get_users(session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

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
def get_users(user_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    statement = select(User).where(User.id == user_id)
    results = session.exec(statement)
    user = results.one()
    session.delete(user)
    session.commit()
        
    return {'success': True}

@app.post("/login/")
def login(email_address: str, password:str, session: Session = Depends(get_session)):

    statement = select(User).where(User.email == email_address).where(User.password == password)

    try:
        user = session.exec(statement).one()

    except:
        raise HTTPException(status_code=403, detail="Invalid Credentials. Please try again")

    # Create JWT Token 
    payload_data = {'sub': str(user.id), 'username': user.username}
    token = jwt.encode(payload=payload_data, key='secret')

    return {'jwt_token': token}

@app.post("/follows/", status_code=201)
def follow_user(followee_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    if str(followee_id) == current_user['sub']:
        raise HTTPException(status_code=400, detail="User cannot follow itself")

    existing_user = session.query(User).filter((User.id == followee_id)).first()

    if not existing_user:
        raise HTTPException(status_code=400, detail="User doesn't exist")
    
    existing_follow = session.query(Follower).filter((Follower.followee_id == followee_id) & (Follower.follower_id == current_user['sub'])).first()
    if existing_follow:
        raise HTTPException(status_code=400, detail=f"User {current_user['sub']} is already following {followee_id}")


    link = Follower(follower_id=current_user['sub'], followee_id=followee_id)

    session.add(link)
    session.commit()
    session.refresh(link)

    return {'success': True}

@app.get("/followers/{user_id}")
def get_followers(user_id:int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    statement = select(Follower).where(Follower.followee_id == user_id)
    results = session.exec(statement)
    response = []
    for result in results:
        response.append({'id': result.id,
                         'follower_id': result.follower_id,
                         'followee_id': result.followee_id})
        
    return {'users': response}