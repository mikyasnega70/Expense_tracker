from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
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

async def list_expenses(db:AsyncSession, user:dict, start:date=None, end:date=None, catagory_id:int=None):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    
    query = select(Expense).where(Expense.user_id == user.get('id'))
    
    if start:
        query = query.where(Expense.date >= start)

    if end:
        query = query.where(Expense.date <= end)
    if catagory_id:
        query = query.where(Expense.catagory_id == catagory_id)
    expenses = await db.scalars(query)
    return expenses.all()

async def update_expense(db:AsyncSession, user:dict, expensereq, expense_id:int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    
    expense = await db.scalar(select(Expense).where(Expense.id == expense_id, Expense.user_id == user.get('id')))
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')
    
    expense.amount = expensereq.amount
    expense.description = expensereq.description
    expense.date = expensereq.date
    expense.catagory_id = expensereq.catagory_id
    db.add(expense)
    await db.commit()




