from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class PublicWidgetCORSMiddleware(BaseHTTPMiddleware):
    """Allow cross-origin access for unauthenticated public widget endpoints."""

    def __init__(self, app, *, public_path_prefix: str) -> None:
        super().__init__(app)
        self._public_path_prefix = public_path_prefix

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not request.url.path.startswith(self._public_path_prefix):
            return await call_next(request)

        if request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Accept",
                    "Access-Control-Max-Age": "86400",
                },
            )

        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response
