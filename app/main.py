import contextlib

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount

from .mcp_server import mcp
from .security_middleware import ApiKeyMiddleware


class MCPCompatibilityMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/mcp"):
            headers = list(scope.get("headers", []))
            rewritten_headers = []

            for key, value in headers:
                lower_key = key.lower()

                if lower_key == b"content-type" and value.lower() == b"application/octet-stream":
                    rewritten_headers.append((b"content-type", b"application/json"))
                    continue

                rewritten_headers.append((key, value))

            scope = {**scope, "headers": rewritten_headers}

        await self.app(scope, receive, send)


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with mcp.session_manager.run():
        yield


app = Starlette(
    routes=[
        Mount("/", app=mcp.streamable_http_app()),
    ],
    middleware=[
        Middleware(MCPCompatibilityMiddleware),
        Middleware(ApiKeyMiddleware),
    ],
    lifespan=lifespan,
)