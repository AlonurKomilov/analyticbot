/**
 * 🔒 Role-Based Access Control Components
 *
 * React components for role-based UI rendering and permission checks.
 * Integrates with AuthContext to provide RBAC functionality.
 * 
 * Role Hierarchy (5-tier system):
 * viewer(0) < user(1) < moderator(2) < admin(3) < owner(5)
 */

import React, { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';

// Types
export type RoleType = 'viewer' | 'user' | 'moderator' | 'admin' | 'owner';
export type PermissionType = string;

interface RoleHierarchy {
  [key: string]: number;
}

interface RolePermissions {
  [key: string]: PermissionType[];
}

interface RoleGuardProps {
  children: ReactNode;
  requiredRole: RoleType;
  fallback?: ReactNode;
  requireExact?: boolean;
}

interface PermissionGuardProps {
  children: ReactNode;
  requiredPermission: PermissionType;
  fallback?: ReactNode;
}

interface GuardComponentProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface RBACHook {
  user: any;
  userRole: RoleType;
  hasRole: (requiredRole: RoleType, requireExact?: boolean) => boolean;
  hasPermission: (permission: PermissionType) => boolean;
  isOwner: boolean;
  isAdmin: boolean;
  isModerator: boolean;
  isUser: boolean;
  isViewer: boolean;
  canRead: boolean;
  canCreate: boolean;
  canUpdate: boolean;
  canDelete: boolean;
  canExport: boolean;
}

// Role hierarchy for permission checks (5-tier system)
const ROLE_HIERARCHY: RoleHierarchy = {
  'viewer': 0,    // Public read-only
  'user': 1,      // Authenticated users
  'moderator': 2, // Support team
  'admin': 3,     // Platform admins
  'owner': 5      // System owner (level 5 to match backend)
};

// Permission mappings by role
const ROLE_PERMISSIONS: RolePermissions = {
  'viewer': ['analytics:read', 'report:read'],
  'user': ['analytics:read', 'analytics:create', 'report:read', 'report:create', 'user:read', 'settings:read'],
  'moderator': ['analytics:read', 'analytics:create', 'analytics:update', 'analytics:delete', 'analytics:export', 'report:read', 'report:create', 'report:update', 'report:delete', 'report:share', 'user:read', 'user:update', 'settings:read'],
  'admin': ['*'], // All permissions
  'owner': ['*']  // All permissions
};

/**
 * Check if user has required role or higher
 */
export const hasRole = (userRole: string | undefined | null, requiredRole: RoleType): boolean => {
  const userLevel = ROLE_HIERARCHY[userRole?.toLowerCase() ?? ''] || 0;
  const requiredLevel = ROLE_HIERARCHY[requiredRole?.toLowerCase()] || 0;
  return userLevel >= requiredLevel;
};

/**
 * Check if user has specific permission
 */
export const hasPermission = (userRole: string | undefined | null, permission: PermissionType): boolean => {
  const permissions = ROLE_PERMISSIONS[userRole?.toLowerCase() ?? ''] || [];
  return permissions.includes('*') || permissions.includes(permission);
};

/**
 * RoleGuard Component - Shows content only if user has required role
 */
export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  requiredRole,
  fallback = null,
  requireExact = false
}) => {
  const { user } = useAuth();

  if (!user) {
    return <>{fallback}</>;
  }

  const userRole = (user as any).role || 'viewer';

  // Check role requirement
  const hasRequiredRole = requireExact
    ? userRole.toLowerCase() === requiredRole.toLowerCase()
    : hasRole(userRole, requiredRole);

  return hasRequiredRole ? <>{children}</> : <>{fallback}</>;
};

/**
 * PermissionGuard Component - Shows content only if user has required permission
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  requiredPermission,
  fallback = null
}) => {
  const { user } = useAuth();

  if (!user) {
    return <>{fallback}</>;
  }

  const userRole = (user as any).role || 'viewer';
  const hasRequiredPermission = hasPermission(userRole, requiredPermission);

  return hasRequiredPermission ? <>{children}</> : <>{fallback}</>;
};

/**
 * AdminOnly Component - Shows content only for admin users
 */
export const AdminOnly: React.FC<GuardComponentProps> = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="admin" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * ModeratorOrHigher Component - Shows content for moderator role and above
 */
export const ModeratorOrHigher: React.FC<GuardComponentProps> = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="moderator" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * UserOrHigher Component - Shows content for user role and above (excludes viewers)
 */
export const UserOrHigher: React.FC<GuardComponentProps> = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="user" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * Hook for role-based logic in components
 */
export const useRBAC = (): RBACHook => {
  const { user } = useAuth();

  const userRole: RoleType = ((user as any)?.role as RoleType) || 'viewer';

  return {
    user,
    userRole,
    hasRole: (requiredRole: RoleType, requireExact: boolean = false): boolean => {
      return requireExact
        ? userRole.toLowerCase() === requiredRole.toLowerCase()
        : hasRole(userRole, requiredRole);
    },
    hasPermission: (permission: PermissionType): boolean => hasPermission(userRole, permission),
    isOwner: hasRole(userRole, 'owner'),
    isAdmin: hasRole(userRole, 'admin'),
    isModerator: hasRole(userRole, 'moderator'),
    isUser: hasRole(userRole, 'user'),
    isViewer: hasRole(userRole, 'viewer'),
    canRead: hasPermission(userRole, 'analytics:read'),
    canCreate: hasPermission(userRole, 'analytics:create'),
    canUpdate: hasPermission(userRole, 'analytics:update'),
    canDelete: hasPermission(userRole, 'analytics:delete'),
    canExport: hasPermission(userRole, 'analytics:export')
  };
};

export default RoleGuard;
