import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# ==========================================================
# Configure Logger
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("xecommerce")


# ==========================================================
# Logging Middleware
# ==========================================================

class LoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(
            self,
            request: Request,
            call_next
    ):

        start_time = time.time()

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        logger.info(
            f"Incoming Request | "
            f"{request.method} "
            f"{request.url.path} | "
            f"IP={client_ip}"
        )

        try:

            response = await call_next(request)

        except Exception as e:

            logger.exception(
                f"Unhandled Exception: {str(e)}"
            )

            raise

        process_time = round(
            time.time() - start_time,
            4
        )

        logger.info(
            f"Completed Request | "
            f"{request.method} "
            f"{request.url.path} | "
            f"Status={response.status_code} | "
            f"Time={process_time}s"
        )

        response.headers["X-Process-Time"] = str(
            process_time
        )

        return response