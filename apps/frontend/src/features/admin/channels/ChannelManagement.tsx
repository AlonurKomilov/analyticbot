/**
 * Channel Management Component (REFACTORED)
 *
 * Admin dashboard for channel oversight and management.
 *
 * REFACTORED from 551 lines to ~150 lines by:
 * - Extracting business logic to useChannelManagement hook
 * - Extracting UI components (ChannelTable, ChannelSearchBar, dialogs)
 * - Using base components (BaseDialog, BaseDataTable)
 *
 * Follows the same pattern as UserManagement for consistency.
 * This is now a pure orchestration component.
 */

import React from 'react';
import { Card, CardContent, Typography, Alert } from '@mui/material';
import { useChannelManagement } from './hooks/useChannelManagement';
import {
    ChannelTable,
    ChannelSearchBar,
    SuspendChannelDialog,
    DeleteChannelDialog,
    ChannelStatsDialog,
    ChannelAuditDialog,
} from './index';
import { spacing, colors, radius } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface ChannelManagementProps {
    onChannelUpdated?: () => void;
}

// =============================================================================
// Component
// =============================================================================

const ChannelManagement: React.FC<ChannelManagementProps> = ({ onChannelUpdated }) => {
    // Use custom hook for all business logic
    const {
        // State
        channels,
        loading,
        error,
        searchTerm,
        page,
        rowsPerPage,

        // Dialog state
        dialogState,
        suspendReason,
        statistics,
        auditLogs,
        dialogLoading,

        // Handlers
        setSearchTerm,
        setPage,
        setRowsPerPage,
        setSuspendReason,

        // Actions
        loadChannels,
        handleSearch,
        handleSuspendChannel,
        handleUnsuspendChannel,
        handleDeleteChannel,

        // Dialog actions
        openDialog,
        closeDialog,
    } = useChannelManagement(onChannelUpdated);

    return (
        <Card
            sx={{
                borderRadius: radius.lg,
                border: `1px solid ${colors.border.default}`,
            }}
            elevation={0}
        >
            <CardContent>
                {/* Header */}
                <Typography
                    variant="h5"
                    sx={{
                        mb: spacing.md,
                        fontWeight: 600,
                        color: colors.text.primary,
                    }}
                >
                    Channel Management
                </Typography>

                {/* Error Alert */}
                {error && (
                    <Alert severity="error" sx={{ mb: spacing.md }} onClose={() => {}}>
                        {error}
                    </Alert>
                )}

                {/* Search Bar */}
                <ChannelSearchBar
                    searchTerm={searchTerm}
                    onSearchChange={setSearchTerm}
                    onSearch={handleSearch}
                    onRefresh={loadChannels}
                    loading={loading}
                />

                {/* Channel Table */}
                <ChannelTable
                    channels={channels}
                    loading={loading}
                    page={page}
                    rowsPerPage={rowsPerPage}
                    onPageChange={setPage}
                    onRowsPerPageChange={setRowsPerPage}
                    onSuspendChannel={(channel) => openDialog('suspend', channel)}
                    onUnsuspendChannel={handleUnsuspendChannel}
                    onDeleteChannel={(channel) => openDialog('delete', channel)}
                    onViewStats={(channel) => openDialog('stats', channel)}
                    onViewAudit={(channel) => openDialog('audit', channel)}
                />

                {/* Dialogs */}
                <SuspendChannelDialog
                    open={dialogState.type === 'suspend'}
                    channel={dialogState.channel}
                    reason={suspendReason}
                    onReasonChange={setSuspendReason}
                    onConfirm={handleSuspendChannel}
                    onCancel={closeDialog}
                    loading={dialogLoading}
                />

                <DeleteChannelDialog
                    open={dialogState.type === 'delete'}
                    channel={dialogState.channel}
                    onConfirm={handleDeleteChannel}
                    onCancel={closeDialog}
                    loading={dialogLoading}
                />

                <ChannelStatsDialog
                    open={dialogState.type === 'stats'}
                    statistics={statistics}
                    loading={dialogLoading}
                    onClose={closeDialog}
                />

                <ChannelAuditDialog
                    open={dialogState.type === 'audit'}
                    auditLogs={auditLogs}
                    loading={dialogLoading}
                    onClose={closeDialog}
                />
            </CardContent>
        </Card>
    );
};

export default ChannelManagement;
