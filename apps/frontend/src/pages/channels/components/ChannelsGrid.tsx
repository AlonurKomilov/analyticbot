/**
 * Channels Grid Component
 *
 * Displays grid of channel cards with:
 * - Empty state
 * - Loading state
 * - Channel cards with statistics and admin status
 */

import React from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    Button,
    CircularProgress
} from '@mui/material';
import {
    Tv as ChannelIcon,
    Add as AddIcon
} from '@mui/icons-material';
import { ChannelCard, ChannelStats, ChannelAdminStatus } from './ChannelCard';
import { Channel } from '@/types';

interface ChannelsGridProps {
    channels: Channel[];
    statistics: ChannelStats[] | null;
    adminStatus: Record<number, ChannelAdminStatus>;
    isLoading: boolean;
    onAddChannel: () => void;
    onEditChannel: (channel: Channel) => void;
    onDeleteChannel: (channel: Channel) => void;
}

export const ChannelsGrid: React.FC<ChannelsGridProps> = ({
    channels,
    statistics,
    adminStatus,
    isLoading,
    onAddChannel,
    onEditChannel,
    onDeleteChannel
}) => {
    // Loading state
    if (isLoading && channels.length === 0) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress size={48} />
            </Box>
        );
    }

    // Empty state
    if (channels.length === 0) {
        return (
            <Paper sx={{ p: 6, textAlign: 'center' }}>
                <ChannelIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                    No channels yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Get started by adding your first channel
                </Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={onAddChannel}>
                    Add Your First Channel
                </Button>
            </Paper>
        );
    }

    // Channels grid
    return (
        <Grid container spacing={3}>
            {channels.map((channel) => {
                const channelAdminStatus = adminStatus[Number(channel.id)];
                const channelStats = statistics?.find(s => s.id === Number(channel.id));

                return (
                    <Grid item xs={12} sm={6} md={4} key={channel.id}>
                        <ChannelCard
                            channel={channel}
                            statistics={channelStats}
                            adminStatus={channelAdminStatus}
                            onEdit={onEditChannel}
                            onDelete={onDeleteChannel}
                        />
                    </Grid>
                );
            })}
        </Grid>
    );
};
