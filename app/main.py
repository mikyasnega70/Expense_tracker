from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .database import engine
from .models import Base
from .limiter import limiter
from .router import auth, expenses, catagories, reports

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.get('/')
@limiter.limit('1/minute')
async def test(request:Request):
    return {'status':'healthy'}

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(catagories.router)
app.include_router(reports.router)


