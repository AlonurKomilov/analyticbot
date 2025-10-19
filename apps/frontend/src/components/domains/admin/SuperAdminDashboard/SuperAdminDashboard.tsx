import React, { useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Alert,
    CircularProgress
} from '@mui/material';
import {
    AdminPanelSettings as AdminIcon
} from '@mui/icons-material';

// Import unified admin hooks (new architecture)
import { useAdminDashboard } from '@hooks/useAdminAPI';
import { useAdminAnalytics } from '@hooks/useSpecializedAnalytics';

// Import modular components
import AdminStatsCards from './components/AdminStatsCards';
import AdminTabNavigation from './components/AdminTabNavigation';
import OverviewTab from './components/OverviewTab';
import UserManagementTab from './components/UserManagementTab';
import AuditLogsTab from './components/AuditLogsTab';
import SystemConfigTab from './components/SystemConfigTab';
import SuspendUserDialog from './components/SuspendUserDialog';
import TabPanel from './components/TabPanel';

// Import custom hook for state management
import { useAdminDashboardState } from './hooks/useAdminDashboardState';

/**
 * SuperAdminDashboard - Refactored Modular Component
 *
 * Administrative dashboard with comprehensive system management:
 * - Overview tab with recent activity and system health
 * - User management with suspend/reactivate functionality
 * - Audit logs for administrative actions
 * - System configuration interface
 * - Real-time statistics and monitoring
 */
const SuperAdminDashboard: React.FC = () => {
    // Custom hooks for state management
    const {
        activeTab,
        setActiveTab,
        suspendDialog,
        suspensionReason,
        setSuspensionReason,
        openSuspendDialog,
        closeSuspendDialog,
        success,
        error,
        showSuccess,
        showError,
        clearNotifications
    } = useAdminDashboardState();

    // Admin API data
    const { stats, users, auditLogs, loading, error: apiError, suspendUser, reactivateUser } = useAdminDashboard();
    const { adminAnalytics } = useAdminAnalytics();

    // Set API errors to notification state
    useEffect(() => {
        if (apiError) {
            showError(apiError);
        }
    }, [apiError, showError]);

    // User suspension handler
    const handleSuspendUser = async (): Promise<void> => {
        if (!suspendDialog.user || !suspensionReason.trim()) {
            showError('Please provide a suspension reason');
            return;
        }

        try {
            await suspendUser(suspendDialog.user.id, suspensionReason);
            showSuccess(`User ${suspendDialog.user.username || 'Unknown'} has been suspended`);
            closeSuspendDialog();
        } catch (err: any) {
            showError(`Failed to suspend user: ${err.message}`);
        }
    };

    // User reactivation handler
    const handleReactivateUser = async (userId: string | number): Promise<void> => {
        try {
            await reactivateUser(userId);
            showSuccess('User has been reactivated');
        } catch (err: any) {
            showError(`Failed to reactivate user: ${err.message}`);
        }
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
                <CircularProgress />
                <Typography variant="h6" sx={{ mt: 2 }}>
                    Loading Admin Dashboard...
                </Typography>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                <AdminIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                <Typography variant="h4" component="h1">
                    Super Admin Dashboard
                </Typography>
            </Box>

            {/* Alerts */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={clearNotifications}>
                    {error}
                </Alert>
            )}
            {success && (
                <Alert severity="success" sx={{ mb: 3 }} onClose={clearNotifications}>
                    {success}
                </Alert>
            )}

            {/* System Stats Cards */}
            <AdminStatsCards stats={stats} />

            {/* Main Content Tabs */}
            <Paper sx={{ width: '100%' }}>
                <AdminTabNavigation
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                />

                {/* Overview Tab */}
                <TabPanel value={activeTab} index={0}>
                    <OverviewTab auditLogs={auditLogs} />
                </TabPanel>

                {/* User Management Tab */}
                <TabPanel value={activeTab} index={1}>
                    <UserManagementTab
                        users={users}
                        onSuspendUser={openSuspendDialog}
                        onReactivateUser={handleReactivateUser}
                    />
                </TabPanel>

                {/* Audit Logs Tab */}
                <TabPanel value={activeTab} index={2}>
                    <AuditLogsTab auditLogs={auditLogs} />
                </TabPanel>

                {/* System Configuration Tab */}
                <TabPanel value={activeTab} index={3}>
                    <SystemConfigTab />
                </TabPanel>
            </Paper>

            {/* User Suspension Dialog */}
            <SuspendUserDialog
                open={suspendDialog.open}
                user={suspendDialog.user}
                suspensionReason={suspensionReason}
                onReasonChange={setSuspensionReason}
                onConfirm={handleSuspendUser}
                onCancel={closeSuspendDialog}
            />
        </Container>
    );
};

export default SuperAdminDashboard;
