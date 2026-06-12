import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):

    # Stores request timestamps per client IP
    requests = {}

    # Maximum requests allowed
    MAX_REQUESTS = 100

    # Time window (seconds)
    WINDOW = 60

    async def dispatch(
            self,
            request: Request,
            call_next
    ):

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        current_time = time.time()

        # Initialize client history
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Remove expired timestamps
        self.requests[client_ip] = [
            timestamp
            for timestamp in self.requests[client_ip]
            if current_time - timestamp < self.WINDOW
        ]

        # Check limit
        if len(self.requests[client_ip]) >= self.MAX_REQUESTS:

            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Too many requests. Please try again later."
                }
            )

        # Add current request
        self.requests[client_ip].append(
            current_time
        )

        response = await call_next(request)

        return response