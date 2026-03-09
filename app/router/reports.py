from fastapi import APIRouter, Request, Depends, Query
from starlette import status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..database import Asyncsessionlocal
from .auth import get_current_user
from ..services import report_service
from ..utils import csv_export
from ..limiter import limiter

router = APIRouter(
    prefix='/reports',
    tags=['reports']
)

async def get_db():
    async with Asyncsessionlocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class BudgetCreate(BaseModel):
    limit:int
    catagory_id:int

@router.get('/monthly/', status_code=status.HTTP_200_OK)
@limiter.limit('30/minute')
async def monthly_report(db:db_dependency, request:Request, user:user_dependency, month:int=Query(ge=1, le=12), year:int=Query(ge=2000)):
    report = await report_service.monthly_report(db, user, month, year)
    return {
        'month':f"{year}-{month:02}",
        'total-spent':report['total'],
        'by_catagory':report['by_catagory']
    }

@router.get('/export', status_code=status.HTTP_200_OK)
@limiter.limit('20/minute')
async def export_csv(db:db_dependency, user:user_dependency, request:Request):
    return await csv_export.export_csv(db, user)

@router.post('/budget', status_code=status.HTTP_201_CREATED)
@limiter.limit('20/minute')
async def set_budget(db:db_dependency, user:user_dependency, request:Request, newbgt:BudgetCreate):
    await report_service.set_budget(db, user, newbgt)


