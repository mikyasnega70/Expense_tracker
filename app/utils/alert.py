from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import Budget, Expense

async def send_alert(db:AsyncSession, user:dict, catagory_id:int):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    query =(Expense.user_id == user['id'], Expense.catagory_id == catagory_id)
    total_spent = await db.scalar(select(func.sum(Expense.amount)).where(*query)) or 0
    budget = await db.scalar(select(Budget).where(Budget.user_id == user['id'], Budget.catagory_id == catagory_id))

    if budget and total_spent > budget.limit:
        return {'warning':'budget exceeded'}
    return None

