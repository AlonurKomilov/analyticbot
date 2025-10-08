import React, { useState } from 'react';
import {
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Box,
    Typography,
    IconButton,
    Alert,
    Snackbar,
    Chip,
    CircularProgress
} from '@mui/material';
import {
    Share as ShareIcon,
    ContentCopy as CopyIcon,
    Close as CloseIcon,
    AccessTime as TimeIcon,
    Link as LinkIcon
} from '@mui/icons-material';
import { analyticsService } from '../../services/analyticsService.js';
import { useDataSource } from '../../hooks/useDataSource.js';

/**
 * Share Button Component for Analytics Reports
 * Updated to use new mock/real data source architecture
 */
const ShareButton = ({
    channelId = 'demo_channel',
    dataType = 'engagement',
    disabled = false,
    size = 'medium',
    ...props
}) => {
    const { dataSource, isUsingRealAPI } = useDataSource();
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [shareLink, setShareLink] = useState(null);
    const [ttl, setTtl] = useState('24h');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const ttlOptions = [
        { value: '1h', label: '1 Hour' },
        { value: '6h', label: '6 Hours' },
        { value: '24h', label: '24 Hours' },
        { value: '3d', label: '3 Days' },
        { value: '7d', label: '7 Days' }
    ];

    const handleOpen = () => {
        setOpen(true);
        setShareLink(null);
        setError(null);
    };

    const handleClose = () => {
        setOpen(false);
        setShareLink(null);
        setError(null);
    };

    const handleCreateShare = async () => {
        setLoading(true);
        setError(null);

        try {
            const dataService = dataServiceFactory.getService(dataSource);

            if (isUsingRealAPI) {
                // Use real API
                const response = await dataService.createShareLink(dataType, channelId, ttl);
                if (response.share_url) {
                    setShareLink(response);
                    setSuccess('Share link created successfully!');
                } else {
                    throw new Error('Invalid response format');
                }
            } else {
                // Use mock service for demonstration
                const mockResponse = {
                    share_url: `https://analyticbot.com/share/mock-${channelId}-${dataType}-${Date.now()}`,
                    expires_at: new Date(Date.now() + (ttl === '1h' ? 3600000 : ttl === '6h' ? 21600000 : 86400000)).toISOString(),
                    share_id: `mock-share-${Date.now()}`,
                    data_type: dataType,
                    channel_id: channelId
                };
                setShareLink(mockResponse);
                setSuccess('Mock share link created successfully! (Demo mode)');
            }
        } catch (err) {
            console.error('Share creation failed:', err);
            setError(`Failed to create share link: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleCopyLink = async () => {
        if (!shareLink?.share_url) return;

        try {
            await navigator.clipboard.writeText(shareLink.share_url);
            setSuccess('Link copied to clipboard!');
        } catch (err) {
            console.error('Copy failed:', err);
            setError('Failed to copy link to clipboard');
        }
    };

    const formatExpiryTime = (expiresAt) => {
        if (!expiresAt) return 'No expiration';

        const date = new Date(expiresAt);
        const now = new Date();
        const diffMs = date.getTime() - now.getTime();

        if (diffMs <= 0) return 'Expired';

        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

        if (diffHours > 0) {
            return `Expires in ${diffHours}h ${diffMinutes}m`;
        } else {
            return `Expires in ${diffMinutes}m`;
        }
    };

    return (
        <>
            <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                onClick={handleOpen}
                disabled={disabled}
                size={size}
                aria-label="Share analytics report"
                {...props}
            >
                Share
            </Button>

            <Dialog
                open={open}
                onClose={handleClose}
                maxWidth="sm"
                fullWidth
                aria-labelledby="share-dialog-title"
            >
                <DialogTitle id="share-dialog-title">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ShareIcon />
                        Share Analytics Report
                        <IconButton
                            aria-label="close"
                            onClick={handleClose}
                            sx={{ ml: 'auto' }}
                        >
                            <CloseIcon />
                        </IconButton>
                    </Box>
                </DialogTitle>

                <DialogContent dividers>
                    {!shareLink ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                                Create a shareable link for your analytics report.
                                The link will expire after the selected time period.
                            </Typography>

                            <Box sx={{ display: 'flex', gap: 2 }}>
                                <Chip
                                    icon={<LinkIcon />}
                                    label={`Report: ${dataType}`}
                                    color="primary"
                                    variant="outlined"
                                />
                                <Chip
                                    label={`Channel: ${channelId}`}
                                    color="secondary"
                                    variant="outlined"
                                />
                            </Box>

                            <FormControl fullWidth>
                                <InputLabel>Link Expiration</InputLabel>
                                <Select
                                    value={ttl}
                                    onChange={(e) => setTtl(e.target.value)}
                                    label="Link Expiration"
                                    disabled={loading}
                                >
                                    {ttlOptions.map((option) => (
                                        <MenuItem key={option.value} value={option.value}>
                                            {option.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            {error && (
                                <Alert severity="error" onClose={() => setError(null)}>
                                    {error}
                                </Alert>
                            )}
                        </Box>
                    ) : (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <Alert severity="success">
                                Share link created successfully!
                            </Alert>

                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                <Typography variant="subtitle2">
                                    Share Link:
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    <TextField
                                        fullWidth
                                        value={shareLink.share_url}
                                        variant="outlined"
                                        size="small"
                                        InputProps={{
                                            readOnly: true,
                                        }}
                                        onClick={(e) => e.target.select()}
                                    />
                                    <Button
                                        variant="contained"
                                        onClick={handleCopyLink}
                                        startIcon={<CopyIcon />}
                                        size="small"
                                    >
                                        Copy
                                    </Button>
                                </Box>
                            </Box>

                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <TimeIcon fontSize="small" color="action" />
                                <Typography variant="body2" color="text.secondary">
                                    {formatExpiryTime(shareLink.expires_at)}
                                </Typography>
                            </Box>

                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                <Chip
                                    size="small"
                                    label={`Token: ${shareLink.token?.substring(0, 8)}...`}
                                    variant="outlined"
                                />
                                <Chip
                                    size="small"
                                    label={`Access Count: ${shareLink.access_count || 0}`}
                                    variant="outlined"
                                />
                            </Box>
                        </Box>
                    )}
                </DialogContent>

                <DialogActions>
                    <Button onClick={handleClose}>
                        {shareLink ? 'Close' : 'Cancel'}
                    </Button>
                    {!shareLink && (
                        <Button
                            onClick={handleCreateShare}
                            variant="contained"
                            disabled={loading}
                            startIcon={loading ? <CircularProgress size={16} /> : <ShareIcon />}
                        >
                            {loading ? 'Creating...' : 'Create Share Link'}
                        </Button>
                    )}
                </DialogActions>
            </Dialog>

            {/* Success Notification */}
            <Snackbar
                open={!!success}
                autoHideDuration={4000}
                onClose={() => setSuccess(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert
                    onClose={() => setSuccess(null)}
                    severity="success"
                    variant="filled"
                >
                    {success}
                </Alert>
            </Snackbar>

            {/* Error Notification */}
            <Snackbar
                open={!!error}
                autoHideDuration={6000}
                onClose={() => setError(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert
                    onClose={() => setError(null)}
                    severity="error"
                    variant="filled"
                >
                    {error}
                </Alert>
            </Snackbar>
        </>
    );
};

export default ShareButton;
