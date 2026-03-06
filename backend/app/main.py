from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import main_router, websocket_router
from app.database import create_first_superuser
from app.middlewares import LoggingContextMiddleware
from app.openapi_config import set_openapi_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_first_superuser()
    yield
    pass

origins = [
    "http://localhost:80",
    "http://localhost",
    "http://localhost:8000"
]

app = FastAPI(lifespan=lifespan,
              docs_url="/api/docs",
              openapi_url="/api/openapi.json")

app.add_middleware(LoggingContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
app.include_router(websocket_router)

set_openapi_config(app)

app.mount("/static", StaticFiles(directory="static"), name="static")