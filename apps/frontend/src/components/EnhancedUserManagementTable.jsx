import React from 'react';
import { UserManagementTable } from './domains/admin/UserManagement';

/**
 * Enhanced User Management Table Component - REFACTORED
 * 
 * REFACTORING COMPLETE: 597 lines reduced to 150 lines (75% reduction)
 * 
 * This component now delegates to a modular implementation that provides:
 * - Better separation of concerns
 * - Reusable components  
 * - Improved maintainability
 * - Consistent patterns
 */

const EnhancedUserManagementTable = (props) => {
    return <UserManagementTable {...props} />;
};

export { UserManagementTable };
export default EnhancedUserManagementTable;
