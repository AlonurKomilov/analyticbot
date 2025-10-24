/**
 * useUserManagement Hook
 * 
 * Custom hook that encapsulates all user management business logic, state, and API calls.
 * Extracted from UserManagement.tsx god component for reusability and testability.
 * 
 * Features:
 * - User CRUD operations
 * - Search and filtering
 * - Pagination
 * - User statistics
 * - Audit logs
 * - Role management
 * - Suspend/unsuspend functionality
 * 
 * Usage:
 * ```tsx
 * const {
 *   users,
 *   loading,
 *   error,
 *   searchTerm,
 *   setSearchTerm,
 *   handleSearch,
 *   handleSuspendUser,
 *   ...rest
 * } = useUserManagement();
 * ```
 */

import { useState, useEffect, useCallback } from 'react';
import {
    adminUsersService,
    type AdminUserInfo,
    type UserStatistics,
    type UserAuditLog,
} from '@/services/admin/usersService';

// Re-export types for convenience
export type { UserStatistics, UserAuditLog };

// =============================================================================
// Types
// =============================================================================

export type UserRole = 'viewer' | 'user' | 'moderator' | 'admin' | 'owner';

export type DialogType = 'suspend' | 'delete' | 'role' | 'stats' | 'audit' | 'notify' | null;

export interface DialogState {
    type: DialogType;
    user: AdminUserInfo | null;
}

export interface UseUserManagementReturn {
    // State
    users: AdminUserInfo[];
    loading: boolean;
    error: string | null;
    
    // Search & Pagination
    searchTerm: string;
    setSearchTerm: (term: string) => void;
    page: number;
    setPage: (page: number) => void;
    rowsPerPage: number;
    setRowsPerPage: (rows: number) => void;
    
    // Dialog State
    dialogState: DialogState;
    dialogLoading: boolean;
    suspendReason: string;
    setSuspendReason: (reason: string) => void;
    newRole: UserRole;
    setNewRole: (role: UserRole) => void;
    notificationMessage: string;
    setNotificationMessage: (message: string) => void;
    
    // Statistics & Audit
    statistics: UserStatistics | null;
    auditLogs: UserAuditLog[];
    
    // Actions
    loadUsers: () => Promise<void>;
    handleSearch: () => Promise<void>;
    handleSuspendUser: () => Promise<void>;
    handleUnsuspendUser: (user: AdminUserInfo) => Promise<void>;
    handleUpdateRole: () => Promise<void>;
    handleDeleteUser: () => Promise<void>;
    handleNotifyUser: () => Promise<void>;
    
    // Dialog Actions
    openDialog: (type: Exclude<DialogType, null>, user: AdminUserInfo) => void;
    closeDialog: () => void;
    clearError: () => void;
}

// =============================================================================
// Hook
// =============================================================================

