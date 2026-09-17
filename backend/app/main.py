from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import ask, login, register

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title='Text-To-SQL Agent',
    lifespan=lifespan
)


app.include_router(login.router)
app.include_router(register.router)
app.include_router(ask.router)