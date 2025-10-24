/**
 * Share Link Manager Component
 * 
 * UI for creating and managing share links.
 * Integrates with sharingService.ts
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Alert,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    IconButton,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Tooltip
} from '@mui/material';
import {
    Share as ShareIcon,
    ContentCopy as CopyIcon,
    Delete as DeleteIcon,
    Link as LinkIcon,
    AccessTime as TimeIcon,
    Visibility as ViewsIcon,
    Add as AddIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import {
    sharingService,
    type ShareListItem,
    type TTLOption
} from '@/services/sharingService';

export interface ShareLinkManagerProps {
    channelId?: string;
}

const ShareLinkManager: React.FC<ShareLinkManagerProps> = ({ channelId }) => {
    const [shareLinks, setShareLinks] = useState<ShareListItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Create Share Link State
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [reportType, setReportType] = useState<string>('overview');
    const [ttl, setTTL] = useState<TTLOption>('7d');
    const [format, setFormat] = useState<'csv' | 'png'>('csv');

    useEffect(() => {
        if (channelId) {
            loadShareLinks();
        }
    }, [channelId]);

    const loadShareLinks = async () => {
        if (!channelId) return;

        setLoading(true);
        setError(null);

        try {
            const links = await sharingService.getChannelShareLinks(channelId);
            setShareLinks(links);
        } catch (err: any) {
            setError(err.message || 'Failed to load share links');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateShareLink = async () => {
        if (!channelId) {
            setError('Channel ID is required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await sharingService.createShareLink(
                reportType,
                channelId,
                ttl,
                format
            );

            setSuccess(`Share link created! Valid for ${ttl}`);
            setCreateDialogOpen(false);
            await loadShareLinks();

            // Auto-copy to clipboard
            copyToClipboard(response.share_url);
        } catch (err: any) {
            setError(err.message || 'Failed to create share link');
        } finally {
            setLoading(false);
        }
    };

    const handleRevokeLink = async (token: string) => {
        if (!window.confirm('Are you sure you want to revoke this share link?')) {
            return;
        }

        setLoading(true);
        setError(null);

        try {
            await sharingService.revokeShareLink(token);
            setSuccess('Share link revoked successfully');
            await loadShareLinks();
        } catch (err: any) {
            setError(err.message || 'Failed to revoke share link');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setSuccess('Link copied to clipboard!');
        setTimeout(() => setSuccess(null), 2000);
    };

    const formatTTL = (ttl: string): string => {
        const map: Record<string, string> = {
            '1h': '1 hour',
            '6h': '6 hours',
            '24h': '24 hours',
            '3d': '3 days',
            '7d': '7 days',
            '30d': '30 days'
        };
        return map[ttl] || ttl;
    };

    const isExpired = (expiresAt: string): boolean => {
        return new Date(expiresAt) < new Date();
    };

    return (
        <Card>
            <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinkIcon color="primary" />
                        <Typography variant="h5" component="h2">
                            Share Link Manager
                        </Typography>
                    </Box>
                    <Box>
                        <IconButton onClick={loadShareLinks} disabled={loading || !channelId}>
                            <RefreshIcon />
                        </IconButton>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => setCreateDialogOpen(true)}
                            disabled={!channelId}
                        >
                            Create Link
                        </Button>
                    </Box>
                </Box>

                {/* Alerts */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}
                {success && (
                    <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
                        {success}
                    </Alert>
                )}

                {!channelId && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                        Select a channel to manage share links
                    </Alert>
                )}

                {/* Share Links Table */}
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : shareLinks.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                        <ShareIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
                        <Typography variant="body1">
                            No share links yet. Create one to get started!
                        </Typography>
                    </Box>
                ) : (
                    <TableContainer component={Paper} variant="outlined">
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Report Type</TableCell>
                                    <TableCell>Share URL</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell align="center">Access Count</TableCell>
                                    <TableCell>Expires</TableCell>
                                    <TableCell align="center">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {shareLinks.map((link) => (
                                    <TableRow key={link.share_token} hover>
                                        <TableCell>
                                            <Typography variant="body2" fontWeight="medium">
                                                {link.report_type}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Typography
                                                    variant="body2"
                                                    sx={{
                                                        maxWidth: 300,
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        whiteSpace: 'nowrap'
                                                    }}
                                                >
                                                    {link.share_token}
                                                </Typography>
                                                <IconButton
                                                    size="small"
                                                    onClick={() => copyToClipboard(link.share_token)}
                                                >
                                                    <CopyIcon fontSize="small" />
                                                </IconButton>
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            {isExpired(link.expires_at) ? (
                                                <Chip label="Expired" color="error" size="small" />
                                            ) : (
                                                <Chip label="Active" color="success" size="small" />
                                            )}
                                        </TableCell>
                                        <TableCell align="center">
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                <ViewsIcon fontSize="small" color="action" />
                                                <Typography variant="body2">
                                                    {link.access_count || 0}
                                                </Typography>
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <TimeIcon fontSize="small" color="action" />
                                                <Typography variant="caption">
                                                    {new Date(link.expires_at).toLocaleString()}
                                                </Typography>
                                            </Box>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Tooltip title="Revoke link">
                                                <IconButton
                                                    size="small"
                                                    color="error"
                                                    onClick={() => handleRevokeLink(link.share_token || '')}
                                                    disabled={isExpired(link.expires_at)}
                                                >
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}

                {/* Create Share Link Dialog */}
                <Dialog
                    open={createDialogOpen}
                    onClose={() => setCreateDialogOpen(false)}
                    maxWidth="sm"
                    fullWidth
                >
                    <DialogTitle>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <ShareIcon />
                            Create Share Link
                        </Box>
                    </DialogTitle>
                    <DialogContent>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
                            <FormControl fullWidth>
                                <InputLabel>Report Type</InputLabel>
                                <Select
                                    value={reportType}
                                    label="Report Type"
                                    onChange={(e) => setReportType(e.target.value)}
                                >
                                    <MenuItem value="overview">Overview</MenuItem>
                                    <MenuItem value="growth">Growth</MenuItem>
                                    <MenuItem value="engagement">Engagement</MenuItem>
                                    <MenuItem value="top-posts">Top Posts</MenuItem>
                                    <MenuItem value="analytics">Full Analytics</MenuItem>
                                </Select>
                            </FormControl>

                            <FormControl fullWidth>
                                <InputLabel>Link Validity</InputLabel>
                                <Select
                                    value={ttl}
                                    label="Link Validity"
                                    onChange={(e) => setTTL(e.target.value as TTLOption)}
                                >
                                    <MenuItem value="1h">1 Hour</MenuItem>
                                    <MenuItem value="6h">6 Hours</MenuItem>
                                    <MenuItem value="24h">24 Hours</MenuItem>
                                    <MenuItem value="3d">3 Days</MenuItem>
                                    <MenuItem value="7d">7 Days (Recommended)</MenuItem>
                                    <MenuItem value="30d">30 Days</MenuItem>
                                </Select>
                            </FormControl>

                            <FormControl fullWidth>
                                <InputLabel>Export Format</InputLabel>
                                <Select
                                    value={format}
                                    label="Export Format"
                                    onChange={(e) => setFormat(e.target.value as 'csv' | 'png')}
                                >
                                    <MenuItem value="csv">CSV (Spreadsheet)</MenuItem>
                                    <MenuItem value="png">PNG (Image)</MenuItem>
                                </Select>
                            </FormControl>

                            <Alert severity="info">
                                This link will expire in {formatTTL(ttl)} and can be revoked anytime.
                            </Alert>
                        </Box>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setCreateDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button
                            variant="contained"
                            onClick={handleCreateShareLink}
                            disabled={loading}
                            startIcon={loading ? <CircularProgress size={20} /> : <ShareIcon />}
                        >
                            Create Link
                        </Button>
                    </DialogActions>
                </Dialog>
            </CardContent>
        </Card>
    );
};

export default ShareLinkManager;
