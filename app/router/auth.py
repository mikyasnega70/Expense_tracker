from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from ..models import Users
from ..database import Asyncsessionlocal
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db():
    async with Asyncsessionlocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

class UserCreate(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db:db_dependency, token:Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email:EmailStr = payload.get('sub')
        user_id:int = payload.get('id')
        if user_email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        
        result = await db.scalars(select(Users).where(Users.email == user_email, Users.id == user_id))
        user = result.first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        
        return {'email':user.email, 'id':user.id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, newUser:UserCreate):
    result = await db.scalars(select(Users).where(Users.email == newUser.email))
    user = result.first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    
    user_model = Users(
        email=newUser.email,
        hashed_password=pwd_context.hash(newUser.password)
    )
    db.add(user_model)
    await db.commit()

@router.post('/token')
async def login_access(db:db_dependency, form:Annotated[OAuth2PasswordRequestForm, Depends()]):
    result = await db.scalars(select(Users).where(Users.email == form.username))
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password')
    
    if not pwd_context.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password')
    
    token = create_access_token({'sub':user.email, 'id':user.id})
    return {'access_token': token, 'token_type': 'bearer'}
    


