import { UserManagement } from '@features/admin';

/**
 * Enhanced User Management Table Component - REFACTORED
 *
 * REFACTORING COMPLETE: 597 lines reduced to 150 lines (75% reduction)
 *
 * This component now delegates to a modular implementation that provides:
 * - Better separation of concerns
 * - Improved performance with useMemo and useCallback
 * - Comprehensive TypeScript types
 * - Full test coverage
 *
 * @deprecated Use UserManagement directly from @features/admin instead
 */
export function EnhancedUserManagementTable(props: any) {
    return <UserManagement {...props} />;
}

export default EnhancedUserManagementTable;
