from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import main_router
from app.database import create_first_superuser
from app.middlewares import LoggingContextMiddleware
from app.openapi_config import set_openapi_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_first_superuser()
    yield
    pass

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
app.add_middleware(LoggingContextMiddleware)

set_openapi_config(app)