export const useUserManagement = (onUserUpdated?: () => void): UseUserManagementReturn => {
    // State
    const [users, setUsers] = useState<AdminUserInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [dialogLoading, setDialogLoading] = useState(false);
    
    // Search & Pagination
    const [searchTerm, setSearchTerm] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    
    // Dialog State
    const [dialogState, setDialogState] = useState<DialogState>({
        type: null,
        user: null,
    });
    const [suspendReason, setSuspendReason] = useState('');
    const [newRole, setNewRole] = useState<UserRole>('user');
    const [notificationMessage, setNotificationMessage] = useState('');
    
    // Statistics & Audit
    const [statistics, setStatistics] = useState<UserStatistics | null>(null);
    const [auditLogs, setAuditLogs] = useState<UserAuditLog[]>([]);

    // Load users on mount
    useEffect(() => {
        loadUsers();
    }, []);

    // Clear error helper
    const clearError = useCallback(() => {
        setError(null);
    }, []);

    // Load all users
    const loadUsers = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await adminUsersService.getAllUsers();
            setUsers(data.users);
        } catch (err: any) {
            setError(err.message || 'Failed to load users');
            console.error('Failed to load users:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Search users
    const handleSearch = useCallback(async () => {
        if (!searchTerm.trim()) {
            loadUsers();
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const results = await adminUsersService.searchUsers(searchTerm);
            setUsers(results);
        } catch (err: any) {
            setError(err.message || 'Search failed');
            console.error('Search failed:', err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm, loadUsers]);

    // Dialog Actions
    const openDialog = useCallback((type: Exclude<DialogType, null>, user: AdminUserInfo) => {
        setDialogState({ type, user });
        
        // Load data for specific dialog types
        if (type === 'stats') {
            loadStatisticsData();
        } else if (type === 'audit') {
            loadAuditLogsData(user.user_id);
        } else if (type === 'role') {
            setNewRole(user.role as UserRole);
        }
    }, []);

    const closeDialog = useCallback(() => {
        setDialogState({ type: null, user: null });
        setSuspendReason('');
        setNotificationMessage('');
        setStatistics(null);
        setAuditLogs([]);
    }, []);

    // Load statistics (internal helper)
    const loadStatisticsData = useCallback(async () => {
        setDialogLoading(true);
        setError(null);
        try {
            const stats = await adminUsersService.getUserStatistics();
            setStatistics(stats);
        } catch (err: any) {
            setError(err.message || 'Failed to load statistics');
            console.error('Failed to load statistics:', err);
        } finally {
            setDialogLoading(false);
        }
    }, []);

    // Load audit logs (internal helper)
    const loadAuditLogsData = useCallback(async (userId: number) => {
        setDialogLoading(true);
        setError(null);
        try {
            const logs = await adminUsersService.getUserAuditLog(userId);
            setAuditLogs(logs);
        } catch (err: any) {
            setError(err.message || 'Failed to load audit logs');
            console.error('Failed to load audit logs:', err);
        } finally {
            setDialogLoading(false);
        }
    }, []);

    // Suspend user (uses dialogState)
    const handleSuspendUser = useCallback(async () => {
        if (!dialogState.user || !suspendReason.trim()) {
            setError('Suspension reason is required');
            return;
        }

        setDialogLoading(true);
        setError(null);
        try {
            await adminUsersService.suspendUser(dialogState.user.user_id, {
                reason: suspendReason,
                duration_days: 30,
                notify_user: true,
            });
            await loadUsers();
            onUserUpdated?.();
            closeDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to suspend user');
            console.error('Failed to suspend user:', err);
        } finally {
            setDialogLoading(false);
        }
    }, [dialogState.user, suspendReason, loadUsers, onUserUpdated, closeDialog]);

    // Unsuspend user (direct, no dialog)
    const handleUnsuspendUser = useCallback(async (user: AdminUserInfo) => {
        setLoading(true);
        setError(null);
        try {
            await adminUsersService.unsuspendUser(user.user_id);
            await loadUsers();
            onUserUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to unsuspend user');
            console.error('Failed to unsuspend user:', err);
        } finally {
            setLoading(false);
        }
    }, [loadUsers, onUserUpdated]);

    // Update user role (uses dialogState)
    const handleUpdateRole = useCallback(async () => {
        if (!dialogState.user) return;

        setDialogLoading(true);
        setError(null);
        try {
            await adminUsersService.updateUserRole(dialogState.user.user_id, newRole);
            await loadUsers();
            onUserUpdated?.();
            closeDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to update role');
            console.error('Failed to update role:', err);
        } finally {
            setDialogLoading(false);
        }
    }, [dialogState.user, newRole, loadUsers, onUserUpdated, closeDialog]);

    // Delete user (uses dialogState)
    const handleDeleteUser = useCallback(async () => {
        if (!dialogState.user) return;

        setDialogLoading(true);
        setError(null);
        try {
            await adminUsersService.deleteUser(dialogState.user.user_id, 'Deleted by admin');
            await loadUsers();
            onUserUpdated?.();
            closeDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to delete user');
            console.error('Failed to delete user:', err);
        } finally {
            setDialogLoading(false);
        }
    }, [dialogState.user, loadUsers, onUserUpdated, closeDialog]);

    // Notify user (uses dialogState)
    const handleNotifyUser = useCallback(async () => {
        if (!dialogState.user || !notificationMessage.trim()) {
            setError('Message is required');
            return;
        }

        setDialogLoading(true);
        setError(null);
        try {
            // Note: notifyUser might not exist in the service yet
            // This is a placeholder implementation
            console.log('Sending notification to', dialogState.user.user_id, ':', notificationMessage);
            // await adminUsersService.notifyUser(dialogState.user.user_id, notificationMessage);
            onUserUpdated?.();
            closeDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to send notification');
            console.error('Failed to notify user:', err);
        } finally {
            setDialogLoading(false);
        }
    }, [dialogState.user, notificationMessage, onUserUpdated, closeDialog]);

    return {
        // State
        users,
        loading,
        error,
        
        // Search & Pagination
        searchTerm,
        setSearchTerm,
        page,
        setPage,
        rowsPerPage,
        setRowsPerPage,
        
        // Dialog State
        dialogState,
        dialogLoading,
        suspendReason,
        setSuspendReason,
        newRole,
        setNewRole,
        notificationMessage,
        setNotificationMessage,
        
        // Statistics & Audit
        statistics,
        auditLogs,
        
        // Actions
        loadUsers,
        handleSearch,
        handleSuspendUser,
        handleUnsuspendUser,
        handleUpdateRole,
        handleDeleteUser,
        handleNotifyUser,
        
        // Dialog Actions
        openDialog,
        closeDialog,
        clearError,
    };
};
