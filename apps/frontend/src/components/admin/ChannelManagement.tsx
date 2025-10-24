/**
 * Channel Management Component
 * 
 * Admin dashboard for channel oversight and management.
 * Integrates with admin/channelsService.ts
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    IconButton,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    Chip,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    Paper,
    Avatar,
    Menu,
    MenuItem,
    Divider
} from '@mui/material';
import {
    MoreVert as MoreIcon,
    Block as BlockIcon,
    CheckCircle as ActiveIcon,
    Delete as DeleteIcon,
    Search as SearchIcon,
    Refresh as RefreshIcon,
    History as HistoryIcon,
    Assessment as StatsIcon
} from '@mui/icons-material';
import { 
    adminChannelsService, 
    type AdminChannelInfo, 
    type ChannelStatistics,
    type ChannelAuditLog 
} from '@/services/admin/channelsService';

export interface ChannelManagementProps {
    onChannelUpdated?: () => void;
}

const ChannelManagement: React.FC<ChannelManagementProps> = ({ onChannelUpdated }) => {
    const [channels, setChannels] = useState<AdminChannelInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [selectedChannel, setSelectedChannel] = useState<AdminChannelInfo | null>(null);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [actionDialog, setActionDialog] = useState<{
        open: boolean;
        type: 'suspend' | 'delete' | 'stats' | 'audit' | null;
        channel: AdminChannelInfo | null;
    }>({
        open: false,
        type: null,
        channel: null
    });
    const [suspendReason, setSuspendReason] = useState('');
    const [statistics, setStatistics] = useState<ChannelStatistics | null>(null);
    const [auditLogs, setAuditLogs] = useState<ChannelAuditLog[]>([]);
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        loadChannels();
    }, []);

    const loadChannels = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await adminChannelsService.getAllChannels();
            setChannels(data.channels);
        } catch (err: any) {
            setError(err.message || 'Failed to load channels');
            console.error('Failed to load channels:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchTerm.trim()) {
            loadChannels();
            return;
        }

        setLoading(true);
        try {
            const results = await adminChannelsService.searchChannels(searchTerm);
            setChannels(results);
        } catch (err: any) {
            setError(err.message || 'Search failed');
        } finally {
            setLoading(false);
        }
    };

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, channel: AdminChannelInfo) => {
        setAnchorEl(event.currentTarget);
        setSelectedChannel(channel);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const openActionDialog = (type: 'suspend' | 'delete' | 'stats' | 'audit', channel: AdminChannelInfo) => {
        setActionDialog({ open: true, type, channel });
        handleMenuClose();
        
        // Load additional data for stats and audit
        if (type === 'stats') {
            loadStatistics();
        } else if (type === 'audit') {
            loadAuditLogs(channel.channel_id);
        }
    };

    const closeActionDialog = () => {
        setActionDialog({ open: false, type: null, channel: null });
        setSuspendReason('');
        setStatistics(null);
        setAuditLogs([]);
    };

    const loadStatistics = async () => {
        setActionLoading(true);
        try {
            const stats = await adminChannelsService.getChannelStatistics();
            setStatistics(stats);
        } catch (err) {
            console.error('Failed to load statistics:', err);
        } finally {
            setActionLoading(false);
        }
    };

    const loadAuditLogs = async (channelId: string) => {
        setActionLoading(true);
        try {
            const logs = await adminChannelsService.getChannelAuditLog(channelId);
            setAuditLogs(logs);
        } catch (err) {
            console.error('Failed to load audit logs:', err);
        } finally {
            setActionLoading(false);
        }
    };

    const handleSuspendChannel = async () => {
        if (!actionDialog.channel || !suspendReason.trim()) return;

        setActionLoading(true);
        try {
            await adminChannelsService.suspendChannel(
                actionDialog.channel.channel_id,
                {
                    reason: suspendReason,
                    duration_days: 30, // Default 30 days
                    notify_user: true
                }
            );
            await loadChannels();
            closeActionDialog();
            onChannelUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to suspend channel');
        } finally {
            setActionLoading(false);
        }
    };

    const handleUnsuspendChannel = async (channelId: string) => {
        setActionLoading(true);
        try {
            await adminChannelsService.unsuspendChannel(channelId);
            await loadChannels();
            onChannelUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to unsuspend channel');
        } finally {
            setActionLoading(false);
        }
    };

    const handleDeleteChannel = async () => {
        if (!actionDialog.channel) return;

        setActionLoading(true);
        try {
            await adminChannelsService.deleteChannel(
                actionDialog.channel.channel_id,
                'Admin deleted channel'
            );
            await loadChannels();
            closeActionDialog();
            onChannelUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to delete channel');
        } finally {
            setActionLoading(false);
        }
    };

    const filteredChannels = channels.filter(channel => 
        channel.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        channel.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        channel.channel_id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const paginatedChannels = filteredChannels.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
    );

    return (
        <Card>
            <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                    <Typography variant="h5" component="h2">
                        Channel Management
                    </Typography>
                    <Button
                        startIcon={<RefreshIcon />}
                        onClick={loadChannels}
                        disabled={loading}
                        size="small"
                    >
                        Refresh
                    </Button>
                </Box>

                {/* Search Bar */}
                <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                    <TextField
                        fullWidth
                        size="small"
                        placeholder="Search by channel name or ID..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        InputProps={{
                            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                        }}
                    />
                    <Button variant="contained" onClick={handleSearch}>
                        Search
                    </Button>
                </Box>

                {/* Error Alert */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {/* Channels Table */}
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        <TableContainer component={Paper} variant="outlined">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Channel</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell align="right">Subscribers</TableCell>
                                        <TableCell align="right">Posts</TableCell>
                                        <TableCell>Created</TableCell>
                                        <TableCell align="center">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {paginatedChannels.map((channel) => (
                                        <TableRow key={channel.channel_id} hover>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Avatar sx={{ width: 32, height: 32 }}>
                                                        {channel.title[0]}
                                                    </Avatar>
                                                    <Box>
                                                        <Typography variant="body2" fontWeight="medium">
                                                            {channel.title}
                                                        </Typography>
                                                        <Typography variant="caption" color="text.secondary">
                                                            @{channel.username}
                                                        </Typography>
                                                    </Box>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                {channel.status === 'suspended' ? (
                                                    <Chip 
                                                        label="Suspended" 
                                                        color="error" 
                                                        size="small"
                                                        icon={<BlockIcon />}
                                                    />
                                                ) : channel.status === 'deleted' ? (
                                                    <Chip 
                                                        label="Deleted" 
                                                        color="default" 
                                                        size="small"
                                                        icon={<DeleteIcon />}
                                                    />
                                                ) : (
                                                    <Chip 
                                                        label="Active" 
                                                        color="success" 
                                                        size="small"
                                                        icon={<ActiveIcon />}
                                                    />
                                                )}
                                            </TableCell>
                                            <TableCell align="right">
                                                {channel.total_views?.toLocaleString() || 'N/A'}
                                            </TableCell>
                                            <TableCell align="right">
                                                {channel.total_posts?.toLocaleString() || 'N/A'}
                                            </TableCell>
                                            <TableCell>
                                                {new Date(channel.created_at).toLocaleDateString()}
                                            </TableCell>
                                            <TableCell align="center">
                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => handleMenuOpen(e, channel)}
                                                >
                                                    <MoreIcon />
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>

                        <TablePagination
                            component="div"
                            count={filteredChannels.length}
                            page={page}
                            onPageChange={(_, newPage) => setPage(newPage)}
                            rowsPerPage={rowsPerPage}
                            onRowsPerPageChange={(e) => {
                                setRowsPerPage(parseInt(e.target.value, 10));
                                setPage(0);
                            }}
                        />
                    </>
                )}

                {/* Action Menu */}
                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                >
                    <MenuItem onClick={() => selectedChannel && openActionDialog('stats', selectedChannel)}>
                        <StatsIcon fontSize="small" sx={{ mr: 1 }} />
                        View Statistics
                    </MenuItem>
                    <MenuItem onClick={() => selectedChannel && openActionDialog('audit', selectedChannel)}>
                        <HistoryIcon fontSize="small" sx={{ mr: 1 }} />
                        Audit Log
                    </MenuItem>
                    <Divider />
                    {selectedChannel?.status === 'suspended' ? (
                        <MenuItem onClick={() => selectedChannel && handleUnsuspendChannel(selectedChannel.channel_id)}>
                            <ActiveIcon fontSize="small" sx={{ mr: 1 }} />
                            Unsuspend
                        </MenuItem>
                    ) : (
                        <MenuItem onClick={() => selectedChannel && openActionDialog('suspend', selectedChannel)}>
                            <BlockIcon fontSize="small" sx={{ mr: 1 }} />
                            Suspend
                        </MenuItem>
                    )}
                    <MenuItem 
                        onClick={() => selectedChannel && openActionDialog('delete', selectedChannel)}
                        sx={{ color: 'error.main' }}
                    >
                        <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
                        Delete
                    </MenuItem>
                </Menu>

                {/* Action Dialogs */}
                <Dialog 
                    open={actionDialog.open} 
                    onClose={closeActionDialog}
                    maxWidth="sm"
                    fullWidth
                >
                    <DialogTitle>
                        {actionDialog.type === 'suspend' && 'Suspend Channel'}
                        {actionDialog.type === 'delete' && 'Delete Channel'}
                        {actionDialog.type === 'stats' && 'Channel Statistics'}
                        {actionDialog.type === 'audit' && 'Audit Log'}
                    </DialogTitle>
                    <DialogContent>
                        {/* Suspend Dialog */}
                        {actionDialog.type === 'suspend' && (
                            <Box>
                                <Alert severity="warning" sx={{ mb: 2 }}>
                                    This will suspend the channel and prevent further activity.
                                </Alert>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={3}
                                    label="Suspension Reason"
                                    value={suspendReason}
                                    onChange={(e) => setSuspendReason(e.target.value)}
                                    placeholder="Enter reason for suspension..."
                                    required
                                />
                            </Box>
                        )}

                        {/* Delete Dialog */}
                        {actionDialog.type === 'delete' && (
                            <Alert severity="error">
                                Are you sure you want to delete channel "{actionDialog.channel?.title}"? 
                                This action cannot be undone.
                            </Alert>
                        )}

                        {/* Statistics Dialog */}
                        {actionDialog.type === 'stats' && (
                            <Box>
                                {actionLoading ? (
                                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                        <CircularProgress />
                                    </Box>
                                ) : statistics ? (
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                Total Posts
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.total_posts.toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                Total Views
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.total_views.toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                New This Week
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.new_this_week}
                                            </Typography>
                                        </Box>
                                    </Box>
                                ) : (
                                    <Alert severity="info">No statistics available</Alert>
                                )}
                            </Box>
                        )}

                        {/* Audit Log Dialog */}
                        {actionDialog.type === 'audit' && (
                            <Box>
                                {actionLoading ? (
                                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                        <CircularProgress />
                                    </Box>
                                ) : auditLogs.length > 0 ? (
                                    <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                                        {auditLogs.map((log, index) => (
                                            <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                                                <Typography variant="body2" fontWeight="medium">
                                                    {log.action}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    by {log.admin_email} • {new Date(log.timestamp).toLocaleString()}
                                                </Typography>
                                                {log.details && Object.keys(log.details).length > 0 && (
                                                    <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                                        {JSON.stringify(log.details)}
                                                    </Typography>
                                                )}
                                            </Box>
                                        ))}
                                    </Box>
                                ) : (
                                    <Alert severity="info">No audit logs available</Alert>
                                )}
                            </Box>
                        )}
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={closeActionDialog}>Cancel</Button>
                        {actionDialog.type === 'suspend' && (
                            <Button 
                                onClick={handleSuspendChannel} 
                                variant="contained" 
                                color="warning"
                                disabled={!suspendReason.trim() || actionLoading}
                            >
                                {actionLoading ? <CircularProgress size={20} /> : 'Suspend'}
                            </Button>
                        )}
                        {actionDialog.type === 'delete' && (
                            <Button 
                                onClick={handleDeleteChannel} 
                                variant="contained" 
                                color="error"
                                disabled={actionLoading}
                            >
                                {actionLoading ? <CircularProgress size={20} /> : 'Delete'}
                            </Button>
                        )}
                    </DialogActions>
                </Dialog>
            </CardContent>
        </Card>
    );
};

export default ChannelManagement;
