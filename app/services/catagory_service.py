from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Catagory


async def create_catagory(db:AsyncSession, user:dict, newcatagory):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    catagory_model = Catagory(
        name=newcatagory.name,
        description=newcatagory.description
    )
    db.add(catagory_model)
    await db.commit()

async def list_catagories(db:AsyncSession, user:dict, paginate=None, search:str=None):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    query = select(Catagory)
    if search:
        query = query.where(Catagory.name.ilike(f"%{search}%")).limit(paginate.limit).offset(paginate.offset)
    
    catagories = await db.scalars(query)
    catagories = catagories.all()
    return catagories 

async def update_catagory(db:AsyncSession, user:dict, update, catagory_id:int):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    catagory = await db.scalar(select(Catagory).where(Catagory.id == catagory_id))
    if not catagory:
        raise HTTPException(status_code=404, detail='Catagory not found')
    
    catagory.name = update.name
    catagory.description = update.description
    db.add(catagory)
    await db.commit()



