from typing import Any, Callable, Dict

from fastapi.responses import JSONResponse


class ExceptionMiddleware:
    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(
        self, scope: Dict[str, Any], receive: Callable, send: Callable
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        try:
            response = await self.app(scope, receive, send)
            return response
        except Exception as exc:
            # Log the error here if needed
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "error": str(exc)},
            )
            await response(scope, receive, send)
