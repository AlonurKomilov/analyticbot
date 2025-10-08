import { useState } from 'react';

/**
 * Custom hook for managing SuperAdminDashboard state
 * Handles tab navigation, dialogs, and UI state
 */
export const useAdminDashboardState = () => {
    // Tab navigation
    const [activeTab, setActiveTab] = useState(0);

    // Dialog state
    const [suspendDialog, setSuspendDialog] = useState({
        open: false,
        user: null
    });
    const [suspensionReason, setSuspensionReason] = useState('');

    // Notification state
    const [success, setSuccess] = useState(null);
    const [error, setError] = useState(null);

    // Dialog handlers
    const openSuspendDialog = (user) => {
        setSuspendDialog({ open: true, user });
        setSuspensionReason('');
    };

    const closeSuspendDialog = () => {
        setSuspendDialog({ open: false, user: null });
        setSuspensionReason('');
    };

    // Notification handlers
    const showSuccess = (message) => {
        setSuccess(message);
        setTimeout(() => setSuccess(null), 5000);
    };

    const showError = (message) => {
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
