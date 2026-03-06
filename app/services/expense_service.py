from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Expense, Users, Catagory

async def create_expense(db:AsyncSession, user, newexp, catagory_id):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    result = await db.scalars(select(Catagory).where(Catagory.id == catagory_id))
    catagory = result.first()
    if not catagory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Catagory not found')
    
    exp_model = Expense(
        amount=newexp.amount,
        description=newexp.description,
        date=newexp.date,
        user_id=user['id'],
        catagory_id=catagory_id
    )
    db.add(exp_model)
    await db.commit()


