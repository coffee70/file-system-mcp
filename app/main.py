import contextlib

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware import Middleware

from .mcp_server import mcp
from .security_middleware import ApiKeyMiddleware


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with mcp.session_manager.run():
        yield


app = Starlette(
    middleware=[Middleware(ApiKeyMiddleware)],
    routes=[
        Mount("/", app=mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)