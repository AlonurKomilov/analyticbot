/**
 * 📺 Channel Selector Component
 *
 * Professional channel selection component with search, creation, and management.
 * Replaces hardcoded demo_channel with dynamic user channel selection.
 */

import React, { useState } from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    Button,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton,
    Typography,
    Alert,
    CircularProgress,
    Tooltip,
    InputAdornment,
    SelectChangeEvent
} from '@mui/material';
import {
    Add as AddIcon,
    Search as SearchIcon,
    Tv as ChannelIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { useUserChannels } from '../hooks/useUserChannels';

interface ChannelSelectorProps {
    onChannelChange?: ((channel: any) => void) | null;
    showCreateButton?: boolean;
    showRefreshButton?: boolean;
    size?: 'small' | 'medium';
    variant?: 'outlined' | 'filled' | 'standard';
    fullWidth?: boolean;
}

interface NewChannelData {
    name: string;
    description: string;
    telegram_channel_id: string;
}

const ChannelSelector: React.FC<ChannelSelectorProps> = ({
    onChannelChange = null,
    showCreateButton = true,
    showRefreshButton = true,
    size = 'medium',
    variant = 'outlined',
    fullWidth = true
}) => {
    const {
        channels,
        selectedChannel,
        loading,
        error,
        fetchChannels,
        createChannel,
        selectChannel,
        isAuthenticated
    } = useUserChannels({
        onChannelChange
    });

    const [createDialogOpen, setCreateDialogOpen] = useState<boolean>(false);
    const [newChannelData, setNewChannelData] = useState<NewChannelData>({
        name: '',
        description: '',
        telegram_channel_id: ''
    });
    const [createError, setCreateError] = useState<string>('');
    const [creating, setCreating] = useState<boolean>(false);
    const [searchTerm, setSearchTerm] = useState<string>('');

    // Filter channels based on search term
    const filteredChannels = channels.filter(channel =>
        !searchTerm ||
        channel.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        channel.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Handle channel selection
    const handleChannelSelect = (event: SelectChangeEvent<string>): void => {
        const channelId = event.target.value;
        const channel = channels.find(ch => String(ch.id) === channelId);
        if (channel) {
            selectChannel(channel);
        }
    };

    // Handle create channel dialog
    const handleCreateChannel = async (): Promise<void> => {
        if (!newChannelData.name.trim()) {
            setCreateError('Channel name is required');
            return;
        }

        setCreating(true);
        setCreateError('');

        try {
            await createChannel({
                name: newChannelData.name.trim(),
                description: newChannelData.description.trim(),
                telegram_channel_id: newChannelData.telegram_channel_id.trim() || null
            });

            // Reset form and close dialog
            setNewChannelData({
                name: '',
                description: '',
                telegram_channel_id: ''
            });
            setCreateDialogOpen(false);
        } catch (err: any) {
            setCreateError(err.message || 'Failed to create channel');
        } finally {
            setCreating(false);
        }
    };

    // Handle create dialog input changes
    const handleCreateInputChange = (field: keyof NewChannelData) => (event: React.ChangeEvent<HTMLInputElement>): void => {
        setNewChannelData(prev => ({
            ...prev,
            [field]: event.target.value
        }));
        // Clear error when user starts typing
        if (createError) {
            setCreateError('');
        }
    };

    // Don't render if not authenticated
    if (!isAuthenticated) {
        return (
            <Alert severity="warning" sx={{ my: 2 }}>
                Please log in to select channels
            </Alert>
        );
    }

    return (
        <Box sx={{ width: fullWidth ? '100%' : 'auto' }}>
            {/* Error Display */}
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Channel Selection Section */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {/* Main Channel Selector */}
                <FormControl
                    variant={variant}
                    size={size}
                    sx={{
                        flex: 1,
                        minWidth: 200
                    }}
                    disabled={loading}
                >
                    <InputLabel id="channel-selector-label">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <ChannelIcon fontSize="small" />
                            Channel
                        </Box>
                    </InputLabel>
                    <Select
                        labelId="channel-selector-label"
                        value={selectedChannel?.id ? String(selectedChannel.id) : ''}
                        onChange={handleChannelSelect}
                        label="Channel"
                        renderValue={(selected) => {
                            const channel = channels.find(ch => String(ch.id) === selected);
                            return channel ? (
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="body2">
                                        {channel.name}
                                    </Typography>
                                    <Chip
                                        label={`ID: ${channel.id}`}
                                        size="small"
                                        variant="outlined"
                                        sx={{ height: 20 }}
                                    />
                                </Box>
                            ) : 'Select a channel';
                        }}
                    >
                        {/* Search Field */}
                        {channels.length > 5 && (
                            <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
                                <TextField
                                    size="small"
                                    placeholder="Search channels..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <SearchIcon fontSize="small" />
                                            </InputAdornment>
                                        )
                                    }}
                                    onClick={(e) => e.stopPropagation()}
                                    fullWidth
                                />
                            </Box>
                        )}

                        {/* Channel Options */}
                        {filteredChannels.length === 0 && searchTerm ? (
                            <MenuItem disabled>
                                <Typography variant="body2" color="text.secondary">
                                    No channels found matching "{searchTerm}"
                                </Typography>
                            </MenuItem>
                        ) : filteredChannels.length === 0 ? (
                            <MenuItem disabled>
                                <Typography variant="body2" color="text.secondary">
                                    No channels available
                                </Typography>
                            </MenuItem>
                        ) : (
                            filteredChannels.map((channel) => (
                                <MenuItem key={channel.id} value={String(channel.id)}>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '100%' }}>
                                        <Typography variant="body2" fontWeight="medium">
                                            {channel.name}
                                        </Typography>
                                        {channel.description && (
                                            <Typography variant="caption" color="text.secondary">
                                                {channel.description}
                                            </Typography>
                                        )}
                                        <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                                            <Chip
                                                label={`ID: ${channel.id}`}
                                                size="small"
                                                variant="outlined"
                                                sx={{ height: 16, fontSize: '0.65rem' }}
                                            />
                                            {channel.telegram_channel_id && (
                                                <Chip
                                                    label={`TG: ${channel.telegram_channel_id}`}
                                                    size="small"
                                                    variant="outlined"
                                                    sx={{ height: 16, fontSize: '0.65rem' }}
                                                />
                                            )}
                                        </Box>
                                    </Box>
                                </MenuItem>
                            ))
                        )}
                    </Select>
                </FormControl>

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                    {/* Refresh Button */}
                    {showRefreshButton && (
                        <Tooltip title="Refresh channels">
                            <IconButton
                                onClick={fetchChannels}
                                disabled={loading}
                                size={size}
                            >
                                {loading ? (
                                    <CircularProgress size={20} />
                                ) : (
                                    <RefreshIcon />
                                )}
                            </IconButton>
                        </Tooltip>
                    )}

                    {/* Create Channel Button */}
                    {showCreateButton && (
                        <Tooltip title="Create new channel">
                            <IconButton
                                onClick={() => setCreateDialogOpen(true)}
                                color="primary"
                                size={size}
                            >
                                <AddIcon />
                            </IconButton>
                        </Tooltip>
                    )}
                </Box>
            </Box>

            {/* Selected Channel Info */}
            {selectedChannel && (
                <Box sx={{ mt: 1, p: 1, backgroundColor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                        Selected: {selectedChannel.name}
                        {selectedChannel.description && ` - ${selectedChannel.description}`}
                    </Typography>
                </Box>
            )}

            {/* Create Channel Dialog */}
            <Dialog
                open={createDialogOpen}
                onClose={() => !creating && setCreateDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AddIcon />
                        Create New Channel
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {createError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {createError}
                        </Alert>
                    )}

                    <TextField
                        autoFocus
                        margin="dense"
                        label="Channel Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={newChannelData.name}
                        onChange={handleCreateInputChange('name')}
                        disabled={creating}
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
                        value={newChannelData.description}
                        onChange={handleCreateInputChange('description')}
                        disabled={creating}
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        margin="dense"
                        label="Telegram Channel ID (Optional)"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={newChannelData.telegram_channel_id}
                        onChange={handleCreateInputChange('telegram_channel_id')}
                        disabled={creating}
                        helperText="Link this channel to a Telegram channel for data sync"
                    />
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={() => setCreateDialogOpen(false)}
                        disabled={creating}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleCreateChannel}
                        variant="contained"
                        disabled={creating || !newChannelData.name.trim()}
                    >
                        {creating ? (
                            <>
                                <CircularProgress size={16} sx={{ mr: 1 }} />
                                Creating...
                            </>
                        ) : (
                            'Create Channel'
                        )}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ChannelSelector;
