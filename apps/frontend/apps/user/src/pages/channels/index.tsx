/**
 * Channels Management Page - Refactored Microservice Architecture
 *
 * Main orchestrator component that:
 * - Manages state and business logic
 * - Delegates rendering to specialized components
 * - Coordinates between child components
 *
 * Architecture: God object refactored into focused microservice components
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Button,
    IconButton,
    Alert,
    Divider,
    Tooltip,
    CircularProgress
} from '@mui/material';
import {
    Add as AddIcon,
    Refresh as RefreshIcon,
    Info as InfoIcon
} from '@mui/icons-material';
import { useChannelStore } from '@store';
import { Channel } from '@/types';
import { apiClient } from '@/api/client';
import { useChannelAdminStatus } from './hooks/useChannelAdminStatus';

// Microservice Components
import { ChannelStatisticsOverview, type AggregateStats } from './components/ChannelStatisticsOverview';
import { ChannelsGrid } from './components/ChannelsGrid';
import {
    CreateChannelDialog,
    EditChannelDialog,
    DeleteChannelDialog,
    type ChannelFormData
} from './components/ChannelDialogs';
import { type ChannelStats } from './components/ChannelCard';

interface StatisticsResponse {
    aggregate: AggregateStats;
    channels: ChannelStats[];
}

const ChannelsManagementPage: React.FC = () => {
    // Store hooks
    const { channels, isLoading, error, fetchChannels, addChannel, updateChannel, deleteChannel } = useChannelStore();
    const { adminStatus, fetchAdminStatus, refreshAdminStatus } = useChannelAdminStatus();

    // Dialog state
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);

    // Statistics state
    const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
    const [statsLoading, setStatsLoading] = useState(true);

    // Form state
    const [formData, setFormData] = useState<ChannelFormData>({
        name: '',
        description: '',
        username: '',
        telegram_id: ''
    });
    const [formError, setFormError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    // Initialize data
    useEffect(() => {
        fetchChannels();
        fetchStatistics();
        fetchAdminStatus();

        // Auto-refresh admin status every 2 minutes
        const interval = setInterval(() => {
            refreshAdminStatus();
        }, 2 * 60 * 1000);

        return () => clearInterval(interval);
    }, [fetchChannels, fetchAdminStatus, refreshAdminStatus]);

    // Fetch statistics
    const fetchStatistics = async () => {
        try {
            setStatsLoading(true);
            const response = await apiClient.get<StatisticsResponse>('/channels/statistics/overview');
            setStatistics(response);
        } catch (err) {
            console.error('Failed to fetch statistics:', err);
        } finally {
            setStatsLoading(false);
        }
    };

    // Handle refresh
    const handleRefresh = async () => {
        await Promise.all([
            fetchChannels(),
            fetchStatistics(),
            refreshAdminStatus()
        ]);
    };

    // ============================================================================
    // CREATE DIALOG HANDLERS
    // ============================================================================

    const handleOpenCreate = () => {
        setFormData({
            name: '',
            description: '',
            username: '',
            telegram_id: ''
        });
        setFormError('');
        setCreateDialogOpen(true);
    };

    const handleFormDataChange = (data: Partial<ChannelFormData>) => {
        setFormData(prev => ({ ...prev, ...data }));
    };

    const handleCreate = async () => {
        try {
            setSubmitting(true);
            setFormError('');

            await addChannel({
                name: formData.name.trim(),
                description: formData.description.trim(),
                username: formData.username.trim(),
                telegram_id: formData.telegram_id.trim() || undefined,
                subscriber_count: formData.subscriber_count || 0
            });

            setCreateDialogOpen(false);
            await handleRefresh();
        } catch (err: any) {
            // Extract error message from various possible sources
            let errorMessage = 'Failed to add channel';

            // Check for API response with detail
            if (err.response?.data?.detail) {
                errorMessage = err.response.data.detail;
            } else if (err.message) {
                // The ApiRequestError includes the detail in the message
                // Check for specific error patterns
                if (err.message.includes('already registered') || err.message.includes('already added')) {
                    // Channel already exists - use the message as-is
                    errorMessage = err.message;
                } else if (err.message.includes('bot') && (err.message.includes('admin') || err.message.includes('administrator'))) {
                    // Bot not admin error
                    errorMessage = err.message;
                } else if (err.message.includes('API is currently unavailable')) {
                    errorMessage = 'The API server is currently unavailable. Please try again in a few moments.';
                } else if (err.message.includes('CORS') || err.message.includes('Network')) {
                    errorMessage = 'Cannot connect to the server. Please check your internet connection.';
                } else if (err.message.includes('timeout')) {
                    errorMessage = 'The request timed out. Please try again.';
                } else {
                    errorMessage = err.message;
                }
            }

            setFormError(errorMessage);
        } finally {
            setSubmitting(false);
        }
    };

    // ============================================================================
    // EDIT DIALOG HANDLERS
    // ============================================================================

    const handleOpenEdit = (channel: Channel) => {
        setSelectedChannel(channel);
        setFormData({
            name: channel.name,
            description: channel.description || '',
            username: channel.username || '',
            telegram_id: channel.telegramId || ''
        });
        setFormError('');
        setEditDialogOpen(true);
    };

    const handleEdit = async () => {
        if (!selectedChannel) return;

        try {
            setSubmitting(true);
            setFormError('');

            await updateChannel(selectedChannel.id, {
                name: formData.name.trim(),
                description: formData.description.trim(),
                username: formData.username.trim(),
                telegramId: formData.telegram_id.trim() || undefined
            });

            setEditDialogOpen(false);
            await handleRefresh();
        } catch (err: any) {
            setFormError(err.response?.data?.detail || 'Failed to update channel');
        } finally {
            setSubmitting(false);
        }
    };

    // ============================================================================
    // DELETE DIALOG HANDLERS
    // ============================================================================

    const handleOpenDelete = (channel: Channel) => {
        setSelectedChannel(channel);
        setDeleteDialogOpen(true);
    };

    const handleDelete = async () => {
        if (!selectedChannel) return;

        try {
            setSubmitting(true);
            await deleteChannel(selectedChannel.id);
            setDeleteDialogOpen(false);
            await handleRefresh();
        } catch (err) {
            console.error('Failed to delete channel:', err);
        } finally {
            setSubmitting(false);
        }
    };

    // ============================================================================
    // FORM HANDLERS
    // ============================================================================

    const handleInputChange = (field: keyof ChannelFormData) =>
        (event: React.ChangeEvent<HTMLInputElement>) => {
            setFormData(prev => ({
                ...prev,
                [field]: event.target.value
            }));
        };

    // ============================================================================
    // RENDER
    // ============================================================================

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box>
                        <Typography variant="h4" fontWeight={700} gutterBottom>
                            Channel Analytics Tracking
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Add existing Telegram channels to track and analyze their performance
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Tooltip title="Refresh channels and statistics">
                            <span>
                                <IconButton onClick={handleRefresh} disabled={isLoading || statsLoading}>
                                    {(isLoading || statsLoading) ? <CircularProgress size={24} /> : <RefreshIcon />}
                                </IconButton>
                            </span>
                        </Tooltip>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={handleOpenCreate}
                            size="large"
                        >
                            Add Channel
                        </Button>
                    </Box>
                </Box>
                <Divider />
            </Box>

            {/* Statistics Overview - Microservice Component */}
            <ChannelStatisticsOverview
                statistics={statistics?.aggregate || null}
                isLoading={statsLoading}
            />

            {/* Error Display */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
                    {error}
                </Alert>
            )}

            {/* Info Banner */}
            <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
                <strong>Note:</strong> To sync data from Telegram, make sure your Bot and MTProto is added as an administrator to each channel.
            </Alert>

            {/* Channels Grid - Microservice Component */}
            <ChannelsGrid
                channels={channels}
                statistics={statistics?.channels || null}
                adminStatus={adminStatus}
                isLoading={isLoading}
                onAddChannel={handleOpenCreate}
                onEditChannel={handleOpenEdit}
                onDeleteChannel={handleOpenDelete}
            />

            {/* Dialogs - Microservice Components */}
            <CreateChannelDialog
                open={createDialogOpen}
                formData={formData}
                formError={formError}
                submitting={submitting}
                onClose={() => setCreateDialogOpen(false)}
                onInputChange={handleInputChange}
                onSubmit={handleCreate}
                onFormDataChange={handleFormDataChange}
                onClearError={() => setFormError('')}
            />

            <EditChannelDialog
                open={editDialogOpen}
                formData={formData}
                formError={formError}
                submitting={submitting}
                onClose={() => setEditDialogOpen(false)}
                onInputChange={handleInputChange}
                onSubmit={handleEdit}
            />

            <DeleteChannelDialog
                open={deleteDialogOpen}
                channel={selectedChannel}
                submitting={submitting}
                onClose={() => setDeleteDialogOpen(false)}
                onConfirm={handleDelete}
            />
        </Container>
    );
};

export default ChannelsManagementPage;
