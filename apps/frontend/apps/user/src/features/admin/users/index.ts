/**
 * User Management Components
 *
 * Extracted components from UserManagement.tsx god component
 */

// Main component
export { default as UserManagement } from './UserManagement';

// Sub-components
export { default as UserTable } from './UserTable';
export { default as UserSearchBar } from './UserSearchBar';
export { default as SuspendUserDialog } from './SuspendUserDialog';
export { default as DeleteUserDialog } from './DeleteUserDialog';
export { default as ChangeRoleDialog } from './ChangeRoleDialog';
export { default as UserStatsDialog } from './UserStatsDialog';
export { default as UserAuditDialog } from './UserAuditDialog';
export { default as NotifyUserDialog } from './NotifyUserDialog';

// Hooks
export { useUserManagement } from './hooks/useUserManagement';

// Types
export type { UserTableProps } from './UserTable';
export type { UserSearchBarProps } from './UserSearchBar';
export type { SuspendUserDialogProps } from './SuspendUserDialog';
export type { DeleteUserDialogProps } from './DeleteUserDialog';
export type { ChangeRoleDialogProps } from './ChangeRoleDialog';
export type { UserStatsDialogProps } from './UserStatsDialog';
export type { UserAuditDialogProps } from './UserAuditDialog';
export type { NotifyUserDialogProps } from './NotifyUserDialog';
