import React, { useState, useCallback, useMemo } from 'react';
import { Box, TextField, Typography, Alert, CircularProgress } from '@mui/material';
import { useChannelStore } from '@/stores';
import UnifiedButton from './common/UnifiedButton.jsx';

interface Status {
    success: boolean;
    message: string;
}

const AddChannel: React.FC = React.memo(() => {
    const { addChannel, isLoading, error } = useChannelStore();
    const [channelName, setChannelName] = useState<string>('');
    const [status, setStatus] = useState<Status>({ success: false, message: '' });
    const [validationError, setValidationError] = useState<string>('');

    const validateChannelName = useCallback((name: string): boolean => {
        if (!name.trim()) {
            setValidationError('Channel name is required');
            return false;
        }
        if (!name.startsWith('@')) {
            setValidationError('Channel name must start with @');
            return false;
        }
        if (name.length < 4) {
            setValidationError('Channel name must be at least 4 characters long');
            return false;
        }
        if (!/^@[a-zA-Z0-9_]+$/.test(name)) {
            setValidationError('Channel name can only contain letters, numbers, and underscores');
            return false;
        }
        setValidationError('');
        return true;
    }, []);

    const handleChannelNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setChannelName(value);
        setStatus({ success: false, message: '' });

        if (value) {
            validateChannelName(value);
        } else {
            setValidationError('');
        }
    }, [validateChannelName]);

    const handleAdd = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateChannelName(channelName)) {
            return;
        }

        try {
            setStatus({ success: false, message: '' });
            await addChannel({
                name: channelName.trim(),
                username: channelName.trim()
            });
            setChannelName('');
            setValidationError('');
            setStatus({ success: true, message: 'Channel added successfully!' });
        } catch (error: any) {
            setStatus({
                success: false,
                message: error.message || 'Unable to add channel. Please check the channel name and try again.'
            });
        }
    }, [channelName, validateChannelName, addChannel]);

    const loading = isLoading;
    const canSubmit = useMemo(
        () => channelName.trim() && !validationError && !loading,
        [channelName, validationError, loading]
    );

    return (
        <Box
            component="form"
            onSubmit={handleAdd}
            sx={{ mb: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: '8px' }}
            role="form"
            aria-labelledby="add-channel-title"
        >
            <Typography variant="h2" id="add-channel-title" sx={{ fontSize: '1.25rem', mb: 2 }}>
                Add New Channel
            </Typography>

            {/* Live region for form status */}
            <div aria-live="polite" aria-atomic="true" className="sr-only">
                {loading && "Adding channel..."}
                {status.success && "Channel added successfully"}
                {(error || status.message) && !status.success && `Error: ${error || status.message}`}
            </div>

            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    size="small"
                    label="Channel Username"
                    placeholder="@channel_username"
                    value={channelName}
                    onChange={handleChannelNameChange}
                    disabled={loading}
                    error={!!validationError}
                    helperText={validationError || "Enter the channel username starting with @"}
                    aria-describedby={validationError ? "channel-error" : "channel-help"}
                    id="channel-name"
                    autoComplete="username"
                    inputProps={{
                        'aria-label': 'Channel username',
                        'aria-required': 'true',
                        maxLength: 50
                    }}
                </TextField>
                <UnifiedButton
                    type="submit"
                    disabled={!canSubmit}
                    sx={{
                        minWidth: '100px',
                        '&:focus-visible': {
                            outline: '2px solid #fff',
                            outlineOffset: '2px'
                        }
                    }}
                    aria-describedby="add-button-help"
                >
                    {loading ? (
                        <>
                            <CircularProgress size={16} sx={{ mr: 1 }} color="inherit" aria-hidden="true" />
                            Adding...
                        </>
                    ) : (
                        'Add Channel'
                    )}
                </UnifiedButton>
            </Box>

            {validationError && (
                <Typography
                    variant="caption"
                    color="error"
                    id="channel-error"
                    role="alert"
                    sx={{ display: 'block', mb: 1 }}
                >
                    {validationError}
                </Typography>
            )}

            {!canSubmit && !validationError && channelName && (
                <Typography
                    variant="caption"
                    color="text.secondary"
                    id="add-button-help"
                    sx={{ display: 'block', mb: 1 }}
                >
                    Please enter a valid channel username to continue
                </Typography>
            )}

            {(status.message || error) && !loading && (
                <Alert
                    severity={status.success && !error ? 'success' : 'error'}
                    sx={{ mt: 2 }}
                    role="alert"
                >
                    {status.success && !error ? (
                        <strong>Success!</strong>
                    ) : (
                        <strong>Unable to add channel:</strong>
                    )} {error || status.message}
                </Alert>
            )}

            <Typography
                variant="caption"
                color="text.secondary"
                id="channel-help"
                sx={{ display: 'block', mt: 1 }}
            >
                Example: @myawesomechannel • Make sure the bot is added as an admin to the channel
            </Typography>
        </Box>
    );
});

AddChannel.displayName = 'AddChannel';

export default AddChannel;
