from typing import Callable

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authentication and authorization
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # TODO: authentication logic can be centralized here.
        # - Extract and validate API keys/tokens
        # - Check user permissions
        # - Handle authentication errors

        # TODO: Validate API key or JWT token

        # TODO: Add user context to request state if needed
        # request.state.user = user

        response = await call_next(request)

        return response
