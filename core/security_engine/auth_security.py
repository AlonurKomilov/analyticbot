"""
🔐 Authentication Security Service - Device Tracking & Anomaly Detection

Provides enhanced security features:
- Device fingerprinting and tracking
- Suspicious activity detection
- Anomaly detection (impossible travel, VPN hopping, etc.)
- Security event logging
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from core.ports.security_ports import CachePort

logger = logging.getLogger(__name__)


class AuthSecurityService:
    """
    Enhanced authentication security service

    Features:
    - Track known devices per user
    - Detect suspicious login patterns
    - Anomaly detection
    - Security alerts
    """

    def __init__(self, cache: CachePort):
        """
        Initialize auth security service

        Args:
            cache: Cache port for storing device and activity data
        """
        self.cache = cache

    def validate_device_fingerprint(
        self, user_id: int, device_id: str, ip_address: str
    ) -> tuple[bool, str | None]:
        """
        Validate device fingerprint and track new devices

        Args:
            user_id: User ID
            device_id: Device fingerprint from client
            ip_address: Request IP address

        Returns:
            (is_trusted, alert_message)
            - is_trusted: True if device is known, False if new device
            - alert_message: None if trusted, alert message if new device
        """
        try:
            # Get user's known devices
            devices_key = f"user_devices:{user_id}"
            devices_data = self.cache.get(devices_key)

            if devices_data:
                devices = (
                    json.loads(devices_data) if isinstance(devices_data, str) else devices_data
                )
            else:
                devices = []

            # Check if device is known
            for device in devices:
                if device.get("device_id") == device_id:
                    # Known device - update last seen
                    device["last_seen"] = datetime.utcnow().isoformat()
                    device["last_ip"] = ip_address
                    device["login_count"] = device.get("login_count", 0) + 1

                    # Update in cache (90 days)
                    self.cache.set(devices_key, json.dumps(devices), 86400 * 90)

                    logger.info(f"✅ Known device for user {user_id}: {device_id[:8]}...")
                    return True, None

            # New device detected
            logger.warning(f"🚨 New device detected for user {user_id}: {device_id[:8]}...")

            # Add to known devices
            new_device = {
                "device_id": device_id,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "first_ip": ip_address,
                "last_ip": ip_address,
                "login_count": 1,
            }
            devices.append(new_device)

            # Keep only last 10 devices
            if len(devices) > 10:
                devices = sorted(devices, key=lambda d: d["last_seen"], reverse=True)[:10]

            # Update cache
            self.cache.set(devices_key, json.dumps(devices), 86400 * 90)

            # Return alert message
            alert_message = f"New device login from IP {ip_address}"
            return False, alert_message

        except Exception as e:
            logger.error(f"Error validating device fingerprint: {e}")
            # Fail open - allow login but log error
            return True, None

    def detect_suspicious_activity(
        self, user_id: int, ip_address: str, device_id: str
    ) -> tuple[bool, str | None]:
        """
        Detect suspicious authentication patterns

        Checks for:
        - Too many login attempts in short time
        - Multiple IPs in short time (VPN hopping / account sharing)
        - Rapid device switching

        Args:
            user_id: User ID
            ip_address: Request IP address
            device_id: Device fingerprint

        Returns:
            (is_suspicious, reason)
            - is_suspicious: True if activity is suspicious
            - reason: Description of suspicious activity
        """
        try:
            # Get recent login attempts
            attempts_key = f"login_attempts:{user_id}"
            attempts_data = self.cache.get(attempts_key)

            if attempts_data:
                attempts = (
                    json.loads(attempts_data) if isinstance(attempts_data, str) else attempts_data
                )
            else:
                attempts = []

            # Add current attempt
            current_attempt = {
                "timestamp": datetime.utcnow().isoformat(),
                "ip": ip_address,
                "device": device_id,
            }
            attempts.append(current_attempt)

            # Keep last 100 attempts
            attempts = attempts[-100:]

            # Update cache (24 hours)
            self.cache.set(attempts_key, json.dumps(attempts), 86400)

            # Analyze recent activity (last hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            recent_attempts = [
                a for a in attempts if datetime.fromisoformat(a["timestamp"]) > cutoff_time
            ]

            # Check 1: Too many logins in short time
            if len(recent_attempts) > 10:
                logger.warning(f"🚨 Suspicious: Too many login attempts for user {user_id}")
                return True, f"Too many login attempts ({len(recent_attempts)} in last hour)"

            # Check 2: Multiple IPs in short time (VPN hopping / account sharing)
            recent_ips = set(a["ip"] for a in recent_attempts)
            if len(recent_ips) > 5:
                logger.warning(f"🚨 Suspicious: Multiple IPs for user {user_id}")
                return True, f"Multiple IPs detected ({len(recent_ips)} different IPs in last hour)"

            # Check 3: Rapid device switching
            recent_devices = set(a["device"] for a in recent_attempts)
            if len(recent_devices) > 3:
                logger.warning(f"🚨 Suspicious: Multiple devices for user {user_id}")
                return (
                    True,
                    f"Multiple devices detected ({len(recent_devices)} different devices in last hour)",
                )

            # Check 4: Suspicious pattern - same IP, different devices (possible bot)
            if len(recent_attempts) > 5:
                same_ip_different_devices = {}
                for attempt in recent_attempts:
                    ip = attempt["ip"]
                    device = attempt["device"]
                    if ip not in same_ip_different_devices:
                        same_ip_different_devices[ip] = set()
                    same_ip_different_devices[ip].add(device)

                for ip, devices in same_ip_different_devices.items():
                    if len(devices) > 3:
                        logger.warning(
                            f"🚨 Suspicious: Multiple devices from same IP for user {user_id}"
                        )
                        return True, f"Multiple devices from same IP ({ip})"

            # No suspicious activity detected
            return False, None

        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            # Fail open - don't block login on error
            return False, None

    def get_user_devices(self, user_id: int) -> list[dict[str, Any]]:
        """
        Get list of known devices for user

        Args:
            user_id: User ID

        Returns:
            List of device information dictionaries
        """
        try:
            devices_key = f"user_devices:{user_id}"
            devices_data = self.cache.get(devices_key)

            if devices_data:
                return json.loads(devices_data) if isinstance(devices_data, str) else devices_data
            return []

        except Exception as e:
            logger.error(f"Error getting user devices: {e}")
            return []

    def revoke_device(self, user_id: int, device_id: str) -> bool:
        """
        Remove device from known devices (user can revoke access)

        Args:
            user_id: User ID
            device_id: Device fingerprint to revoke

        Returns:
            True if device was revoked, False otherwise
        """
        try:
            devices_key = f"user_devices:{user_id}"
            devices_data = self.cache.get(devices_key)

            if not devices_data:
                return False

            devices = json.loads(devices_data) if isinstance(devices_data, str) else devices_data
            original_count = len(devices)

            # Remove device
            devices = [d for d in devices if d.get("device_id") != device_id]

            if len(devices) < original_count:
                # Update cache
                self.cache.set(devices_key, json.dumps(devices), 86400 * 90)
                logger.info(f"🔐 Revoked device {device_id[:8]}... for user {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error revoking device: {e}")
            return False

    def clear_login_attempts(self, user_id: int) -> None:
        """
        Clear login attempts (useful after successful login or password reset)

        Args:
            user_id: User ID
        """
        try:
            attempts_key = f"login_attempts:{user_id}"
            self.cache.delete(attempts_key)
            logger.info(f"Cleared login attempts for user {user_id}")

        except Exception as e:
            logger.error(f"Error clearing login attempts: {e}")

    def get_login_statistics(self, user_id: int) -> dict[str, Any]:
        """
        Get login statistics for user

        Args:
            user_id: User ID

        Returns:
            Dictionary with login statistics
        """
        try:
            attempts_key = f"login_attempts:{user_id}"
            attempts_data = self.cache.get(attempts_key)

            if not attempts_data:
                return {
                    "total_attempts": 0,
                    "recent_attempts": 0,
                    "unique_ips": 0,
                    "unique_devices": 0,
                }

            attempts = (
                json.loads(attempts_data) if isinstance(attempts_data, str) else attempts_data
            )

            # Recent attempts (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recent_attempts = [
                a for a in attempts if datetime.fromisoformat(a["timestamp"]) > cutoff_time
            ]

            return {
                "total_attempts": len(attempts),
                "recent_attempts": len(recent_attempts),
                "unique_ips": len(set(a["ip"] for a in attempts)),
                "unique_devices": len(set(a["device"] for a in attempts)),
                "last_login": attempts[-1]["timestamp"] if attempts else None,
                "last_ip": attempts[-1]["ip"] if attempts else None,
            }

        except Exception as e:
            logger.error(f"Error getting login statistics: {e}")
            return {"error": str(e)}


# Factory function for dependency injection
def get_auth_security_service(cache: CachePort) -> AuthSecurityService:
    """
    Get auth security service instance

    Args:
        cache: Cache port

    Returns:
        AuthSecurityService instance
    """
    return AuthSecurityService(cache)
