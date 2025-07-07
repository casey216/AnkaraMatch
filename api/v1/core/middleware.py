from time import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .logger import logger
from .settings import settings

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time()

        body = await request.body()

        if settings.ENV.lower() == "production":
            logged_body = "[REDACTED]"
        else:
            try:
                logged_body = body.decode("utf-8") or "{}"
            except UnicodeDecodeError:
                logged_body = "[binary date]"

        logger.info(f"Request: {request.method} {request.url} | Body: {logged_body}")

        response: Response = await call_next(request)

        duration = round(time() - start_time, 4)
        logger.info(f"Response: {request.method} {request.url} | Status: {response.status_code} | Duration: {duration}s")

        return response