import { useState } from 'react';

interface SuspendDialogState {
    open: boolean;
    user: any | null;
}

interface UseAdminDashboardStateReturn {
    activeTab: number;
    setActiveTab: (tab: number) => void;
    suspendDialog: SuspendDialogState;
    suspensionReason: string;
    setSuspensionReason: (reason: string) => void;
    openSuspendDialog: (user: any) => void;
    closeSuspendDialog: () => void;
    success: string | null;
    error: string | null;
    showSuccess: (message: string) => void;
    showError: (message: string) => void;
    clearNotifications: () => void;
}

/**
 * Custom hook for managing SuperAdminDashboard state
 * Handles tab navigation, dialogs, and UI state
 */
export const useAdminDashboardState = (): UseAdminDashboardStateReturn => {
    // Tab navigation
    const [activeTab, setActiveTab] = useState<number>(0);

    // Dialog state
    const [suspendDialog, setSuspendDialog] = useState<SuspendDialogState>({
        open: false,
        user: null
    });
    const [suspensionReason, setSuspensionReason] = useState<string>('');

    // Notification state
    const [success, setSuccess] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Dialog handlers
    const openSuspendDialog = (user: any) => {
        setSuspendDialog({ open: true, user });
        setSuspensionReason('');
    };

    const closeSuspendDialog = () => {
        setSuspendDialog({ open: false, user: null });
        setSuspensionReason('');
    };

    // Notification handlers
    const showSuccess = (message: string) => {
        setSuccess(message);
        setTimeout(() => setSuccess(null), 5000);
    };

    const showError = (message: string) => {
        setError(message);
        setTimeout(() => setError(null), 5000);
    };

    const clearNotifications = () => {
        setSuccess(null);
        setError(null);
    };

    return {
        // Tab state
        activeTab,
        setActiveTab,

        // Dialog state
        suspendDialog,
        suspensionReason,
        setSuspensionReason,
        openSuspendDialog,
        closeSuspendDialog,

        // Notifications
        success,
        error,
        showSuccess,
        showError,
        clearNotifications
    };
};
