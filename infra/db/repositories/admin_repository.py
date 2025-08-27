"""
Admin Repository Implementation
Concrete implementation of AdminRepository interface
"""

from typing import Optional
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.interfaces import AdminRepository as IAdminRepository


class AsyncpgAdminRepository(IAdminRepository):
    """Admin repository implementation using asyncpg"""
    
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def get_admin_by_username(self, username: str) -> Optional[dict]:
        """Get admin by username"""
        query = """
            SELECT id, username, role, permissions, created_at, last_login
            FROM admins 
            WHERE username = $1 AND is_active = true
        """
        row = await self._pool.fetchrow(query, username)
        return dict(row) if row else None

    async def create_admin(self, admin_data: dict) -> dict:
        """Create new admin"""
        query = """
            INSERT INTO admins (username, password_hash, role, permissions)
            VALUES ($1, $2, $3, $4)
            RETURNING id, username, role, permissions, created_at
        """
        username = admin_data['username']
        password_hash = admin_data['password_hash']
        role = admin_data.get('role', 'admin')
        permissions = admin_data.get('permissions', [])
        
        row = await self._pool.fetchrow(query, username, password_hash, role, permissions)
        return dict(row) if row else None

    async def update_admin(self, admin_id: int, **updates) -> bool:
        """Update admin information"""
        # Build dynamic update query
        set_clauses = []
        values = []
        param_count = 1
        
        allowed_fields = ['username', 'password_hash', 'role', 'permissions', 'last_login', 'is_active']
        
        for key, value in updates.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not set_clauses:
            return False
            
        query = f"""
            UPDATE admins 
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = ${param_count}
        """
        values.append(admin_id)
        
        result = await self._pool.execute(query, *values)
        return result == 'UPDATE 1'

    async def admin_exists(self, username: str) -> bool:
        """Check if admin exists"""
        query = "SELECT EXISTS(SELECT 1 FROM admins WHERE username = $1 AND is_active = true)"
        return await self._pool.fetchval(query, username)


class SQLAlchemyAdminRepository(IAdminRepository):
    """Admin repository implementation using SQLAlchemy (for future use)"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_admin_by_username(self, username: str) -> Optional[dict]:
        """Get admin by username - SQLAlchemy implementation"""
        # TODO: Implement when we migrate to SQLAlchemy models
        pass
    
    async def create_admin(self, admin_data: dict) -> dict:
        """Create new admin"""
        # TODO: Implement SQLAlchemy version
        pass
    
    async def update_admin(self, admin_id: int, **updates) -> bool:
        """Update admin information"""
        # TODO: Implement SQLAlchemy version
        pass
    
    async def admin_exists(self, username: str) -> bool:
        """Check if admin exists"""
        # TODO: Implement SQLAlchemy version
        return True
