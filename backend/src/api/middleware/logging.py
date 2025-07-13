import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    """

    @asynccontextmanager
    async def _log_request_context(self, request: Request):
        """Context manager for logging request/response cycle"""
        start_time = time.time()
        # Filter sensitive headers
        headers = {k: v for k, v in request.headers.items() if k.lower() != "authorization"}
        
        logger.info(f"Request: {request.method} {request.url.path} Headers: {headers}")
        
        try:
            yield start_time
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} Error: {exc} Time: {process_time:.4f}s"
            )
            raise

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        async with self._log_request_context(request) as start_time:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url.path} Status: {response.status_code} Time: {process_time:.4f}s"
            )
            return response
