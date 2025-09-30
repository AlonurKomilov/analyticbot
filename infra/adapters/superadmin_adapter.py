"""
SuperAdmin Service Repository Adapter

Complete adapter that provides repository implementations for the refactored SuperAdminService.
This preserves all existing logic while providing clean architecture compliance.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import hashlib
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from infra.database.models.superadmin_orm import (
    AdminUser,
    AdminSession, 
    AdminAuditLog,
    SystemUser,
    UserStatus,
)


class SQLAlchemyAdminRepository:
    """Complete repository implementation for the SuperAdminService"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_admin_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get admin user by username"""
        stmt = select(AdminUser).where(AdminUser.username == username)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()
        
        if admin:
            return {
                'id': admin.id,
                'username': admin.username,
                'password_hash': admin.password_hash,
                'is_active': admin.is_active,
                'role': admin.role
            }
        return None

    async def update_admin_login(self, admin_id: UUID, last_login: datetime, failed_attempts: int = 0) -> None:
        """Update admin login timestamp"""
        stmt = select(AdminUser).where(AdminUser.id == admin_id)
        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()
        
        if admin:
            admin.failed_login_attempts = failed_attempts
            admin.last_login = last_login
            await self.db.commit()

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        # User statistics
        total_users = await self.db.scalar(select(func.count(SystemUser.id))) or 0
        active_users = (
            await self.db.scalar(
                select(func.count(SystemUser.id)).where(SystemUser.status == UserStatus.ACTIVE)
            ) or 0
        )
        premium_users = (
            await self.db.scalar(
                select(func.count(SystemUser.id)).where(SystemUser.subscription_tier == "premium")
            ) or 0
        )

        # Admin statistics  
        total_admins = await self.db.scalar(select(func.count(AdminUser.id))) or 0
        active_admins = (
            await self.db.scalar(select(func.count(AdminUser.id)).where(AdminUser.is_active == True))
            or 0
        )
        active_sessions = (
            await self.db.scalar(
                select(func.count(AdminSession.id)).where(
                    and_(
                        AdminSession.is_active == True, 
                        AdminSession.expires_at > datetime.utcnow()
                    )
                )
            ) or 0
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
                "active_sessions": active_sessions,
            },
            "system": {
                "uptime": "N/A",  # Would be calculated elsewhere
                "version": "2.0.0",
                "last_backup": "N/A",  # Would come from backup service
            }
        }

    async def suspend_user(self, user_id: UUID, reason: str, admin_id: UUID) -> bool:
        """Suspend a system user"""
        try:
            stmt = select(SystemUser).where(SystemUser.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.status = UserStatus.SUSPENDED
            user.suspended_at = datetime.utcnow()
            user.suspended_by = admin_id
            user.suspension_reason = reason

            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            return False

    async def get_audit_logs(self, admin_id: Optional[UUID] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        stmt = (
            select(AdminAuditLog)
            .order_by(desc(AdminAuditLog.created_at))
            .limit(limit)
            .offset(offset)
        )

        if admin_id:
            stmt = stmt.where(AdminAuditLog.admin_user_id == admin_id)

        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        return [
            {
                "id": log.id,
                "admin_user_id": log.admin_user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
                "success": log.success,
                "additional_data": log.additional_data or {}
            }
            for log in logs
        ]

    async def create_audit_log(self, admin_id: UUID, action: str, resource_type: str, resource_id: str, details: Dict[str, Any]) -> None:
        """Create new audit log entry"""
        log = AdminAuditLog(
            admin_user_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=details.get("ip_address", "127.0.0.1"),
            new_values=details,
            success=True,
            additional_data={"info": details.get("additional_info", "")}
        )

        self.db.add(log)
        await self.db.commit()

    async def validate_admin_session(self, token_hash: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate admin session token"""
        try:
            stmt = (
                select(AdminSession, AdminUser)
                .join(AdminUser, AdminSession.admin_user_id == AdminUser.id)
                .where(
                    and_(
                        AdminSession.session_token == token_hash,
                        AdminSession.is_active == True,
                        AdminSession.expires_at > datetime.utcnow(),
                        AdminUser.is_active == True
                    )
                )
            )

            result = await self.db.execute(stmt)
            session_data = result.first()

            if session_data:
                session, admin_user = session_data
                
                # Update last activity
                session.last_activity = datetime.utcnow()
                await self.db.commit()
                
                return {
                    "admin_id": admin_user.id,
                    "username": admin_user.username,
                    "role": admin_user.role,
                    "session_id": session.id
                }

            return None

        except Exception:
            return None

    async def create_session(self, admin_user: Dict[str, Any], ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Create secure admin session"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=8)  # 8-hour sessions

        session = AdminSession(
            admin_user_id=admin_user['id'],
            session_token=hashlib.sha256(session_token.encode()).hexdigest(),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        self.db.add(session)
        await self.db.commit()
        
        return {
            "session_id": session.id,
            "session_token": session_token,  # Return unhashed token
            "expires_at": expires_at
        }

    async def log_security_event(self, event_type: str, details: Dict[str, Any], admin_id: Optional[UUID] = None) -> None:
        """Log security events"""
        log = AdminAuditLog(
            admin_user_id=admin_id,
            action=f"security_{event_type}",
            resource_type="security_events",
            resource_id="0",
            ip_address=details.get("ip", "127.0.0.1"),
            new_values=details,
            success=event_type == "successful_login",
            additional_data={"info": f"Security event: {event_type}"}
        )
        self.db.add(log)
        await self.db.commit()


def create_superadmin_service_with_adapter(db: AsyncSession):
    """
    Factory function that creates a SuperAdminService with complete repository adapter.
    
    This maintains backward compatibility while improving architecture.
    """
    # Import the clean core service
    from core.services.superadmin_service import SuperAdminService
    
    # Create repository adapter
    admin_repo = SQLAlchemyAdminRepository(db)
    
    # Create a compatible security logger
    class SecurityLoggerAdapter:
        def __init__(self, repo):
            self.repo = repo
            
        async def log_security_event(self, event_type: str, details: Dict[str, Any], admin_id: Optional[UUID] = None) -> None:
            await self.repo.log_security_event(event_type, details, admin_id)
    
    security_logger = SecurityLoggerAdapter(admin_repo)
    
    # Return service with proper dependencies
    return SuperAdminService(admin_repo, security_logger)