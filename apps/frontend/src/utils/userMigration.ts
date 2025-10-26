/**
 * User Status Migration Utilities
 *
 * Provides backward compatibility helpers for transitioning from
 * isActive boolean to UserStatus enum
 *
 * Created: October 25, 2025
 */

import { User, UserStatus } from '../types/api';

/**
 * Legacy User interface with isActive boolean
 * @deprecated Use User with status field instead
 */
export interface LegacyUser {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role: string;
  tier?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
  preferences?: any;
}

/**
 * Check if user is active (backward compatibility helper)
 *
 * @param user - User object with status field
 * @returns true if user status is 'active'
 *
 * @example
 * const user = { status: 'active', ... };
 * if (isUserActive(user)) {
 *   // User can access the system
 * }
 */
export function isUserActive(user: User): boolean {
  return user.status === 'active';
}

/**
 * Check if user account is accessible
 * Active users can access the system
 *
 * @param user - User object
 * @returns true if user can access the system
 */
export function canUserAccessSystem(user: User): boolean {
  return user.status === 'active';
}

/**
 * Check if user is suspended
 *
 * @param user - User object
 * @returns true if user status is 'suspended'
 */
export function isUserSuspended(user: User): boolean {
  return user.status === 'suspended';
}

/**
 * Check if user is pending verification
 *
 * @param user - User object
 * @returns true if user status is 'pending'
 */
export function isUserPending(user: User): boolean {
  return user.status === 'pending';
}

/**
 * Check if user is deleted
 *
 * @param user - User object
 * @returns true if user status is 'deleted'
 */
export function isUserDeleted(user: User): boolean {
  return user.status === 'deleted';
}

/**
 * Migrate legacy user object to new format
 * Converts isActive boolean to status enum
 *
 * @param legacy - Legacy user with isActive field
 * @returns User with status field
 *
 * @example
 * const legacyUser = { isActive: true, ... };
 * const user = migrateLegacyUser(legacyUser);
 * // user.status === 'active'
 */
export function migrateLegacyUser(legacy: LegacyUser): User {
  const status: UserStatus = legacy.isActive ? 'active' : 'inactive';

  return {
    ...legacy,
    status,
    // Remove isActive from result but keep for backward compatibility
    isActive: legacy.isActive,
    role: legacy.role as any,
    tier: legacy.tier as any
  };
}

/**
 * Convert UserStatus to boolean for legacy code
 *
 * @param status - User status enum value
 * @returns true if status is 'active'
 */
export function statusToBoolean(status: UserStatus): boolean {
  return status === 'active';
}

/**
 * Convert boolean to UserStatus
 *
 * @param isActive - Boolean active state
 * @returns 'active' if true, 'inactive' if false
 */
export function booleanToStatus(isActive: boolean): UserStatus {
  return isActive ? 'active' : 'inactive';
}

/**
 * Get user-friendly status label
 *
 * @param status - User status enum value
 * @returns Human-readable status label
 */
export function getUserStatusLabel(status: UserStatus): string {
  switch (status) {
    case 'active':
      return 'Active';
    case 'inactive':
      return 'Inactive';
    case 'suspended':
      return 'Suspended';
    case 'pending':
      return 'Pending Verification';
    case 'deleted':
      return 'Deleted';
  }
}

/**
 * Get user status description
 *
 * @param status - User status enum value
 * @returns Description of what the status means
 */
export function getUserStatusDescription(status: UserStatus): string {
  switch (status) {
    case 'active':
      return 'User account is active and can access all features';
    case 'inactive':
      return 'User account is inactive and cannot access the system';
    case 'suspended':
      return 'User account is suspended due to policy violation or payment issues';
    case 'pending':
      return 'User account is pending email verification or admin approval';
    case 'deleted':
      return 'User account has been deleted and cannot be recovered';
  }
}

/**
 * Check if user status allows login
 *
 * @param status - User status enum value
 * @returns true if user can log in
 */
export function canUserLogin(status: UserStatus): boolean {
  // Only active and pending users can attempt login
  // Pending users might see verification prompt after login
  return status === 'active' || status === 'pending';
}

/**
 * Check if user status requires action
 *
 * @param status - User status enum value
 * @returns true if user needs to take action
 */
export function requiresUserAction(status: UserStatus): boolean {
  return status === 'pending' || status === 'suspended';
}

/**
 * Get action message for user status
 *
 * @param status - User status enum value
 * @returns Action message if action required, null otherwise
 */
export function getUserStatusActionMessage(status: UserStatus): string | null {
  switch (status) {
    case 'pending':
      return 'Please verify your email address to activate your account';
    case 'suspended':
      return 'Your account is suspended. Please contact support for assistance';
    case 'inactive':
      return 'Your account is inactive. Please contact support to reactivate';
    case 'deleted':
      return 'This account has been deleted';
    case 'active':
      return null;
  }
}

/**
 * Normalize user object to ensure it has status field
 * Handles both new (status) and legacy (isActive) formats
 *
 * @param user - User object that might have either status or isActive
 * @returns User object with guaranteed status field
 */
export function normalizeUser(user: any): User {
  // If user already has status field, return as is
  if (user.status) {
    return {
      ...user,
      isActive: statusToBoolean(user.status) // Add isActive for backward compatibility
    };
  }

  // If user has only isActive, convert it
  if (typeof user.isActive === 'boolean') {
    return {
      ...user,
      status: booleanToStatus(user.isActive)
    };
  }

  // Default to inactive if neither field exists
  console.warn('User object missing both status and isActive fields, defaulting to inactive');
  return {
    ...user,
    status: 'inactive',
    isActive: false
  };
}
