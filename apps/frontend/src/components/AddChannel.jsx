import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';
import { useAppStore } from '../store/appStore.js';

const AddChannel = () => {
    const { addChannel, isLoading, getError } = useAppStore();
    const [channelName, setChannelName] = useState('');
    const [status, setStatus] = useState({ success: false, message: '' });

    const handleAdd = async () => {
        if (channelName.trim()) {
            try {
                setStatus({ success: false, message: '' });
                await addChannel(channelName.trim());
                setChannelName('');
                setStatus({ success: true, message: 'Channel added successfully!' });
            } catch (error) {
                setStatus({ success: false, message: error.message || 'Failed to add channel' });
            }
        }
    };

    const loading = isLoading('addChannel');
    const error = getError('addChannel');

    return (
        <Box sx={{ mb: 3, p: 2, border: '1px solid #30363d', borderRadius: '6px' }}>
            <Typography variant="h6" gutterBottom>Add New Channel</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    size="small"
                    placeholder="@channel_username"
                    value={channelName}
                    onChange={(e) => setChannelName(e.target.value)}
                    disabled={loading}
                />
                <Button
                    variant="contained"
                    onClick={handleAdd}
                    disabled={loading}
                    sx={{ minWidth: '80px' }}
                >
                    {loading ? <CircularProgress size={24} color="inherit" /> : 'Add'}
                </Button>
            </Box>
            {(status.message || error) && !loading && (
                <Alert severity={status.success && !error ? 'success' : 'error'} sx={{ mt: 2 }}>
                    {error || status.message}
                </Alert>
            )}
        </Box>
    );
};

export default AddChannel;
