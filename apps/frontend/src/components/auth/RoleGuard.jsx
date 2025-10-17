/**
 * 🔒 Role-Based Access Control Components
 *
 * React components for role-based UI rendering and permission checks.
 * Integrates with AuthContext to provide RBAC functionality.
 */

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';

// Role hierarchy for permission checks
const ROLE_HIERARCHY = {
  'guest': 0,
  'readonly': 1,
  'user': 2,
  'analyst': 3,
  'moderator': 4,
  'admin': 5,
  'superadmin': 6
};

// Permission mappings by role
const ROLE_PERMISSIONS = {
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
export const hasRole = (userRole, requiredRole) => {
  const userLevel = ROLE_HIERARCHY[userRole?.toLowerCase()] || 0;
  const requiredLevel = ROLE_HIERARCHY[requiredRole?.toLowerCase()] || 0;
  return userLevel >= requiredLevel;
};

/**
 * Check if user has specific permission
 */
export const hasPermission = (userRole, permission) => {
  const permissions = ROLE_PERMISSIONS[userRole?.toLowerCase()] || [];
  return permissions.includes('*') || permissions.includes(permission);
};

/**
 * RoleGuard Component - Shows content only if user has required role
 */
export const RoleGuard = ({
  children,
  requiredRole,
  fallback = null,
  requireExact = false
}) => {
  const { user } = useAuth();

  if (!user) {
    return fallback;
  }

  const userRole = user.role || 'guest';

  // Check role requirement
  const hasRequiredRole = requireExact
    ? userRole.toLowerCase() === requiredRole.toLowerCase()
    : hasRole(userRole, requiredRole);

  return hasRequiredRole ? children : fallback;
};

/**
 * PermissionGuard Component - Shows content only if user has required permission
 */
export const PermissionGuard = ({
  children,
  requiredPermission,
  fallback = null
}) => {
  const { user } = useAuth();

  if (!user) {
    return fallback;
  }

  const userRole = user.role || 'guest';
  const hasRequiredPermission = hasPermission(userRole, requiredPermission);

  return hasRequiredPermission ? children : fallback;
};

/**
 * AdminOnly Component - Shows content only for admin users
 */
export const AdminOnly = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="admin" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * AnalystOrHigher Component - Shows content for analyst role and above
 */
export const AnalystOrHigher = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="analyst" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * UserOrHigher Component - Shows content for user role and above (excludes guests)
 */
export const UserOrHigher = ({ children, fallback = null }) => {
  return (
    <RoleGuard requiredRole="user" fallback={fallback}>
      {children}
    </RoleGuard>
  );
};

/**
 * Hook for role-based logic in components
 */
export const useRBAC = () => {
  const { user } = useAuth();

  const userRole = user?.role || 'guest';

  return {
    user,
    userRole,
    hasRole: (requiredRole, requireExact = false) => {
      return requireExact
        ? userRole.toLowerCase() === requiredRole.toLowerCase()
        : hasRole(userRole, requiredRole);
    },
    hasPermission: (permission) => hasPermission(userRole, permission),
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
