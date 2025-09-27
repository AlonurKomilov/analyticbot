"""
SuperAdmin Service Layer
Enterprise-grade service for SuperAdmin operations
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.shared_kernel.domain.entities.admin import (
    AdminAuditLog,
    AdminSession,
    AdminUser,
    SystemUser,
    UserStatus,
)


class SuperAdminService:
    """Service for SuperAdmin operations and management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def authenticate_admin(
        self, db: AsyncSession, username: str, password: str, ip_address: str
    ) -> AdminSession | None:
        """Authenticate admin user and create session"""
        try:
            # Get admin user
            stmt = select(AdminUser).where(
                AdminUser.username == username, AdminUser.is_active == True
            )
            result = await db.execute(stmt)
            admin = result.scalar_one_or_none()

            if not admin:
                await self._log_security_event(
                    db,
                    "failed_login",
                    {
                        "username": username,
                        "ip": ip_address,
                        "reason": "user_not_found",
                    },
                )
                return None

            # Verify password
            if not self.pwd_context.verify(password, admin.password_hash):
                await self._log_security_event(
                    db,
                    "failed_login",
                    {
                        "username": username,
                        "ip": ip_address,
                        "reason": "invalid_password",
                    },
                )
                return None

            # Successful login - reset failed attempts
            admin.failed_login_attempts = 0
            admin.last_login = datetime.utcnow()

            # Create session
            session = await self.create_admin_session(db, admin, ip_address, "Test User Agent")
            await db.commit()

            await self._log_security_event(
                db,
                "successful_login",
                {"username": username, "ip": ip_address},
                admin.id,
            )
            return session

        except Exception as e:
            await self._log_security_event(
                db,
                "login_error",
                {"username": username, "ip": ip_address, "error": str(e)},
            )
            return None

    async def create_admin_session(
        self, db: AsyncSession, admin_user: AdminUser, ip_address: str, user_agent: str
    ) -> AdminSession:
        """Create secure admin session"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=8)  # 8-hour sessions

        session = AdminSession(
            admin_user_id=admin_user.id,
            session_token=hashlib.sha256(session_token.encode()).hexdigest(),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        db.add(session)
        return session

    async def get_system_stats(self, db: AsyncSession) -> dict[str, Any]:
        """Get comprehensive system statistics"""
        # User statistics
        total_users = await db.scalar(select(func.count(SystemUser.id))) or 0
        active_users = (
            await db.scalar(
                select(func.count(SystemUser.id)).where(SystemUser.status == UserStatus.ACTIVE)
            )
            or 0
        )
        premium_users = (
            await db.scalar(
                select(func.count(SystemUser.id)).where(SystemUser.subscription_tier == "premium")
            )
            or 0
        )

        # Admin statistics
        total_admins = await db.scalar(select(func.count(AdminUser.id))) or 0
        active_admins = (
            await db.scalar(select(func.count(AdminUser.id)).where(AdminUser.is_active == True))
            or 0
        )
        active_sessions = (
            await db.scalar(
                select(func.count(AdminSession.id)).where(
                    and_(
                        AdminSession.is_active == True,
                        AdminSession.expires_at > datetime.utcnow(),
                    )
                )
            )
            or 0
        )

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "premium": premium_users,
                "suspended": total_users - active_users,
            },
            "admins": {
                "total": total_admins,
                "active": active_admins,
                "sessions": active_sessions,
            },
            "system": {
                "uptime": "N/A",  # Will be calculated in production
                "version": "1.0.0",
                "environment": "development",
            },
        }

    async def suspend_user(
        self,
        db: AsyncSession,
        admin_id: int,
        user_id: int,
        suspended_by: str,
        reason: str,
    ) -> bool:
        """Suspend a system user"""
        try:
            stmt = select(SystemUser).where(SystemUser.telegram_id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Store original status for audit log
            original_status = user.status

            user.status = UserStatus.SUSPENDED
            user.updated_at = datetime.utcnow()

            # Create audit log entry
            await self._create_audit_log(
                db,
                admin_id,
                "suspend_user",
                "system_users",
                user.id,
                {"status": original_status.value},
                {"status": UserStatus.SUSPENDED.value},
                f"User suspended: {reason}",
            )

            await db.commit()
            return True

        except Exception:
            await db.rollback()
            return False

    async def get_audit_logs(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 50,
        admin_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Get paginated audit logs"""
        offset = (page - 1) * limit

        stmt = (
            select(AdminAuditLog)
            .order_by(desc(AdminAuditLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        if admin_id:
            stmt = stmt.where(AdminAuditLog.admin_user_id == admin_id)

        result = await db.execute(stmt)
        logs = result.scalars().all()

        # Get total count
        count_stmt = select(func.count(AdminAuditLog.id))
        if admin_id:
            count_stmt = count_stmt.where(AdminAuditLog.admin_user_id == admin_id)
        total_count = await db.scalar(count_stmt) or 0

        return {
            "logs": logs,
            "total": total_count,
            "page": page,
            "pages": ((total_count) + limit - 1) // limit if total_count > 0 else 0,
        }

    async def _create_audit_log(
        self,
        db: AsyncSession,
        admin_id: int,
        action: str,
        table_name: str,
        record_id: UUID,
        old_values: dict | None = None,
        new_values: dict | None = None,
        additional_info: str | None = None,
    ) -> None:
        """Create audit log entry"""
        log = AdminAuditLog(
            admin_user_id=admin_id,
            action=action,
            resource_type=table_name,
            resource_id=str(record_id),
            ip_address="127.0.0.1",  # Default for testing
            old_values=old_values,
            new_values=new_values,
            success=True,
            additional_data={"info": additional_info} if additional_info else None,
        )

        db.add(log)

    async def validate_admin_session(self, token: str, ip_address: str) -> AdminUser | None:
        """Validate admin session token"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            stmt = (
                select(AdminSession)
                .join(AdminUser)
                .where(
                    and_(
                        AdminSession.session_token == token_hash,
                        AdminSession.is_active == True,
                        AdminSession.expires_at > datetime.utcnow(),
                        AdminUser.is_active == True,
                    )
                )
            )
            result = await self.db.execute(stmt)
            session = result.scalar_one_or_none()

            if not session:
                return None

            # Update session activity
            session.last_activity = datetime.utcnow()
            await self.db.commit()

            # Return admin user
            stmt = select(AdminUser).where(AdminUser.id == session.admin_user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        except Exception:
            return None

    async def get_system_users(self, page: int = 1, limit: int = 50) -> dict[str, Any]:
        """Get paginated system users"""
        offset = (page - 1) * limit

        stmt = select(SystemUser).order_by(desc(SystemUser.created_at)).offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        users = result.scalars().all()

        # Get total count
        count_stmt = select(func.count(SystemUser.id))
        total_count = await self.db.scalar(count_stmt) or 0

        return {
            "users": users,
            "total": total_count,
            "page": page,
            "pages": ((total_count) + limit - 1) // limit if total_count > 0 else 0,
        }

    async def reactivate_user(self, user_id: int, admin_id: int) -> bool:
        """Reactivate a suspended user"""
        try:
            stmt = select(SystemUser).where(SystemUser.telegram_id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Store original status for audit log
            original_status = user.status

            user.status = UserStatus.ACTIVE
            user.updated_at = datetime.utcnow()

            # Create audit log entry
            await self._create_audit_log(
                self.db,
                admin_id,
                "reactivate_user",
                "system_users",
                user.id,
                {"status": original_status.value},
                {"status": UserStatus.ACTIVE.value},
                "User reactivated by admin",
            )

            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            return False

    async def get_system_config(self) -> dict[str, Any]:
        """Get system configuration"""
        # This would typically come from a database table or config file
        return {
            "maintenance_mode": False,
            "max_users_per_channel": 1000,
            "rate_limit_messages_per_hour": 100,
            "premium_features_enabled": True,
            "backup_frequency_hours": 24,
            "session_timeout_hours": 8,
            "max_failed_login_attempts": 5,
        }

    async def update_system_config(self, config: dict[str, Any], admin_id: int) -> bool:
        """Update system configuration"""
        try:
            # In a real implementation, this would update a database table
            # For now, we'll just log the change
            await self._create_audit_log(
                self.db,
                admin_id,
                "update_system_config",
                "system_config",
                UUID("00000000-0000-0000-0000-000000000001"),  # Dummy UUID for config
                {},  # old values would be fetched
                config,
                "System configuration updated",
            )

            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            return False

    async def _log_security_event(
        self,
        db: AsyncSession,
        event_type: str,
        details: dict,
        admin_id: UUID | None = None,
    ) -> None:
        """Log security events"""
        log = AdminAuditLog(
            admin_user_id=admin_id,
            action=f"security_{event_type}",
            resource_type="security_events",
            resource_id="0",
            ip_address=details.get("ip", "127.0.0.1"),
            new_values=details,
            success=event_type == "successful_login",
            additional_data={"info": f"Security event: {event_type}"},
        )

        db.add(log)
