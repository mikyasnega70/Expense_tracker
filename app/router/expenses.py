from fastapi import APIRouter, HTTPException, Depends, Path
from starlette import status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
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

@router.post('/{catagory_id}', status_code=status.HTTP_201_CREATED)
async def create_expense(db:db_dependency, user:user_dependency, newexp:ExpenseCreate, catagory_id:int=Path(gt=0)):
    await expense_service.create_expense(db, user, newexp, catagory_id)


