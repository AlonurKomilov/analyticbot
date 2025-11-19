"""
Health Check HTTP Server

Provides HTTP endpoints for process health monitoring:
- GET /health - Health status check
- GET /metrics - Detailed process metrics
- GET /ready - Readiness check

Usage:
    from apps.shared.health_server import HealthCheckServer

    server = HealthCheckServer(
        port=9090,
        process_manager=process_manager
    )

    await server.start()
    # ... run your application ...
    await server.stop()
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health checks."""

    def __init__(self, process_manager, *args, **kwargs):
        self.process_manager = process_manager
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass  # Disable default logging

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/metrics":
            self._handle_metrics()
        elif self.path == "/ready":
            self._handle_ready()
        else:
            self._send_response(404, {"error": "Not found"})

    def _handle_health(self):
        """Handle /health endpoint."""
        is_healthy, reason = self.process_manager.is_healthy()

        status_code = 200 if is_healthy else 503

        response = {
            "status": "healthy" if is_healthy else "unhealthy",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._send_response(status_code, response)

    def _handle_metrics(self):
        """Handle /metrics endpoint."""
        metrics = self.process_manager.get_metrics()

        response = {
            "metrics": asdict(metrics),
            "health": {
                "is_healthy": self.process_manager.is_healthy()[0],
                "reason": self.process_manager.is_healthy()[1],
            },
            "runtime": {
                "uptime_hours": metrics.uptime_seconds / 3600,
                "remaining_hours": (
                    self.process_manager.get_remaining_runtime() / 3600
                    if self.process_manager.get_remaining_runtime()
                    else None
                ),
            },
            "limits": {
                "max_runtime_hours": self.process_manager.max_runtime_hours,
                "memory_limit_mb": self.process_manager.memory_limit_mb,
                "cpu_limit_percent": self.process_manager.cpu_limit_percent,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._send_response(200, response)

    def _handle_ready(self):
        """Handle /ready endpoint - check if ready to serve traffic."""
        is_healthy, reason = self.process_manager.is_healthy()

        # For readiness, we also check if startup is complete
        is_ready = is_healthy and self.process_manager.running

        status_code = 200 if is_ready else 503

        response = {
            "ready": is_ready,
            "reason": reason if not is_ready else "ready",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._send_response(status_code, response)

    def _send_response(self, status_code: int, data: dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode())


class HealthCheckServer:
    """
    HTTP server for health check endpoints.

    Runs in a separate thread to avoid blocking the main event loop.
    """

    def __init__(self, port: int, process_manager, host: str = "0.0.0.0"):
        """
        Initialize health check server.

        Args:
            port: Port to listen on
            process_manager: ProcessManager instance to monitor
            host: Host to bind to (default: 0.0.0.0)
        """
        self.port = port
        self.host = host
        self.process_manager = process_manager
        self.server: HTTPServer | None = None
        self.thread: Thread | None = None
        self.running = False

    def start(self):
        """Start the health check server in a background thread."""
        if self.running:
            logger.warning("Health check server already running")
            return

        # Create handler class with process_manager bound
        def handler_factory(*args, **kwargs):
            return HealthCheckHandler(self.process_manager, *args, **kwargs)

        # Create server
        self.server = HTTPServer((self.host, self.port), handler_factory)
        self.running = True

        # Start server in thread
        self.thread = Thread(target=self._run_server, daemon=True)
        self.thread.start()

        logger.info(f"✅ Health check server started on http://{self.host}:{self.port}")
        logger.info("   - GET /health - Health status")
        logger.info("   - GET /metrics - Detailed metrics")
        logger.info("   - GET /ready - Readiness check")

    def _run_server(self):
        """Run the HTTP server (called in thread)."""
        try:
            while self.running:
                self.server.handle_request()
        except Exception as e:
            if self.running:  # Only log if not intentionally stopped
                logger.error(f"Health check server error: {e}")

    def stop(self):
        """Stop the health check server."""
        if not self.running:
            return

        logger.info("Stopping health check server...")
        self.running = False

        if self.server:
            self.server.shutdown()
            self.server = None

        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None

        logger.info("✅ Health check server stopped")

    def __enter__(self):
        """Context manager support."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.stop()
        return False
