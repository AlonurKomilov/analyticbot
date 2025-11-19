/**
 * Channel Card Component
 *
 * Single channel display card with:
 * - Channel info (name, description, username)
 * - Admin status indicators
 * - Channel statistics (subscribers, posts, views)
 * - MTProto toggle
 * - Edit/Delete actions
 */

import React from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    CardActions,
    Paper,
    Typography,
    Chip,
    IconButton,
    Tooltip,
    Divider
} from '@mui/material';
import {
    Tv as ChannelIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    People as PeopleIcon,
    Article as ArticleIcon,
    Visibility as VisibilityIcon,
    TrendingUp as TrendingUpIcon,
    CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { ChannelMTProtoToggle } from '@/features/mtproto-setup/components/ChannelMTProtoToggle';
import { ChannelAdminStatusIndicator } from './ChannelAdminStatusIndicator';
import { Channel } from '@/types';

export interface ChannelStats {
    id: number;
    name: string;
    username: string | null;
    subscriber_count: number;
    post_count: number;
    total_views: number;
    avg_views_per_post: number;
    latest_post_date: string | null;
    is_active: boolean;
    created_at: string;
}

export interface ChannelAdminStatus {
    bot_is_admin: boolean | null;
    mtproto_is_admin: boolean | null;
    is_inactive?: boolean;
    message?: string;
}

interface ChannelCardProps {
    channel: Channel;
    statistics?: ChannelStats;
    adminStatus?: ChannelAdminStatus;
    onEdit: (channel: Channel) => void;
    onDelete: (channel: Channel) => void;
}

export const ChannelCard: React.FC<ChannelCardProps> = ({
    channel,
    statistics,
    adminStatus,
    onEdit,
    onDelete
}) => {
    const isInactive = adminStatus?.is_inactive === true;
    const hasNoAdmin = adminStatus &&
        adminStatus.bot_is_admin === false &&
        adminStatus.mtproto_is_admin === false;

    return (
        <Card
            elevation={2}
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                opacity: isInactive ? 0.5 : 1,
                filter: isInactive ? 'grayscale(70%)' : 'none',
                border: isInactive ? '2px solid' : 'none',
                borderColor: isInactive ? 'error.main' : 'transparent',
                backgroundColor: isInactive ? 'grey.50' : 'background.paper',
                '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                }
            }}
        >
            <CardContent sx={{ flexGrow: 1 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <ChannelIcon sx={{
                        fontSize: 32,
                        color: isInactive ? 'grey.400' : 'primary.main',
                        mr: 1
                    }} />
                    <Box sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography
                                variant="h6"
                                fontWeight={600}
                                color={isInactive ? 'text.disabled' : 'text.primary'}
                            >
                                {channel.name}
                            </Typography>
                            {adminStatus && (
                                <ChannelAdminStatusIndicator
                                    botIsAdmin={adminStatus.bot_is_admin}
                                    mtprotoIsAdmin={adminStatus.mtproto_is_admin}
                                    compact={true}
                                />
                            )}
                        </Box>
                        {channel.description && (
                            <Typography
                                variant="body2"
                                color={isInactive ? 'text.disabled' : 'text.secondary'}
                            >
                                {channel.description}
                            </Typography>
                        )}
                    </Box>
                </Box>

                {/* Admin Status Alert */}
                {adminStatus && (hasNoAdmin || isInactive) && (
                    <Box sx={{ mb: 2 }}>
                        <ChannelAdminStatusIndicator
                            botIsAdmin={adminStatus.bot_is_admin}
                            mtprotoIsAdmin={adminStatus.mtproto_is_admin}
                            compact={false}
                            message={adminStatus.message}
                        />
                    </Box>
                )}

                {/* Channel Identifiers */}
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                    <Chip
                        label={`ID: ${channel.id}`}
                        size="small"
                        variant="outlined"
                    />
                    {channel.username && (
                        <Chip
                            label={`@${channel.username}`}
                            size="small"
                            color="primary"
                            variant="outlined"
                        />
                    )}
                </Box>

                {/* Statistics */}
                {!statistics ? (
                    <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.100', borderRadius: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                            No statistics available yet
                        </Typography>
                    </Box>
                ) : (
                    <Box sx={{ mt: 2 }}>
                        <Grid container spacing={1}>
                            {/* Subscribers */}
                            <Grid item xs={6}>
                                <Paper sx={{
                                    p: 1.5,
                                    bgcolor: isInactive ? 'grey.100' : 'primary.50',
                                    textAlign: 'center',
                                    opacity: isInactive ? 0.6 : 1
                                }}>
                                    <PeopleIcon sx={{
                                        fontSize: 20,
                                        color: isInactive ? 'grey.400' : 'primary.main',
                                        mb: 0.5
                                    }} />
                                    <Typography
                                        variant="h6"
                                        fontWeight={700}
                                        color={isInactive ? 'text.disabled' : 'primary.main'}
                                    >
                                        {(statistics.subscriber_count ?? 0).toLocaleString()}
                                    </Typography>
                                    <Typography variant="caption" color={isInactive ? 'text.disabled' : 'text.secondary'}>
                                        Subscribers
                                    </Typography>
                                </Paper>
                            </Grid>

                            {/* Posts */}
                            <Grid item xs={6}>
                                <Paper sx={{
                                    p: 1.5,
                                    bgcolor: isInactive ? 'grey.100' : 'info.50',
                                    textAlign: 'center',
                                    opacity: isInactive ? 0.6 : 1
                                }}>
                                    <ArticleIcon sx={{
                                        fontSize: 20,
                                        color: isInactive ? 'grey.400' : 'info.main',
                                        mb: 0.5
                                    }} />
                                    <Typography
                                        variant="h6"
                                        fontWeight={700}
                                        color={isInactive ? 'text.disabled' : 'info.main'}
                                    >
                                        {(statistics.post_count ?? 0).toLocaleString()}
                                    </Typography>
                                    <Typography variant="caption" color={isInactive ? 'text.disabled' : 'text.secondary'}>
                                        Posts
                                    </Typography>
                                </Paper>
                            </Grid>

                            {/* Total Views */}
                            <Grid item xs={6}>
                                <Paper sx={{
                                    p: 1.5,
                                    bgcolor: isInactive ? 'grey.100' : 'success.50',
                                    textAlign: 'center',
                                    opacity: isInactive ? 0.6 : 1
                                }}>
                                    <VisibilityIcon sx={{
                                        fontSize: 20,
                                        color: isInactive ? 'grey.400' : 'success.main',
                                        mb: 0.5
                                    }} />
                                    <Typography
                                        variant="h6"
                                        fontWeight={700}
                                        color={isInactive ? 'text.disabled' : 'success.main'}
                                    >
                                        {(statistics.total_views ?? 0).toLocaleString()}
                                    </Typography>
                                    <Typography variant="caption" color={isInactive ? 'text.disabled' : 'text.secondary'}>
                                        Total Views
                                    </Typography>
                                </Paper>
                            </Grid>

                            {/* Avg Views */}
                            <Grid item xs={6}>
                                <Paper sx={{
                                    p: 1.5,
                                    bgcolor: isInactive ? 'grey.100' : 'warning.50',
                                    textAlign: 'center',
                                    opacity: isInactive ? 0.6 : 1
                                }}>
                                    <TrendingUpIcon sx={{
                                        fontSize: 20,
                                        color: isInactive ? 'grey.400' : 'warning.main',
                                        mb: 0.5
                                    }} />
                                    <Typography
                                        variant="h6"
                                        fontWeight={700}
                                        color={isInactive ? 'text.disabled' : 'warning.main'}
                                    >
                                        {(statistics.avg_views_per_post ?? 0).toLocaleString()}
                                    </Typography>
                                    <Typography variant="caption" color={isInactive ? 'text.disabled' : 'text.secondary'}>
                                        Avg Views
                                    </Typography>
                                </Paper>
                            </Grid>
                        </Grid>

                        {/* Latest Post Date */}
                        {statistics.latest_post_date && (
                            <Box sx={{ mt: 1.5, p: 1, bgcolor: 'grey.50', borderRadius: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <CheckCircleIcon sx={{ fontSize: 16, color: 'success.main' }} />
                                <Typography variant="caption" color="text.secondary">
                                    Latest post: {new Date(statistics.latest_post_date).toLocaleDateString()}
                                </Typography>
                            </Box>
                        )}
                    </Box>
                )}
            </CardContent>

            <Divider />

            {/* MTProto Toggle Section */}
            <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
                <ChannelMTProtoToggle
                    channelId={channel.id}
                    channelName={channel.name}
                    compact
                />
            </Box>

            <Divider />

            {/* Actions */}
            <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
                <Tooltip title="Edit channel">
                    <IconButton
                        size="small"
                        onClick={() => onEdit(channel)}
                        color="primary"
                    >
                        <EditIcon fontSize="small" />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Delete channel">
                    <IconButton
                        size="small"
                        onClick={() => onDelete(channel)}
                        color="error"
                    >
                        <DeleteIcon fontSize="small" />
                    </IconButton>
                </Tooltip>
            </CardActions>
        </Card>
    );
};
