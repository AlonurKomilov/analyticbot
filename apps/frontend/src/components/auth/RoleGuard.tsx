/**
 * 🔒 Role-Based Access Control Components
 *
 * React components for role-based UI rendering and permission checks.
 * Integrates with AuthContext to provide RBAC functionality.
 */

import React, { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';

// Types
export type RoleType = 'guest' | 'readonly' | 'user' | 'analyst' | 'moderator' | 'admin' | 'superadmin';
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
  isAdmin: boolean;
  isAnalyst: boolean;
  isModerator: boolean;
  isUser: boolean;
  canRead: boolean;
  canCreate: boolean;
  canUpdate: boolean;
  canDelete: boolean;
  canExport: boolean;
}

// Role hierarchy for permission checks
const ROLE_HIERARCHY: RoleHierarchy = {
  'guest': 0,
  'readonly': 1,
  'user': 2,
  'analyst': 3,
  'moderator': 4,
  'admin': 5,
  'superadmin': 6
};

// Permission mappings by role
const ROLE_PERMISSIONS: RolePermissions = {
  'guest': ['analytics:read', 'report:read'],
  'readonly': ['analytics:read', 'report:read', 'user:read', 'settings:read'],
  'user': ['analytics:read', 'analytics:create', 'report:read', 'report:create', 'user:read', 'settings:read'],
  'analyst': ['analytics:read', 'analytics:create', 'analytics:update', 'analytics:export', 'report:read', 'report:create', 'report:update', 'report:share', 'user:read', 'settings:read'],
  'moderator': ['analytics:read', 'analytics:create', 'analytics:update', 'analytics:delete', 'analytics:export', 'report:read', 'report:create', 'report:update', 'report:delete', 'report:share', 'user:read', 'user:update', 'settings:read'],
  'admin': ['*'], // All permissions
  'superadmin': ['*'] // All permissions
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

  const userRole = user.role || 'guest';

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

  const userRole = user.role || 'guest';
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
 * AnalystOrHigher Component - Shows content for analyst role and above
 */
export const AnalystOrHigher: React.FC<GuardComponentProps> = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="analyst" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * UserOrHigher Component - Shows content for user role and above (excludes guests)
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

  const userRole: RoleType = (user?.role as RoleType) || 'guest';

  return {
    user,
    userRole,
    hasRole: (requiredRole: RoleType, requireExact: boolean = false): boolean => {
      return requireExact
        ? userRole.toLowerCase() === requiredRole.toLowerCase()
        : hasRole(userRole, requiredRole);
    },
    hasPermission: (permission: PermissionType): boolean => hasPermission(userRole, permission),
    isAdmin: hasRole(userRole, 'admin'),
    isAnalyst: hasRole(userRole, 'analyst'),
    isModerator: hasRole(userRole, 'moderator'),
    isUser: hasRole(userRole, 'user'),
    canRead: hasPermission(userRole, 'analytics:read'),
    canCreate: hasPermission(userRole, 'analytics:create'),
    canUpdate: hasPermission(userRole, 'analytics:update'),
    canDelete: hasPermission(userRole, 'analytics:delete'),
    canExport: hasPermission(userRole, 'analytics:export')
  };
};

export default RoleGuard;
