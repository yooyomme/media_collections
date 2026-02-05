from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.loggers import user_for_logs_var


class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_for_logs_var.set("anonym or system")
        response = await call_next(request)
        return response