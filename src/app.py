# app/main.py

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from db.db_connection import get_session
from db.models import Users, Follower
from datetime import datetime
import jwt
import os
from utils.minio import MinioClient
import uuid

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

router = APIRouter(prefix="/users")  # Create router with prefix

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

minio_client = MinioClient().get_client()

def get_current_user(token: str = Depends(oauth2_scheme)):
    if token is None:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        user_info = jwt.decode(jwt=token, key=os.environ["JWT_SECRET"], algorithms=["HS256",])
        return user_info  # In a real application, you would return a user object
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")

@router.post("/users/", status_code=201)
def create_user(user: Users, session: Session = Depends(get_session)):
    # Check if the username or email already exists
    existing_user = session.query(Users).filter((Users.username == user.username) | (Users.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    format_string = "%Y-%m-%d"
    user.date_of_birth = datetime.strptime(user.date_of_birth, format_string)

    session.add(user)
    session.commit()
    session.refresh(user)

    return {'success': True}

@router.get("/users/")
def get_users(session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    statement = select(Users)
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


@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):
        
    try:
        statement = select(Users).where(Users.id == user_id)
        result = session.exec(statement).one()
        
        response = {'id': result.id,
                    'first_name': result.first_name,
                    'last_name': result.last_name,
                    'username': result.username,
                    'date_of_birth': result.date_of_birth,
                    'email': result.email,
                    'profile_picture_url': result.profile_picture_url,
                    'bio': result.bio}
        
        return {'user': response}
    
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    statement = select(Users).where(Users.id == user_id)
    results = session.exec(statement)
    user = results.one()
    session.delete(user)
    session.commit()
        
    return {'success': True}

@router.post("/login/")
def login(email_address: str, password:str, session: Session = Depends(get_session)):

    statement = select(Users)

    results = session.exec(statement)

    print (results.all())

    statement = select(Users).where(Users.email == email_address).where(Users.password == password)

    try:
        user = session.exec(statement).one()
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid Credentials. Please try again")

    # Create JWT Token 
    payload_data = {'sub': str(user.id), 'username': user.username}
    token = jwt.encode(payload=payload_data, key=os.environ["JWT_SECRET"], algorithm="HS256")

    return {'jwt_token': token}

@router.post("/follows/{followee_id}", status_code=201)
def follow_user(followee_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    if str(followee_id) == current_user['sub']:
        raise HTTPException(status_code=400, detail="User cannot follow itself")

    existing_user = session.query(Users).filter((Users.id == followee_id)).first()

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

@router.get("/followers/{user_id}")
def get_followers(user_id:int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    statement = select(Follower).where(Follower.followee_id == user_id)
    results = session.exec(statement)
    response = []
    for result in results:
        response.append({'id': result.id,
                         'follower_id': result.follower_id,
                         'followee_id': result.followee_id})
        
    return {'users': response}

@router.get("/following/{user_id}")
def get_following(user_id:int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    statement = select(Follower).where(Follower.follower_id == user_id)
    results = session.exec(statement)
    response = []
    for result in results:
        response.append({'id': result.id,
                         'follower_id': result.follower_id,
                         'followee_id': result.followee_id})
        
    return {'users': response}


@router.get("/get_presigned_url/{image_name}")
def get_presigned_url(image_name: str, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):

    if image_name is None or not image_name.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid image name. Must end with .png, .jpg, or .jpeg")
    
    extension = '.' + image_name.split('.')[-1]
    blob_name = uuid.uuid4().hex + extension
    
    try:
        presigned_url = minio_client.presigned_put_object("user-images", blob_name)
        return {'presigned_url': presigned_url, 'blob_name': blob_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/profile_picture/{picture_url}", status_code=201)
def add_profile_picture(picture_url: str, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):
    if not picture_url:
        raise HTTPException(status_code=400, detail="Picture URL cannot be empty")
    
    # Update the user's profile picture URL
    user = session.query(Users).filter(Users.id == current_user['sub']).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_picture_url = picture_url
    session.commit()

    print (f"Updated profile picture for user {user.id}: {picture_url}")

    return {'success': True, 'profile_picture_url': picture_url}

# Include the router in the main app
app.include_router(router)