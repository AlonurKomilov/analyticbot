/**
 * useChannelManagement Hook
 *
 * Custom hook that encapsulates all channel management business logic, state, and API calls.
 * Follows the same pattern as useUserManagement for consistency.
 *
 * Features:
 * - Channel CRUD operations
 * - Search and filtering
 * - Pagination
 * - Channel statistics
 * - Audit logs
 * - Suspend/unsuspend functionality
 */

import { useState, useEffect, useCallback } from 'react';
import {
    adminChannelsService,
    type AdminChannelInfo,
    type ChannelStatistics,
    type ChannelAuditLog,
} from '@/services/admin/channelsService';

// =============================================================================
// Types
// =============================================================================

export type DialogType = 'suspend' | 'delete' | 'stats' | 'audit' | null;

export interface DialogState {
    type: DialogType;
    channel: AdminChannelInfo | null;
}

// Re-export types for convenience
export type { ChannelStatistics, ChannelAuditLog };

export interface UseChannelManagementReturn {
    // State
    channels: AdminChannelInfo[];
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

    // Statistics & Audit
    statistics: ChannelStatistics | null;
    auditLogs: ChannelAuditLog[];

    // Actions
    loadChannels: () => Promise<void>;
    handleSearch: () => Promise<void>;
    handleSuspendChannel: () => Promise<void>;
    handleUnsuspendChannel: (channel: AdminChannelInfo) => Promise<void>;
    handleDeleteChannel: () => Promise<void>;

    // Dialog Actions
    openDialog: (type: Exclude<DialogType, null>, channel: AdminChannelInfo) => void;
    closeDialog: () => void;
    clearError: () => void;
}

// =============================================================================
// Hook
// =============================================================================

export const useChannelManagement = (onChannelUpdated?: () => void): UseChannelManagementReturn => {
    // State
    const [channels, setChannels] = useState<AdminChannelInfo[]>([]);
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
        channel: null,
    });
    const [suspendReason, setSuspendReason] = useState('');

    // Statistics & Audit
    const [statistics, setStatistics] = useState<ChannelStatistics | null>(null);
    const [auditLogs, setAuditLogs] = useState<ChannelAuditLog[]>([]);

    // Load channels on mount
    useEffect(() => {
        loadChannels();
    }, []);

    // Clear error helper
    const clearError = useCallback(() => {
        setError(null);
    }, []);

    // Load all channels
    const loadChannels = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await adminChannelsService.getAllChannels();
            setChannels(data.channels);
        } catch (err: any) {
            setError(err.message || 'Failed to load channels');
            console.error('Failed to load channels:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Search channels
    const handleSearch = useCallback(async () => {
        if (!searchTerm.trim()) {
            loadChannels();
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const results = await adminChannelsService.searchChannels(searchTerm);
            setChannels(results);
        } catch (err: any) {
            setError(err.message || 'Search failed');
            console.error('Search failed:', err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm, loadChannels]);

    // Dialog Actions
    const openDialog = useCallback((type: Exclude<DialogType, null>, channel: AdminChannelInfo) => {
        setDialogState({ type, channel });

        // Load data for specific dialog types
        if (type === 'stats') {
            loadStatisticsData();
        } else if (type === 'audit') {
            loadAuditLogsData(channel.channel_id);
        }
    }, []);

    const closeDialog = useCallback(() => {
        setDialogState({ type: null, channel: null });
        setSuspendReason('');
        setStatistics(null);
        setAuditLogs([]);
    }, []);

    // Load statistics (internal helper)
    const loadStatisticsData = useCallback(async () => {
        setDialogLoading(true);
        setError(null);
        try {
            const stats = await adminChannelsService.getChannelStatistics();
            setStatistics(stats);
        } catch (err: any) {
            setError(err.message || 'Failed to load statistics');
            console.error('Failed to load statistics:', err);
        } finally {
            setDialogLoading(false);
        }
    }, []);

    // Load audit logs (internal helper)
    const loadAuditLogsData = useCallback(async (channelId: string) => {
        setDialogLoading(true);
        setError(null);
        try {
            const logs = await adminChannelsService.getChannelAuditLog(channelId);
            setAuditLogs(logs);
        } catch (err: any) {
            setError(err.message || 'Failed to load audit logs');
            console.error('Failed to load audit logs:', err);
        } finally {
            setDialogLoading(false);
        }
    }, []);

    // Suspend channel (uses dialogState)
    const handleSuspendChannel = useCallback(async () => {
        if (!dialogState.channel || !suspendReason.trim()) {
            setError('Suspension reason is required');
            return;
        }

        setDialogLoading(true);
        setError(null);
        try {
            await adminChannelsService.suspendChannel(dialogState.channel.channel_id, {
                reason: suspendReason,
                duration_days: 30,
                notify_user: true,
            });
            await loadChannels();
            onChannelUpdated?.();
            closeDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to suspend channel');
            console.error('Failed to suspend channel:', err);
        } finally {
            setDialogLoading(false);
        }
    }, [dialogState.channel, suspendReason, loadChannels, onChannelUpdated, closeDialog]);

    // Unsuspend channel (direct, no dialog)
    const handleUnsuspendChannel = useCallback(async (channel: AdminChannelInfo) => {
        setLoading(true);
        setError(null);
        try {
            await adminChannelsService.unsuspendChannel(channel.channel_id);
            await loadChannels();
            onChannelUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to unsuspend channel');
            console.error('Failed to unsuspend channel:', err);
        } finally {
            setLoading(false);
        }
    }, [loadChannels, onChannelUpdated]);

    // Delete channel (uses dialogState)
    const handleDeleteChannel = useCallback(async () => {
        if (!dialogState.channel) return;

        setDialogLoading(true);
        setError(null);
        try {
            await adminChannelsService.deleteChannel(dialogState.channel.channel_id, 'Deleted by admin');
            await loadChannels();
            onChannelUpdated?.();
            closeDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to delete channel');
            console.error('Failed to delete channel:', err);
        } finally {
            setDialogLoading(false);
        }
    }, [dialogState.channel, loadChannels, onChannelUpdated, closeDialog]);

    return {
        // State
        channels,
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

        // Statistics & Audit
        statistics,
        auditLogs,

        // Actions
        loadChannels,
        handleSearch,
        handleSuspendChannel,
        handleUnsuspendChannel,
        handleDeleteChannel,

        // Dialog Actions
        openDialog,
        closeDialog,
        clearError,
    };
};
