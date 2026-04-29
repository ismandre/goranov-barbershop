"""Request ID middleware for tracking requests through the system."""

import uuid
import logging
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Context variable to store request ID for the current request
request_id_var: ContextVar[str] = ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and attach a unique request ID to each request.

    The request ID is:
    - Generated as a UUID4
    - Added to response headers as X-Request-ID
    - Made available to logging context
    - Stored in context variable for access throughout request lifecycle
    """

    async def dispatch(self, request: Request, call_next):
        """Process the request and add request ID."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store in context variable
        request_id_var.set(request_id)

        # Add to request state for access in route handlers
        request.state.request_id = request_id

        # Process request
        response: Response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


def get_request_id() -> str:
    """
    Get the current request ID from context.

    Returns:
        Request ID string, or None if not in request context
    """
    return request_id_var.get()


class RequestIDFilter(logging.Filter):
    """Logging filter to inject request ID into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request ID to log record if available."""
        request_id = get_request_id()
        if request_id:
            record.request_id = request_id
        return True
