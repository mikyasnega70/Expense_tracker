from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract
from sqlalchemy.sql import func
from ..models import Expense, Catagory

async def monthly_report(db:AsyncSession, user:dict, month, year):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    query = (Expense.user_id == user['id'], extract('month', Expense.date) == month, extract('year', Expense.date) == year)

    result = await db.execute(select(Catagory.name, func.sum(Expense.amount)).join(Expense.catagory).where(*query).group_by(Catagory.name))
    by_catagory = [{'catagory':r[0], 'total':r[1]} for r in result]
    total = sum(r['total'] for r in by_catagory)

    return {'total':total, 'by_catagory':by_catagory}



