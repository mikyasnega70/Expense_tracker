from fastapi import APIRouter, HTTPException, Depends, Path, Query
from starlette import status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import date
from ..database import Asyncsessionlocal
from .auth import get_current_user
from ..services import expense_service

router = APIRouter(
    prefix='/expenses',
    tags=['expenses']
)

async def get_db():
    async with Asyncsessionlocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class ExpenseCreate(BaseModel):
    amount: float
    description: str
    date: str

class ExpenseUpdate(BaseModel):
    amount:float
    description:str
    date:str
    catagory_id:int

@router.post('/{catagory_id}', status_code=status.HTTP_201_CREATED)
async def create_expense(db:db_dependency, user:user_dependency, newexp:ExpenseCreate, catagory_id:int=Path(gt=0)):
    await expense_service.create_expense(db, user, newexp, catagory_id)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_expenses(db:db_dependency, user:user_dependency, start_date:date=Query(default=None), end_date:date=Query(default=None), catagory_id:int=None):
    expenses = await expense_service.list_expenses(db, user, start_date, end_date, catagory_id)
    return expenses

@router.get('/{expense_id}', status_code=status.HTTP_200_OK)
async def single_response(db:db_dependency, user:user_dependency, expense_id:int=Path(gt=0)):
    expenses = expense_service.list_expenses(db, user)
    expense = next((exp for exp in expenses if exp.id == expense_id), None)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')
    
    return expense

@router.put('/{expense_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_expense(db:db_dependency, user:user_dependency, expensereq:ExpenseUpdate, expense_id:int=Path(gt=0)):
    await expense_service.update_expense(db, user, expensereq, expense_id)

@router.delete('/{expense_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(db:db_dependency, user:user_dependency, expense_id:int=Path(gt=0)):
    expenses = await expense_service.list_expenses(db, user)
    expense = next((exp for exp in expenses if exp.id == expense_id), None)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')
    
    await db.delete(expense)
    await db.commit()


