/**
 * 📊 My Services Page
 *
 * Manage active service subscriptions, view usage stats, and configure services.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    Container,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    CardActions,
    Button,
    Chip,
    Alert,
    Snackbar,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Switch,
    Skeleton,
} from '@mui/material';
import {
    CheckCircle as ActiveIcon,
    Cancel as CancelIcon,
    Refresh as RefreshIcon,
    TrendingUp as UsageIcon,
    CalendarToday as CalendarIcon,
    Autorenew as AutoRenewIcon,
    Info as InfoIcon,
    ShoppingCart as ShopIcon,
    Extension as ExtensionIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api/client';
import { ROUTES } from '@/config/routes';
import { getServiceIcon as getServiceIconFromRegistry } from '@/features/marketplace';

// Types
interface UserServiceSubscription {
    id: number;
    service_id: number;
    service_key: string;
    service_name: string;
    service_description: string | null;
    icon: string | null;
    color: string | null;
    category: string;
    status: 'active' | 'expired' | 'cancelled';
    billing_cycle: 'monthly' | 'yearly';
    price_paid: number;
    started_at: string;  // API field name
    expires_at: string;
    auto_renew: boolean;
    usage_quota_daily: number | null;
    usage_quota_monthly: number | null;
    usage_count_daily: number;  // API field name
    usage_count_monthly: number;  // API field name
}

// Get icon component for a service (use registry or fallback)
const getServiceIcon = (iconName: string | null, serviceKey: string): React.ReactNode => {
    // Try getting from registry first
    const registryIcon = getServiceIconFromRegistry(serviceKey);
    if (registryIcon) {
        return registryIcon;
    }
    return <ExtensionIcon />;
};

const MyServicesPage: React.FC = () => {
    const navigate = useNavigate();
    const [subscriptions, setSubscriptions] = useState<UserServiceSubscription[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Cancel dialog
    const [cancelDialog, setCancelDialog] = useState<{
        open: boolean;
        subscription: UserServiceSubscription | null;
    }>({ open: false, subscription: null });
    const [cancelling, setCancelling] = useState(false);

    // Snackbar
    const [snackbar, setSnackbar] = useState<{
        open: boolean;
        message: string;
        severity: 'success' | 'error' | 'info';
    }>({ open: false, message: '', severity: 'info' });

    // Fetch subscriptions
    const fetchSubscriptions = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await apiClient.get<{ subscriptions: UserServiceSubscription[] }>(
                '/services/user/active'
            );
            setSubscriptions(res.subscriptions || []);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to load subscriptions');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSubscriptions();
    }, [fetchSubscriptions]);

    // Toggle auto-renew
    const handleToggleAutoRenew = async (subscription: UserServiceSubscription) => {
        try {
            await apiClient.post(`/services/user/${subscription.id}/auto-renew`, {
                auto_renew: !subscription.auto_renew,
            });
            setSnackbar({
                open: true,
                message: `Auto-renewal ${!subscription.auto_renew ? 'enabled' : 'disabled'} for ${subscription.service_name}`,
                severity: 'success',
            });
            fetchSubscriptions();
        } catch (err: any) {
            setSnackbar({
                open: true,
                message: err.response?.data?.detail || 'Failed to update auto-renewal',
                severity: 'error',
            });
        }
    };

    // Cancel subscription
    const handleCancelSubscription = async () => {
        if (!cancelDialog.subscription) return;
        setCancelling(true);
        try {
            await apiClient.post(`/services/user/${cancelDialog.subscription.id}/cancel`);
            setSnackbar({
                open: true,
                message: `Successfully cancelled ${cancelDialog.subscription.service_name} subscription`,
                severity: 'success',
            });
            setCancelDialog({ open: false, subscription: null });
            fetchSubscriptions();
        } catch (err: any) {
            setSnackbar({
                open: true,
                message: err.response?.data?.detail || 'Failed to cancel subscription',
                severity: 'error',
            });
        } finally {
            setCancelling(false);
        }
    };

    // Get usage percentage
    const getUsagePercentage = (used: number, quota: number | null): number => {
        if (!quota) return 0;
        return Math.min((used / quota) * 100, 100);
    };

    // Format date
    const formatDate = (dateStr: string): string => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    };

    // Get status color
    const getStatusColor = (status: string): 'success' | 'error' | 'warning' => {
        switch (status) {
            case 'active':
                return 'success';
            case 'expired':
                return 'error';
            case 'cancelled':
                return 'warning';
            default:
                return 'success';
        }
    };

    // Get days remaining
    const getDaysRemaining = (expiresAt: string): number => {
        const now = new Date();
        const expiry = new Date(expiresAt);
        const diff = expiry.getTime() - now.getTime();
        return Math.ceil(diff / (1000 * 60 * 60 * 24));
    };

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                    <Typography variant="h4" component="h1" gutterBottom>
                        📊 My Services
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Manage your active service subscriptions and monitor usage
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={fetchSubscriptions}
                        disabled={loading}
                    >
                        Refresh
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<ShopIcon />}
                        onClick={() => navigate(ROUTES.MARKETPLACE + '?tab=services')}
                    >
                        Browse Services
                    </Button>
                </Box>
            </Box>

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Loading State */}
            {loading ? (
                <Grid container spacing={3}>
                    {[1, 2, 3].map((i) => (
                        <Grid item xs={12} md={6} lg={4} key={i}>
                            <Card>
                                <CardContent>
                                    <Skeleton variant="rectangular" height={80} sx={{ mb: 2 }} />
                                    <Skeleton variant="text" />
                                    <Skeleton variant="text" />
                                    <Skeleton variant="text" width="60%" />
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : subscriptions.length === 0 ? (
                <Card>
                    <CardContent sx={{ textAlign: 'center', py: 6 }}>
                        <InfoIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" gutterBottom>
                            No Active Subscriptions
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            You don't have any active service subscriptions yet.
                        </Typography>
                        <Button
                            variant="contained"
                            startIcon={<ShopIcon />}
                            onClick={() => navigate(ROUTES.MARKETPLACE + '?tab=services')}
                        >
                            Browse Services Marketplace
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <Grid container spacing={3}>
                    {subscriptions.map((subscription) => {
                        const daysRemaining = getDaysRemaining(subscription.expires_at);
                        const isExpiringSoon = daysRemaining <= 7 && subscription.status === 'active';

                        return (
                            <Grid item xs={12} md={6} lg={4} key={subscription.id}>
                                <Card
                                    sx={{
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        position: 'relative',
                                    }}
                                >
                                    {/* Status Badge */}
                                    <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
                                        <Chip
                                            label={subscription.status.toUpperCase()}
                                            color={getStatusColor(subscription.status)}
                                            size="small"
                                            icon={<ActiveIcon />}
                                        />
                                    </Box>

                                    <CardContent sx={{ flexGrow: 1 }}>
                                        {/* Service Info */}
                                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
                                            <Box
                                                sx={{
                                                    width: 50,
                                                    height: 50,
                                                    borderRadius: 2,
                                                    bgcolor: subscription.color || '#667eea',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    color: 'white',
                                                    flexShrink: 0,
                                                }}
                                            >
                                                {getServiceIcon(subscription.icon, subscription.service_key)}
                                            </Box>
                                            <Box sx={{ flex: 1, minWidth: 0 }}>
                                                <Typography variant="h6" component="h3" noWrap title={subscription.service_name}>
                                                    {subscription.service_name}
                                                </Typography>
                                                <Chip
                                                    label={subscription.billing_cycle}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                            </Box>
                                        </Box>

                                        {/* Expiration Warning */}
                                        {isExpiringSoon && (
                                            <Alert severity="warning" sx={{ mb: 2 }}>
                                                Expires in {daysRemaining} days
                                            </Alert>
                                        )}

                                        {/* Subscription Details */}
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon>
                                                    <CalendarIcon fontSize="small" />
                                                </ListItemIcon>
                                                <ListItemText
                                                    primary="Subscribed"
                                                    secondary={formatDate(subscription.started_at)}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemIcon>
                                                    <CalendarIcon fontSize="small" />
                                                </ListItemIcon>
                                                <ListItemText
                                                    primary="Expires"
                                                    secondary={formatDate(subscription.expires_at)}
                                                />
                                            </ListItem>
                                        </List>

                                        {/* Usage Stats */}
                                        {(subscription.usage_quota_daily || subscription.usage_quota_monthly) && (
                                            <Box sx={{ mt: 2 }}>
                                                <Typography variant="subtitle2" gutterBottom>
                                                    Usage Statistics
                                                </Typography>

                                                {/* Daily Usage */}
                                                {subscription.usage_quota_daily && (
                                                    <Box sx={{ mb: 2 }}>
                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                                            <Typography variant="caption">Daily</Typography>
                                                            <Typography variant="caption">
                                                                {subscription.usage_count_daily} / {subscription.usage_quota_daily}
                                                            </Typography>
                                                        </Box>
                                                        <LinearProgress
                                                            variant="determinate"
                                                            value={getUsagePercentage(
                                                                subscription.usage_count_daily,
                                                                subscription.usage_quota_daily
                                                            )}
                                                            color={
                                                                getUsagePercentage(
                                                                    subscription.usage_count_daily,
                                                                    subscription.usage_quota_daily
                                                                ) >= 90
                                                                    ? 'error'
                                                                    : 'primary'
                                                            }
                                                        />
                                                    </Box>
                                                )}

                                                {/* Monthly Usage */}
                                                {subscription.usage_quota_monthly && (
                                                    <Box>
                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                                            <Typography variant="caption">Monthly</Typography>
                                                            <Typography variant="caption">
                                                                {subscription.usage_count_monthly} / {subscription.usage_quota_monthly}
                                                            </Typography>
                                                        </Box>
                                                        <LinearProgress
                                                            variant="determinate"
                                                            value={getUsagePercentage(
                                                                subscription.usage_count_monthly,
                                                                subscription.usage_quota_monthly
                                                            )}
                                                            color={
                                                                getUsagePercentage(
                                                                    subscription.usage_count_monthly,
                                                                    subscription.usage_quota_monthly
                                                                ) >= 90
                                                                    ? 'error'
                                                                    : 'primary'
                                                            }
                                                        />
                                                    </Box>
                                                )}
                                            </Box>
                                        )}

                                        {/* Auto-renewal */}
                                        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <AutoRenewIcon fontSize="small" />
                                                <Typography variant="body2">Auto-Renewal</Typography>
                                            </Box>
                                            <Switch
                                                checked={subscription.auto_renew}
                                                onChange={() => handleToggleAutoRenew(subscription)}
                                                disabled={subscription.status !== 'active'}
                                            />
                                        </Box>
                                    </CardContent>

                                    <CardActions>
                                        <Button
                                            size="small"
                                            color="error"
                                            startIcon={<CancelIcon />}
                                            onClick={() => setCancelDialog({ open: true, subscription })}
                                            disabled={subscription.status !== 'active'}
                                        >
                                            Cancel
                                        </Button>
                                    </CardActions>
                                </Card>
                            </Grid>
                        );
                    })}
                </Grid>
            )}

            {/* Cancel Confirmation Dialog */}
            <Dialog
                open={cancelDialog.open}
                onClose={() => setCancelDialog({ open: false, subscription: null })}
            >
                <DialogTitle>Cancel Subscription</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to cancel your subscription to{' '}
                        <strong>{cancelDialog.subscription?.service.name}</strong>?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Your subscription will remain active until {cancelDialog.subscription?.expires_at ? formatDate(cancelDialog.subscription.expires_at) : 'expiry'}. No refunds will be issued.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCancelDialog({ open: false, subscription: null })}>
                        Keep Subscription
                    </Button>
                    <Button
                        onClick={handleCancelSubscription}
                        color="error"
                        variant="contained"
                        disabled={cancelling}
                    >
                        {cancelling ? 'Cancelling...' : 'Cancel Subscription'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
            >
                <Alert
                    onClose={() => setSnackbar({ ...snackbar, open: false })}
                    severity={snackbar.severity}
                    sx={{ width: '100%' }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default MyServicesPage;
