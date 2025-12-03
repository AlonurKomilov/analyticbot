/**
 * Auth Feature Module
 * Barrel export for authentication features
 */

// Login and registration
export * from './login';

// MFA and access control
export { default as MFASetup } from './MFASetup';
export { default as RoleGuard, AdminOnly, hasRole, hasPermission, type RoleType, type PermissionType } from './RoleGuard';
