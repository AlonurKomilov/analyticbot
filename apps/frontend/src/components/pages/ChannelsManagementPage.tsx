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
    Divider
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Refresh as RefreshIcon,
    Tv as ChannelIcon,
    TrendingUp as TrendingUpIcon,
    Info as InfoIcon
} from '@mui/icons-material';
import { useChannelStore } from '@/stores';
import { Channel } from '@/types';

interface ChannelFormData {
    name: string;
    description: string;
    username: string;
}

const ChannelsManagementPage: React.FC = () => {
    const { channels, isLoading, error, fetchChannels, addChannel, updateChannel, deleteChannel } = useChannelStore();
    
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
    
    const [formData, setFormData] = useState<ChannelFormData>({
        name: '',
        description: '',
        username: ''
    });
    const [formError, setFormError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    // Load channels on mount
    useEffect(() => {
        fetchChannels();
    }, [fetchChannels]);

    // Handle create dialog
    const handleOpenCreate = () => {
        setFormData({ name: '', description: '', username: '' });
        setFormError('');
        setCreateDialogOpen(true);
    };

    const handleCreate = async () => {
        if (!formData.name.trim()) {
            setFormError('Channel name is required');
            return;
        }

        setSubmitting(true);
        setFormError('');

        try {
            await addChannel({
                name: formData.name.trim(),
                username: formData.username.trim(),
                description: formData.description.trim()
            });
            setCreateDialogOpen(false);
            setFormData({ name: '', description: '', username: '' });
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
            username: channel.username || ''
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
                            Channels Management
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Manage your Telegram channels and track their performance
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Tooltip title="Refresh channels">
                            <span>
                                <IconButton onClick={fetchChannels} disabled={isLoading}>
                                    {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
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

                                    {/* Channel Stats (if available) */}
                                    {channel.metrics && (
                                        <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main' }} />
                                                <Typography variant="caption" color="text.secondary">
                                                    {channel.metrics.totalPosts || 0} posts
                                                    {channel.metrics.totalViews && ` • ${channel.metrics.totalViews} views`}
                                                </Typography>
                                            </Box>
                                        </Box>
                                    )}
                                </CardContent>

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

            {/* Create Channel Dialog */}
            <Dialog open={createDialogOpen} onClose={() => !submitting && setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AddIcon />
                        Add New Channel
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
                    <Button onClick={() => setCreateDialogOpen(false)} disabled={submitting}>
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleCreate} 
                        variant="contained" 
                        disabled={submitting || !formData.name.trim()}
                    >
                        {submitting ? <CircularProgress size={24} /> : 'Create Channel'}
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
