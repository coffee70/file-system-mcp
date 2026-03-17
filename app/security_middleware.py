import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class ApiKeyMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        expected = os.getenv("MCP_API_KEY")

        if expected:
            provided = request.headers.get("x-api-key")

            # fallback to query param because ChatGPT connectors
            # do not reliably send custom headers
            if not provided:
                provided = request.query_params.get("api_key")

            if provided != expected:
                return JSONResponse(
                    {"error": "unauthorized"},
                    status_code=401
                )

        return await call_next(request)