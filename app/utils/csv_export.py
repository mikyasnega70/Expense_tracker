from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models import Expense
from io import StringIO
import csv

async def export_csv(db:AsyncSession, user:dict):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    query = select(Expense).options(selectinload(Expense.catagory)).where(Expense.user_id == user['id'])
    result = await db.scalars(query)
    expenses = result.all()

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['date', 'amount', 'catagory', 'description'])
    writer.writeheader()

    writer.writerows({'date':exp.date, 'amount':exp.amount, 'catagory':exp.catagory.name, 'description':exp.description} for exp in expenses)
    output.seek(0)

    return StreamingResponse(output, media_type='text/csv', headers={'Content-Disposition':'attachment;filename=expense.csv'},)



