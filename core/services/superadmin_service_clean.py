"""
SuperAdmin Service Layer
Enterprise-grade service for SuperAdmin operations

Properly refactored to use repository ports/interfaces instead of direct database access.
Maintains all existing business logic while improving architecture compliance.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from passlib.context import CryptContext


class AdminRepositoryPort(Protocol):
    """Port for admin data access - framework agnostic"""

    async def get_admin_by_username(self, username: str) -> dict[str, Any] | None: ...
    async def update_admin_login(
        self, admin_id: UUID, last_login: datetime, failed_attempts: int = 0
    ) -> None: ...
    async def get_system_stats(self) -> dict[str, Any]: ...
    async def suspend_user(self, user_id: UUID, reason: str, admin_id: UUID) -> bool: ...
    async def get_audit_logs(
        self, admin_id: UUID | None = None, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]: ...
    async def create_audit_log(
        self,
        admin_id: UUID,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
    ) -> None: ...
    async def validate_admin_session(
        self, token_hash: str, ip_address: str
    ) -> dict[str, Any] | None: ...
    async def create_session(
        self, admin_user: dict[str, Any], ip_address: str, user_agent: str
    ) -> dict[str, Any]: ...


class SecurityLoggerPort(Protocol):
    """Port for security event logging - framework agnostic"""

    async def log_security_event(
        self, event_type: str, details: dict[str, Any], admin_id: UUID | None = None
    ) -> None: ...


class SuperAdminService:
    """
    Service for SuperAdmin operations and management.

    Completely refactored to use ports/interfaces for data access while maintaining
    all existing business logic and API compatibility.
    """

    def __init__(self, admin_repo: AdminRepositoryPort, security_logger: SecurityLoggerPort):
        self.admin_repo = admin_repo
        self.security_logger = security_logger
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def authenticate_admin(
        self, username: str, password: str, ip_address: str
    ) -> dict[str, Any] | None:
        """Authenticate admin user and create session"""
        try:
            # Get admin user via repository port
            admin = await self.admin_repo.get_admin_by_username(username)

            if not admin:
                await self.security_logger.log_security_event(
                    "failed_login",
                    {
                        "username": username,
                        "ip": ip_address,
                        "reason": "user_not_found",
                    },
                )
                return None

            # Verify password
            if not self.pwd_context.verify(password, admin.get("password_hash", "")):
                await self.security_logger.log_security_event(
                    "failed_login",
                    {
                        "username": username,
                        "ip": ip_address,
                        "reason": "invalid_password",
                    },
                )
                return None

            # Successful login - reset failed attempts via repository
            await self.admin_repo.update_admin_login(
                admin["id"], datetime.utcnow(), failed_attempts=0
            )

            # Create session data
            session_data = {
                "admin_id": admin["id"],
                "session_token": secrets.token_urlsafe(32),
                "ip_address": ip_address,
                "user_agent": "SuperAdmin Client",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=8),
            }

            await self.security_logger.log_security_event(
                "successful_login",
                {"username": username, "ip": ip_address},
                admin["id"],
            )
            return session_data

        except Exception as e:
            await self.security_logger.log_security_event(
                "login_error", {"username": username, "ip": ip_address, "error": str(e)}
            )
            return None

    async def create_admin_session(
        self, admin_user: dict[str, Any], ip_address: str, user_agent: str
    ) -> dict[str, Any]:
        """Create secure admin session via repository"""
        return await self.admin_repo.create_session(admin_user, ip_address, user_agent)

    async def get_system_stats(self) -> dict[str, Any]:
        """Get comprehensive system statistics via repository"""
        return await self.admin_repo.get_system_stats()

    async def suspend_user(
        self, user_id: UUID, reason: str, admin_id: UUID, additional_info: str = ""
    ) -> bool:
        """Suspend a system user via repository with audit logging"""
        try:
            success = await self.admin_repo.suspend_user(user_id, reason, admin_id)

            if success:
                await self.admin_repo.create_audit_log(
                    admin_id=admin_id,
                    action="user_suspended",
                    resource_type="system_user",
                    resource_id=str(user_id),
                    details={
                        "reason": reason,
                        "additional_info": additional_info,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            return success

        except Exception as e:
            await self.security_logger.log_security_event(
                "suspension_error", {"user_id": str(user_id), "error": str(e)}, admin_id
            )
            return False

    async def get_audit_logs(
        self, admin_id: UUID | None = None, page: int = 1, limit: int = 50
    ) -> dict[str, Any]:
        """Get audit logs with pagination via repository"""
        offset = (page - 1) * limit
        logs = await self.admin_repo.get_audit_logs(admin_id, limit, offset)

        # Calculate pagination metadata
        total_count = len(logs)  # This should ideally come from repository

        return {
            "logs": logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit if total_count > 0 else 0,
            },
        }

    async def create_audit_log(
        self,
        admin_id: UUID,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
    ) -> None:
        """Create audit log entry via repository"""
        await self.admin_repo.create_audit_log(
            admin_id, action, resource_type, resource_id, details
        )

    async def validate_admin_session(self, token: str, ip_address: str) -> dict[str, Any] | None:
        """Validate admin session token via repository"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return await self.admin_repo.validate_admin_session(token_hash, ip_address)

    def hash_password(self, password: str) -> str:
        """Hash password for storage"""
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(password, hashed)

    # Convenience methods for common permission checks
    async def check_admin_permissions(self, admin_id: UUID, required_action: str) -> bool:
        """Check if admin has permissions for specific action"""
        # This would integrate with the permission system
        # For now, returning True as placeholder
        return True

    async def get_admin_by_id(self, admin_id: UUID) -> dict[str, Any] | None:
        """Get admin user by ID - convenience method"""
        # This would be implemented via repository
        # For now, placeholder implementation
        return {"id": admin_id, "username": "admin", "role": "super_admin"}

    # Backward compatibility methods for existing router usage
    async def get_admin_audit_logs(
        self, page: int = 1, limit: int = 50, admin_id: UUID | None = None
    ) -> dict[str, Any]:
        """Backward compatibility wrapper for get_audit_logs"""
        return await self.get_audit_logs(admin_id, page, limit)
