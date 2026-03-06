from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine
from .models import Base
from .router import auth, expenses

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def test():
    return {'status':'healthy'}

app.include_router(auth.router)
app.include_router(expenses.router)


