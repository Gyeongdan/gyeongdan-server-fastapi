# middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


WHITELISTED_IPS = [
    "59.20.239.26"  # 운영사무실
    "58.239.146.39"  # 610
    "58.234.217.58"  # 609
]
API_KEY = "018fc735-7bf8-700a-b8d1-b9eb36ee7410"


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        x_forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else request.client.host
        )

        # Check if IP is whitelisted
        if client_ip not in WHITELISTED_IPS:
            return JSONResponse(
                status_code=403,
                content={GenericResponseDTO(result=False, message="IP is not allowed")},
            )

        # Check if API key is valid
        api_key = request.headers.get("apiKey")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={GenericResponseDTO(result=False, message="Invalid API key")},
            )

        response = await call_next(request)
        return response
