"""
API Endpoint Redirect Middleware - Phase 1
Redirects duplicate endpoints to their canonical versions.

This middleware handles the consolidation of duplicate API endpoints
without breaking existing clients. Old endpoints automatically redirect
to new endpoints with HTTP 307 (Temporary Redirect) or 308 (Permanent Redirect).
"""

import logging

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class EndpointRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle endpoint redirects during API restructuring.

    Phase 1 Redirects (Duplicate Consolidation):
    - /payment/* → /payments/*
    - /ai-chat/* → /ai/chat/*
    - /ai-insights/* → /ai/insights/*
    - /ai-services/* → /ai/services/*
    - /content-protection/* → /content/*
    """

    # Define redirect mappings
    REDIRECTS = {
        # Payment endpoints (remove singular /payment)
        "/payment": "/payments",
        # AI endpoints consolidation
        "/ai-chat": "/ai",
        "/ai-insights": "/ai",
        "/ai-services": "/ai",
        # Content endpoints consolidation
        "/content-protection": "/content",
    }

    def __init__(self, app, use_permanent_redirects: bool = False):
        """
        Initialize the redirect middleware.

        Args:
            app: The FastAPI application
            use_permanent_redirects: If True, use 308 (Permanent Redirect)
                                    If False, use 307 (Temporary Redirect)
        """
        super().__init__(app)
        self.redirect_status_code = 308 if use_permanent_redirects else 307

    async def dispatch(self, request: Request, call_next):
        """
        Process requests and redirect if path matches old endpoint pattern.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            RedirectResponse if path matches old endpoint, otherwise normal response
        """
        path = request.url.path

        # Check if path starts with any old endpoint prefix
        for old_prefix, new_prefix in self.REDIRECTS.items():
            if path.startswith(old_prefix):
                # Construct new path by replacing old prefix with new prefix
                new_path = path.replace(old_prefix, new_prefix, 1)

                # Preserve query parameters
                query_string = request.url.query
                if query_string:
                    new_url = f"{new_path}?{query_string}"
                else:
                    new_url = new_path

                # Log the redirect for monitoring
                logger.info(
                    f"API Redirect: {request.method} {path} → {new_path} "
                    f"(Client: {request.client.host if request.client else 'unknown'})"
                )

                # Return redirect response
                return RedirectResponse(url=new_url, status_code=self.redirect_status_code)

        # No redirect needed, continue to route handler
        return await call_next(request)
