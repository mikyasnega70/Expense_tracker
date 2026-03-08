from fastapi import APIRouter, HTTPException, Request, Depends, Query
from starlette import status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..database import Asyncsessionlocal
from .auth import get_current_user
from ..services import catagory_service
from ..limiter import limiter
from dataclasses import dataclass

router = APIRouter(
    prefix='/catagories',
    tags=['catagories']
)

async def get_db():
    async with Asyncsessionlocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class CatagoryCreate(BaseModel):
    name:str
    description:str

class CatagoryUpdate(BaseModel):
    name:str
    description:str

@dataclass
class Pagination:
    limit:int=10
    offset:int=0

@router.post('/', status_code=status.HTTP_201_CREATED)
@limiter.limit('20/minute')
async def create_catagory(db:db_dependency, user:user_dependency, request:Request, newcatagory:CatagoryCreate):
    await catagory_service.create_catagory(db, user, newcatagory)

@router.get('/', status_code=status.HTTP_200_OK)
@limiter.limit('20/minute')
async def get_catagories(db:db_dependency, user:user_dependency, request:Request, paginate:Pagination=Depends(), search:str=None):
    catagories = await catagory_service.list_catagories(db, user, paginate, search)
    return catagories

@router.put('/{catagory_id}', status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit('20/minute')
async def update_catagory(db:db_dependency, user:user_dependency, request:Request, update:CatagoryUpdate, catagory_id:int):
    await catagory_service.update_catagory(db, user, update, catagory_id)

@router.delete('/{catagory_id}', status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit('20/minute')
async def delete_catagory(db:db_dependency, user:user_dependency, request:Request, catagory_id:int):
    catagories = await catagory_service.list_catagories(db, user)
    catagory = next((ctg for ctg in catagories if ctg.id == catagory_id), None)
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Catagory not found')
    
    await db.delete(catagory)
    await db.commit()

