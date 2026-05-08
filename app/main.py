from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio

from app.routers import chat
from app.core.database import engine, Base
import app.models.message

# Ensure DB tables are created
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the Redis listener background task
    task = asyncio.create_task(chat.manager._redis_listener())
    yield
    # Shutdown
    task.cancel()


app = FastAPI(title="RealChat", lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


app.include_router(chat.router)
