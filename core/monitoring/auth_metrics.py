"""
📊 Authentication Metrics - Prometheus Monitoring

Provides Prometheus metrics for authentication system monitoring:
- Token operations (generation, validation, rotation)
- Login attempts (success/failure)
- Session management
- Device tracking
- Anomaly detection

Usage:
    from core.monitoring.auth_metrics import auth_metrics

    # Record successful login
    auth_metrics.record_login_success(user_id="123", method="password")

    # Record token rotation
    auth_metrics.record_token_rotation(user_id="123", success=True)

    # Record anomaly detection
    auth_metrics.record_anomaly_detected(user_id="123", anomaly_type="multiple_ips")
"""

import logging
from typing import Literal

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class AuthMetrics:
    """
    📊 Authentication Metrics Collector

    Tracks authentication-related metrics for monitoring and alerting.
    Requires prometheus_client to be installed.
    """

    def __init__(self):
        """Initialize Prometheus metrics"""
        self._init_prometheus_metrics()

    def _init_prometheus_metrics(self):
        """Initialize all Prometheus metrics"""

        # ===== Login Metrics =====
        self.login_attempts_total = Counter(
            "auth_login_attempts_total",
            "Total number of login attempts",
            [
                "method",
                "status",
            ],  # method: password/telegram/oauth, status: success/failure
        )

        self.login_duration_seconds = Histogram(
            "auth_login_duration_seconds",
            "Login operation duration in seconds",
            ["method"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        # ===== Token Metrics =====
        self.token_operations_total = Counter(
            "auth_token_operations_total",
            "Total number of token operations",
            ["operation", "status"],  # operation: create/validate/refresh/revoke
        )

        self.token_rotation_total = Counter(
            "auth_token_rotation_total",
            "Total number of refresh token rotations",
            ["status"],  # success/failure
        )

        self.token_validation_duration_seconds = Histogram(
            "auth_token_validation_duration_seconds",
            "Token validation duration in seconds",
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
        )

        # ===== Session Metrics =====
        self.active_sessions_total = Gauge(
            "auth_active_sessions_total", "Current number of active sessions"
        )

        self.session_operations_total = Counter(
            "auth_session_operations_total",
            "Total number of session operations",
            ["operation"],  # create/extend/terminate
        )

        self.session_extension_total = Counter(
            "auth_session_extension_total",
            "Total number of session extensions (sliding sessions)",
            ["status"],  # success/failure
        )

        # ===== Device Tracking Metrics =====
        self.device_operations_total = Counter(
            "auth_device_operations_total",
            "Total number of device tracking operations",
            ["operation"],  # register/validate/revoke
        )

        self.new_devices_total = Counter(
            "auth_new_devices_total",
            "Total number of new devices registered",
            ["user_type"],  # returning/new
        )

        # ===== Anomaly Detection Metrics =====
        self.anomalies_detected_total = Counter(
            "auth_anomalies_detected_total",
            "Total number of anomalies detected",
            ["anomaly_type"],  # too_many_logins/multiple_ips/multiple_devices/bot_pattern
        )

        self.anomaly_actions_total = Counter(
            "auth_anomaly_actions_total",
            "Actions taken on anomalies",
            ["action"],  # block/warn/allow
        )

        # ===== Security Events =====
        self.security_events_total = Counter(
            "auth_security_events_total",
            "Total number of security events",
            ["event_type"],  # account_locked/password_reset/suspicious_activity
        )

        self.password_reset_requests_total = Counter(
            "auth_password_reset_requests_total",
            "Total number of password reset requests",
            ["status"],  # success/failure
        )

        logger.info("✅ Prometheus metrics initialized for authentication system")

    # ===== Login Metrics Methods =====

    def record_login_attempt(
        self,
        method: Literal["password", "telegram", "oauth"] = "password",
        success: bool = True,
    ):
        """Record a login attempt"""

        status = "success" if success else "failure"
        self.login_attempts_total.labels(method=method, status=status).inc()
        logger.debug(f"📊 Login attempt: method={method}, status={status}")

    def record_login_duration(
        self,
        duration_seconds: float,
        method: Literal["password", "telegram", "oauth"] = "password",
    ):
        """Record login operation duration"""

        self.login_duration_seconds.labels(method=method).observe(duration_seconds)

    def record_login_success(
        self,
        user_id: str,
        method: Literal["password", "telegram", "oauth"] = "password",
    ):
        """Convenience method to record successful login"""
        self.record_login_attempt(method=method, success=True)
        logger.info(f"✅ Login success: user_id={user_id}, method={method}")

    def record_login_failure(
        self,
        email: str,
        method: Literal["password", "telegram", "oauth"] = "password",
        reason: str = "invalid_credentials",
    ):
        """Convenience method to record failed login"""
        self.record_login_attempt(method=method, success=False)
        logger.warning(f"❌ Login failure: email={email}, method={method}, reason={reason}")

    # ===== Token Metrics Methods =====

    def record_token_operation(
        self,
        operation: Literal["create", "validate", "refresh", "revoke"],
        success: bool = True,
    ):
        """Record a token operation"""

        status = "success" if success else "failure"
        self.token_operations_total.labels(operation=operation, status=status).inc()

    def record_token_rotation(self, user_id: str, success: bool = True):
        """Record refresh token rotation"""

        status = "success" if success else "failure"
        self.token_rotation_total.labels(status=status).inc()
        logger.info(f"🔄 Token rotation: user_id={user_id}, status={status}")

    def record_token_validation_duration(self, duration_seconds: float):
        """Record token validation duration"""

        self.token_validation_duration_seconds.observe(duration_seconds)

    # ===== Session Metrics Methods =====

    def record_session_operation(self, operation: Literal["create", "extend", "terminate"]):
        """Record a session operation"""

        self.session_operations_total.labels(operation=operation).inc()

    def record_session_extension(self, session_id: str, success: bool = True):
        """Record session extension (sliding session)"""

        status = "success" if success else "failure"
        self.session_extension_total.labels(status=status).inc()
        logger.debug(f"🕐 Session extended: session_id={session_id}, status={status}")

    def update_active_sessions_count(self, count: int):
        """Update the gauge for active sessions count"""

        self.active_sessions_total.set(count)

    # ===== Device Tracking Methods =====

    def record_device_operation(self, operation: Literal["register", "validate", "revoke"]):
        """Record device tracking operation"""

        self.device_operations_total.labels(operation=operation).inc()

    def record_new_device(self, user_id: str, is_returning_user: bool = True):
        """Record new device registration"""

        user_type = "returning" if is_returning_user else "new"
        self.new_devices_total.labels(user_type=user_type).inc()
        logger.info(f"📱 New device: user_id={user_id}, user_type={user_type}")

    # ===== Anomaly Detection Methods =====

    def record_anomaly_detected(
        self,
        user_id: str,
        anomaly_type: Literal["too_many_logins", "multiple_ips", "multiple_devices", "bot_pattern"],
    ):
        """Record detected anomaly"""

        self.anomalies_detected_total.labels(anomaly_type=anomaly_type).inc()
        logger.warning(f"⚠️ Anomaly detected: user_id={user_id}, type={anomaly_type}")

    def record_anomaly_action(self, action: Literal["block", "warn", "allow"]):
        """Record action taken on anomaly"""

        self.anomaly_actions_total.labels(action=action).inc()

    # ===== Security Events Methods =====

    def record_security_event(
        self,
        event_type: Literal[
            "account_locked",
            "password_reset",
            "suspicious_activity",
            "mfa_enabled",
            "mfa_disabled",
        ],
    ):
        """Record security event"""

        self.security_events_total.labels(event_type=event_type).inc()
        logger.info(f"🔒 Security event: type={event_type}")

    def record_password_reset(self, success: bool = True):
        """Record password reset request"""

        status = "success" if success else "failure"
        self.password_reset_requests_total.labels(status=status).inc()


# Global singleton instance
auth_metrics = AuthMetrics()


# Export for easy imports
__all__ = ["auth_metrics", "AuthMetrics"]
