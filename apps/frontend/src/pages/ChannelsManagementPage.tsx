/**
 * Channels Management Page
 *
 * Comprehensive channel management interface for users to:
 * - View all their channels
 * - Add new channels
 * - Edit channel details
 * - Delete channels
 * - See channel statistics
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Grid,
    Card,
    CardContent,
    CardActions,
    Button,
    IconButton,
    Chip,
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    CircularProgress,
    Tooltip,
    Divider,
    Skeleton
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Refresh as RefreshIcon,
    Tv as ChannelIcon,
    TrendingUp as TrendingUpIcon,
    Info as InfoIcon,
    People as PeopleIcon,
    Article as ArticleIcon,
    Visibility as VisibilityIcon,
    CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { ChannelMTProtoToggle } from '@/features/mtproto-setup/components/ChannelMTProtoToggle';
import { useChannelStore } from '@store';
import { Channel } from '@/types';
import { apiClient } from '@/api/client';

interface ChannelFormData {
    name: string;
    description: string;
    username: string;
    telegram_id: string;  // Store as string for input, convert to number later
}

interface ChannelStats {
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

interface AggregateStats {
    total_channels: number;
    total_subscribers: number;
    total_posts: number;
    total_views: number;
    active_channels: number;
    avg_views_per_post: number;
}

interface StatisticsResponse {
    aggregate: AggregateStats;
    channels: ChannelStats[];
}

const ChannelsManagementPage: React.FC = () => {
    const { channels, isLoading, error, fetchChannels, addChannel, updateChannel, deleteChannel } = useChannelStore();

    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);

    // Statistics state
    const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
    const [statsLoading, setStatsLoading] = useState(true);

    const [formData, setFormData] = useState<ChannelFormData>({
        name: '',
        description: '',
        username: '',
        telegram_id: ''
    });
    const [formError, setFormError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    // Load channels on mount
    useEffect(() => {
        fetchChannels();
        fetchStatistics();
    }, [fetchChannels]);

    // Fetch statistics
    const fetchStatistics = async () => {
        setStatsLoading(true);
        try {
            const response = await apiClient.get('/channels/statistics/overview');
            setStatistics(response as StatisticsResponse);
        } catch (err: any) {
            console.error('Failed to fetch statistics:', err);
            // Statistics error is not critical - just log it
        } finally {
            setStatsLoading(false);
        }
    };

    // Refresh both channels and statistics
    const handleRefresh = () => {
        fetchChannels();
        fetchStatistics();
    };

    // Handle create dialog
    const handleOpenCreate = () => {
        setFormData({ name: '', description: '', username: '', telegram_id: '' });
        setFormError('');
        setCreateDialogOpen(true);
    };

    const handleCreate = async () => {
        if (!formData.name.trim()) {
            setFormError('Channel name is required');
            return;
        }

        if (!formData.username.trim()) {
            setFormError('Telegram username is required');
            return;
        }

        setSubmitting(true);
        setFormError('');

        try {
            await addChannel({
                name: formData.name.trim(),
                username: formData.username.trim(),
                description: formData.description.trim(),
                telegram_id: formData.telegram_id.trim()  // Pass telegram_id to store
            });
            setCreateDialogOpen(false);
            setFormData({ name: '', description: '', username: '', telegram_id: '' });
        } catch (err: any) {
            setFormError(err.message || 'Failed to create channel');
        } finally {
            setSubmitting(false);
        }
    };

    // Handle edit dialog
    const handleOpenEdit = (channel: Channel) => {
        setSelectedChannel(channel);
        setFormData({
            name: channel.name || '',
            description: channel.description || '',
            username: channel.username || '',
            telegram_id: channel.telegramId?.toString() || ''
        });
        setFormError('');
        setEditDialogOpen(true);
    };

    const handleEdit = async () => {
        if (!selectedChannel || !formData.name.trim()) {
            setFormError('Channel name is required');
            return;
        }

        setSubmitting(true);
        setFormError('');

        try {
            await updateChannel(selectedChannel.id, {
                name: formData.name.trim(),
                description: formData.description.trim(),
                username: formData.username.trim()
            });
            setEditDialogOpen(false);
            setSelectedChannel(null);
        } catch (err: any) {
            setFormError(err.message || 'Failed to update channel');
        } finally {
            setSubmitting(false);
        }
    };

    // Handle delete dialog
    const handleOpenDelete = (channel: Channel) => {
        setSelectedChannel(channel);
        setDeleteDialogOpen(true);
    };

    const handleDelete = async () => {
        if (!selectedChannel) return;

        setSubmitting(true);

        try {
            await deleteChannel(selectedChannel.id);
            setDeleteDialogOpen(false);
            setSelectedChannel(null);
        } catch (err: any) {
            console.error('Failed to delete channel:', err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleInputChange = (field: keyof ChannelFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({ ...prev, [field]: event.target.value }));
        if (formError) setFormError('');
    };

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

            {/* Statistics Overview Cards */}
            {statsLoading ? (
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    {[1, 2, 3, 4].map((i) => (
                        <Grid item xs={12} sm={6} md={3} key={i}>
                            <Card elevation={2}>
                                <CardContent>
                                    <Skeleton variant="text" width="60%" height={24} />
                                    <Skeleton variant="text" width="80%" height={48} sx={{ mt: 1 }} />
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : statistics ? (
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    {/* Total Channels */}
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={2}
                            sx={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                color: 'white',
                                transition: 'transform 0.2s',
                                '&:hover': { transform: 'translateY(-4px)' }
                            }}
                        >
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="h6" fontWeight={600}>
                                        Total Channels
                                    </Typography>
                                    <ChannelIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" fontWeight={700}>
                                    {statistics.aggregate.total_channels}
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                                    {statistics.aggregate.active_channels} active
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Total Subscribers */}
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={2}
                            sx={{
                                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                                color: 'white',
                                transition: 'transform 0.2s',
                                '&:hover': { transform: 'translateY(-4px)' }
                            }}
                        >
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="h6" fontWeight={600}>
                                        Total Subscribers
                                    </Typography>
                                    <PeopleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" fontWeight={700}>
                                    {(statistics.aggregate?.total_subscribers ?? 0).toLocaleString()}
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                                    Across all channels
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Total Posts */}
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={2}
                            sx={{
                                background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                                color: 'white',
                                transition: 'transform 0.2s',
                                '&:hover': { transform: 'translateY(-4px)' }
                            }}
                        >
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="h6" fontWeight={600}>
                                        Total Posts
                                    </Typography>
                                    <ArticleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" fontWeight={700}>
                                    {(statistics.aggregate?.total_posts ?? 0).toLocaleString()}
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                                    Published content
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Total Views */}
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={2}
                            sx={{
                                background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                                color: 'white',
                                transition: 'transform 0.2s',
                                '&:hover': { transform: 'translateY(-4px)' }
                            }}
                        >
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="h6" fontWeight={600}>
                                        Total Views
                                    </Typography>
                                    <VisibilityIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                                </Box>
                                <Typography variant="h3" fontWeight={700}>
                                    {(statistics.aggregate?.total_views ?? 0).toLocaleString()}
                                </Typography>
                                <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                                    Avg {(statistics.aggregate?.avg_views_per_post ?? 0).toLocaleString()} per post
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            ) : null}

            {/* Error Display */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
                    {error}
                </Alert>
            )}

            {/* Info Banner */}
            <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
                <strong>Note:</strong> To sync data from Telegram, make sure your bot is added as an administrator to each channel.
            </Alert>

            {/* Channels Grid */}
            {isLoading && channels.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress size={48} />
                </Box>
            ) : channels.length === 0 ? (
                <Paper sx={{ p: 6, textAlign: 'center' }}>
                    <ChannelIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                        No channels yet
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Get started by adding your first channel
                    </Typography>
                    <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}>
                        Add Your First Channel
                    </Button>
                </Paper>
            ) : (
                <Grid container spacing={3}>
                    {channels.map((channel) => (
                        <Grid item xs={12} sm={6} md={4} key={channel.id}>
                            <Card
                                elevation={2}
                                sx={{
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    transition: 'transform 0.2s, box-shadow 0.2s',
                                    '&:hover': {
                                        transform: 'translateY(-4px)',
                                        boxShadow: 4
                                    }
                                }}
                            >
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                                        <ChannelIcon sx={{ fontSize: 32, color: 'primary.main', mr: 1 }} />
                                        <Box sx={{ flexGrow: 1 }}>
                                            <Typography variant="h6" fontWeight={600} gutterBottom>
                                                {channel.name}
                                            </Typography>
                                            {channel.description && (
                                                <Typography variant="body2" color="text.secondary">
                                                    {channel.description}
                                                </Typography>
                                            )}
                                        </Box>
                                    </Box>

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

                                    {/* Enhanced Channel Statistics */}
                                    {(() => {
                                        const channelStats = statistics?.channels.find(s => s.id === Number(channel.id));
                                        if (!channelStats) {
                                            return (
                                                <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.100', borderRadius: 1 }}>
                                                    <Typography variant="caption" color="text.secondary">
                                                        No statistics available yet
                                                    </Typography>
                                                </Box>
                                            );
                                        }

                                        return (
                                            <Box sx={{ mt: 2 }}>
                                                {/* Statistics Grid */}
                                                <Grid container spacing={1}>
                                                    {/* Subscribers */}
                                                    <Grid item xs={6}>
                                                        <Paper sx={{ p: 1.5, bgcolor: 'primary.50', textAlign: 'center' }}>
                                                            <PeopleIcon sx={{ fontSize: 20, color: 'primary.main', mb: 0.5 }} />
                                                            <Typography variant="h6" fontWeight={700} color="primary.main">
                                                                {(channelStats.subscriber_count ?? 0).toLocaleString()}
                                                            </Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                Subscribers
                                                            </Typography>
                                                        </Paper>
                                                    </Grid>

                                                    {/* Posts */}
                                                    <Grid item xs={6}>
                                                        <Paper sx={{ p: 1.5, bgcolor: 'info.50', textAlign: 'center' }}>
                                                            <ArticleIcon sx={{ fontSize: 20, color: 'info.main', mb: 0.5 }} />
                                                            <Typography variant="h6" fontWeight={700} color="info.main">
                                                                {(channelStats.post_count ?? 0).toLocaleString()}
                                                            </Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                Posts
                                                            </Typography>
                                                        </Paper>
                                                    </Grid>

                                                    {/* Total Views */}
                                                    <Grid item xs={6}>
                                                        <Paper sx={{ p: 1.5, bgcolor: 'success.50', textAlign: 'center' }}>
                                                            <VisibilityIcon sx={{ fontSize: 20, color: 'success.main', mb: 0.5 }} />
                                                            <Typography variant="h6" fontWeight={700} color="success.main">
                                                                {(channelStats.total_views ?? 0).toLocaleString()}
                                                            </Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                Total Views
                                                            </Typography>
                                                        </Paper>
                                                    </Grid>

                                                    {/* Avg Views */}
                                                    <Grid item xs={6}>
                                                        <Paper sx={{ p: 1.5, bgcolor: 'warning.50', textAlign: 'center' }}>
                                                            <TrendingUpIcon sx={{ fontSize: 20, color: 'warning.main', mb: 0.5 }} />
                                                            <Typography variant="h6" fontWeight={700} color="warning.main">
                                                                {(channelStats.avg_views_per_post ?? 0).toLocaleString()}
                                                            </Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                Avg Views
                                                            </Typography>
                                                        </Paper>
                                                    </Grid>
                                                </Grid>

                                                {/* Latest Post Date */}
                                                {channelStats.latest_post_date && (
                                                    <Box sx={{ mt: 1.5, p: 1, bgcolor: 'grey.50', borderRadius: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                        <CheckCircleIcon sx={{ fontSize: 16, color: 'success.main' }} />
                                                        <Typography variant="caption" color="text.secondary">
                                                            Latest post: {new Date(channelStats.latest_post_date).toLocaleDateString()}
                                                        </Typography>
                                                    </Box>
                                                )}
                                            </Box>
                                        );
                                    })()}
                                </CardContent>

                                <Divider />

                                {/* MTProto Toggle Section - FULL WIDTH FOR COMFORT */}
                                <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
                                    <ChannelMTProtoToggle
                                        channelId={channel.id}
                                        channelName={channel.name}
                                        compact
                                    />
                                </Box>

                                <Divider />

                                <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
                                    <Tooltip title="Edit channel">
                                        <IconButton
                                            size="small"
                                            onClick={() => handleOpenEdit(channel)}
                                            color="primary"
                                        >
                                            <EditIcon fontSize="small" />
                                        </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Delete channel">
                                        <IconButton
                                            size="small"
                                            onClick={() => handleOpenDelete(channel)}
                                            color="error"
                                        >
                                            <DeleteIcon fontSize="small" />
                                        </IconButton>
                                    </Tooltip>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Add Existing Channel Dialog */}
            <Dialog open={createDialogOpen} onClose={() => !submitting && setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AddIcon />
                        Add Existing Telegram Channel
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                        <strong>Important:</strong> This adds an existing Telegram channel to your analytics system.
                        It does NOT create a new channel on Telegram. The channel must already exist.
                    </Alert>

                    {formError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {formError}
                        </Alert>
                    )}

                    <TextField
                        autoFocus
                        margin="dense"
                        label="Channel Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.name}
                        onChange={handleInputChange('name')}
                        disabled={submitting}
                        required
                        helperText="Friendly name for your reference (can be different from Telegram channel name)"
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        margin="dense"
                        label="Description"
                        type="text"
                        fullWidth
                        variant="outlined"
                        multiline
                        rows={3}
                        value={formData.description}
                        onChange={handleInputChange('description')}
                        disabled={submitting}
                        placeholder="Optional notes about this channel"
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        margin="dense"
                        label="Telegram Username"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.username}
                        onChange={handleInputChange('username')}
                        disabled={submitting}
                        required
                        helperText="Channel username (e.g., @abclegacynews)"
                        placeholder="@mychannel"
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        margin="dense"
                        label="Telegram Channel ID (Optional)"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.telegram_id}
                        onChange={handleInputChange('telegram_id')}
                        disabled={submitting}
                        helperText="Numeric channel ID from Telegram (e.g., -1082618876654). Leave empty to auto-detect."
                        placeholder="-1001234567890"
                        sx={{ mb: 1 }}
                    />

                    <Alert severity="info" sx={{ mt: 1, mb: 2 }}>
                        <strong>How to get Channel ID:</strong>
                        <ol style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                            <li>Forward a message from the channel to <strong>@userinfobot</strong></li>
                            <li>The bot will show you the Channel ID (e.g., -1082618876654)</li>
                            <li>Paste it in the field above</li>
                        </ol>
                    </Alert>

                    <Alert severity="info" sx={{ mt: 0 }}>
                        <strong>Requirements for Analytics:</strong>
                        <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                            <li>The channel must already exist on Telegram</li>
                            <li>Your bot must be added as an administrator to the channel</li>
                            <li>This will track/monitor the channel for analytics only</li>
                        </ul>
                    </Alert>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateDialogOpen(false)} disabled={submitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleCreate}
                        variant="contained"
                        disabled={submitting || !formData.name.trim() || !formData.username.trim()}
                    >
                        {submitting ? <CircularProgress size={24} /> : 'Add Channel'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Edit Channel Dialog */}
            <Dialog open={editDialogOpen} onClose={() => !submitting && setEditDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <EditIcon />
                        Edit Channel
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {formError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {formError}
                        </Alert>
                    )}

                    <TextField
                        autoFocus
                        margin="dense"
                        label="Channel Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.name}
                        onChange={handleInputChange('name')}
                        disabled={submitting}
                        required
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        margin="dense"
                        label="Description"
                        type="text"
                        fullWidth
                        variant="outlined"
                        multiline
                        rows={3}
                        value={formData.description}
                        onChange={handleInputChange('description')}
                        disabled={submitting}
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        margin="dense"
                        label="Telegram Username (Optional)"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.username}
                        onChange={handleInputChange('username')}
                        disabled={submitting}
                        helperText="Telegram channel username (e.g., @mychannel)"
                        placeholder="@mychannel"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setEditDialogOpen(false)} disabled={submitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleEdit}
                        variant="contained"
                        disabled={submitting || !formData.name.trim()}
                    >
                        {submitting ? <CircularProgress size={24} /> : 'Save Changes'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog open={deleteDialogOpen} onClose={() => !submitting && setDeleteDialogOpen(false)}>
                <DialogTitle>Delete Channel?</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete <strong>{selectedChannel?.name}</strong>?
                    </Typography>
                    <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                        This action cannot be undone. All analytics data for this channel will be lost.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)} disabled={submitting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleDelete}
                        color="error"
                        variant="contained"
                        disabled={submitting}
                    >
                        {submitting ? <CircularProgress size={24} /> : 'Delete'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default ChannelsManagementPage;
