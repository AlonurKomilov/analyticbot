import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Alert,
    Box,
    Chip,
    Stack,
    CircularProgress
} from '@mui/material';
import {
    Warning as WarningIcon,
    CloudOff as OfflineIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

/**
 * ApiFailureDialog - User Prompt for Data Source Fallback
 *
 * This component appears when the API fails and asks the user
 * for explicit permission before switching to mock data.
 *
 * Features:
 * - Clear explanation of the issue
 * - Options to retry or switch to demo mode
 * - No automatic switching without user consent
 */
const ApiFailureDialog = ({
    open,
    onClose,
    onRetry,
    onSwitchToMock,
    error,
    isRetrying = false
}) => {
    const [isProcessing, setIsProcessing] = useState(false);

    const handleSwitchToMock = async () => {
        setIsProcessing(true);
        try {
            await onSwitchToMock();
            onClose();
        } catch (err) {
            console.error('Error switching to mock data:', err);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleRetry = async () => {
        setIsProcessing(true);
        try {
            await onRetry();
            onClose();
        } catch (err) {
            // Keep dialog open if retry fails
            console.error('Retry failed:', err);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <Dialog
            open={open}
            onClose={!isProcessing ? onClose : undefined}
            maxWidth="sm"
            fullWidth
            disableEscapeKeyDown={isProcessing}
        >
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <WarningIcon color="warning" />
                API Connection Failed
            </DialogTitle>

            <DialogContent>
                <Stack spacing={3}>
                    <Alert severity="warning" icon={<OfflineIcon />}>
                        Unable to connect to the analytics API server.
                    </Alert>

                    <Box>
                        <Typography variant="body1" gutterBottom>
                            The system cannot reach the analytics API. This might be due to:
                        </Typography>
                        <Typography variant="body2" color="text.secondary" component="div">
                            • Network connectivity issues<br />
                            • Server maintenance<br />
                            • Incorrect API configuration<br />
                            • Authentication problems
                        </Typography>
                    </Box>

                    {error && (
                        <Box>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                Technical details:
                            </Typography>
                            <Box
                                sx={{
                                    p: 2,
                                    bgcolor: 'grey.100',
                                    borderRadius: 1,
                                    fontFamily: 'monospace',
                                    fontSize: '0.875rem',
                                    color: 'error.main'
                                }}
                            >
                                {error.message || error.toString()}
                            </Box>
                        </Box>
                    )}

                    <Box>
                        <Typography variant="body1" gutterBottom>
                            You can choose to:
                        </Typography>
                        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                            <Chip
                                icon={<CircularProgress size={16} />}
                                label="Retry Connection"
                                variant="outlined"
                                size="small"
                                color="primary"
                            />
                            <Chip
                                icon={<SettingsIcon />}
                                label="Use Demo Data"
                                variant="outlined"
                                size="small"
                                color="secondary"
                            />
                        </Stack>
                    </Box>
                </Stack>
            </DialogContent>

            <DialogActions sx={{ p: 3 }}>
                <Button
                    onClick={onClose}
                    disabled={isProcessing}
                    color="inherit"
                >
                    Cancel
                </Button>

                <Button
                    onClick={handleRetry}
                    disabled={isProcessing || isRetrying}
                    variant="outlined"
                    color="primary"
                    startIcon={isRetrying ? <CircularProgress size={16} /> : null}
                >
                    {isRetrying ? 'Retrying...' : 'Try Again'}
                </Button>

                <Button
                    onClick={handleSwitchToMock}
                    disabled={isProcessing}
                    variant="contained"
                    color="secondary"
                    startIcon={isProcessing ? <CircularProgress size={16} /> : <SettingsIcon />}
                >
                    {isProcessing ? 'Switching...' : 'Use Demo Data'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ApiFailureDialog;
