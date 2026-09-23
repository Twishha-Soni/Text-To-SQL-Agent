from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import ask, login, register, history, fetch_chat, delete_chat

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
app.include_router(history.router)
app.include_router(fetch_chat.router)
app.include_router(delete_chat.router)