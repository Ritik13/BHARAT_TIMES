from fastapi import FastAPI
from routers import posts, auth
from contextlib import asynccontextmanager
from database import engine
from models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
        # shutdown — add cleanup here if needed


app = FastAPI(lifespan=lifespan)

app.include_router(posts.router)
app.include_router(auth.router)
