/**
 * 💰 Credits Page
 *
 * User's credit management center - view balance, buy packages,
 * browse services, and view transaction history.
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
    Divider,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Alert,
    CircularProgress,
    Tabs,
    Tab,
    Paper,
    Avatar,
    Skeleton,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    MonetizationOn as CreditsIcon,
    ShoppingCart as PackageIcon,
    Category as ServiceIcon,
    History as HistoryIcon,
    CardGiftcard as GiftIcon,
    Refresh as RefreshIcon,
    ArrowUpward as CreditAddIcon,
    ArrowDownward as CreditSpendIcon,
    Star as StarIcon,
    Psychology as AIIcon,
    FileDownload as ExportIcon,
    Palette as ThemeIcon,
    Speed as PerformanceIcon,
    Api as ApiIcon,
    AutoAwesome as FeatureIcon,
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/api/client';

// Types - matching API response format
interface CreditPackage {
    id: number;
    name: string;
    slug: string;
    credits: number;
    bonus_credits: number;
    total_credits: number;
    price: number;
    currency: string;
    description: string;
    is_popular: boolean;
}

interface CreditService {
    id: number;
    service_key: string;
    name: string;
    description: string;
    credit_cost: number;
    category: string;
    icon: string;
}

interface CreditTransaction {
    id: number;
    amount: number;
    transaction_type: string;
    description: string;
    reference_type: string | null;
    reference_id: string | null;
    balance_after: number;
    created_at: string;
}

interface DailyRewardResult {
    success: boolean;
    message: string;
    credits_awarded?: number;
    new_balance?: number;
    streak_days?: number;
    next_reward_at?: string;
}

// Tab Panel Component
interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
    <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

// Category icons mapping
const categoryIcons: Record<string, React.ReactElement> = {
    ai: <AIIcon />,
    export: <ExportIcon />,
    theme: <ThemeIcon />,
    upgrade: <PerformanceIcon />,
    feature: <FeatureIcon />,
    api: <ApiIcon />,
};

const CreditsPage: React.FC = () => {
    const { user, updateUser } = useAuth();
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [claimingReward, setClaimingReward] = useState(false);
    const [balance, setBalance] = useState<number>(user?.credit_balance ?? 0);
    const [packages, setPackages] = useState<CreditPackage[]>([]);
    const [services, setServices] = useState<CreditService[]>([]);
    const [transactions, setTransactions] = useState<CreditTransaction[]>([]);
    const [rewardMessage, setRewardMessage] = useState<{ type: 'success' | 'info' | 'error'; text: string } | null>(null);
    
    // Track if initial fetch is done to prevent infinite loop
    const [initialFetchDone, setInitialFetchDone] = useState(false);

    // Fetch all credit data
    const fetchCreditData = useCallback(async (showRefreshing = false) => {
        if (showRefreshing) setRefreshing(true);
        else setLoading(true);

        try {
            const [balanceRes, packagesRes, servicesRes, transactionsRes] = await Promise.all([
                apiClient.get('/credits/balance'),
                apiClient.get('/credits/packages'),
                apiClient.get('/credits/services'),
                apiClient.get('/credits/transactions?limit=20'),
            ]);

            // API returns: { balance: number } for balance
            // API returns: array directly for packages, services, transactions
            const newBalance = (balanceRes as any).balance ?? 0;
            setBalance(newBalance);
            setPackages(Array.isArray(packagesRes) ? packagesRes : []);
            setServices(Array.isArray(servicesRes) ? servicesRes : []);
            setTransactions(Array.isArray(transactionsRes) ? transactionsRes : []);

            // Sync user context with actual balance (fixes header showing stale data)
            if (user && user.credit_balance !== newBalance) {
                updateUser({ ...user, credit_balance: newBalance });
            }

        } catch (error) {
            console.error('Failed to fetch credit data:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [user, updateUser]); // Added user and updateUser dependencies

    // Initial load - run only once
    useEffect(() => {
        if (!initialFetchDone) {
            setInitialFetchDone(true);
            fetchCreditData();
        }
    }, [initialFetchDone, fetchCreditData]);

    // Claim daily reward
    const handleClaimDailyReward = async () => {
        setClaimingReward(true);
        setRewardMessage(null);

        try {
            const result = await apiClient.post('/credits/daily-reward') as DailyRewardResult;

            if (result.success) {
                setRewardMessage({
                    type: 'success',
                    text: `🎉 ${result.message}! You earned ${result.credits_awarded} credits. Streak: ${result.streak_days} days!`,
                });
                setBalance(result.new_balance ?? balance);

                // Update user context
                if (user) {
                    updateUser({ ...user, credit_balance: result.new_balance ?? balance });
                }

                // Refresh transactions
                const transactionsRes = await apiClient.get('/credits/transactions?limit=20');
                setTransactions(Array.isArray(transactionsRes) ? transactionsRes : []);
            } else {
                setRewardMessage({
                    type: 'info',
                    text: result.message,
                });
            }
        } catch (error: any) {
            setRewardMessage({
                type: 'error',
                text: error.message || 'Failed to claim daily reward',
            });
        } finally {
            setClaimingReward(false);
        }
    };

    // Format date
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    // Get transaction icon
    const getTransactionIcon = (_type: string, amount: number) => {
        if (amount > 0) {
            return <CreditAddIcon sx={{ color: 'success.main' }} />;
        }
        return <CreditSpendIcon sx={{ color: 'error.main' }} />;
    };

    // Group services by category
    const servicesByCategory = services.reduce((acc, service) => {
        const cat = service.category || 'other';
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(service);
        return acc;
    }, {} as Record<string, CreditService[]>);

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ py: 4 }}>
                <Skeleton variant="rectangular" height={150} sx={{ mb: 3, borderRadius: 2 }} />
                <Grid container spacing={3}>
                    {[1, 2, 3, 4].map((i) => (
                        <Grid item xs={12} sm={6} md={3} key={i}>
                            <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
                        </Grid>
                    ))}
                </Grid>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {/* Balance Card */}
            <Paper
                elevation={3}
                sx={{
                    mb: 4,
                    p: 4,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    borderRadius: 3,
                }}
            >
                <Grid container spacing={3} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mr: 2, width: 56, height: 56 }}>
                                <CreditsIcon sx={{ fontSize: 32 }} />
                            </Avatar>
                            <Box>
                                <Typography variant="overline" sx={{ opacity: 0.9 }}>
                                    Your Balance
                                </Typography>
                                <Typography variant="h3" fontWeight="bold">
                                    {balance.toLocaleString()}
                                    <Typography component="span" variant="h5" sx={{ ml: 1, opacity: 0.8 }}>
                                        credits
                                    </Typography>
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                            <Button
                                variant="contained"
                                startIcon={claimingReward ? <CircularProgress size={20} color="inherit" /> : <GiftIcon />}
                                onClick={handleClaimDailyReward}
                                disabled={claimingReward}
                                sx={{
                                    bgcolor: 'rgba(255,255,255,0.2)',
                                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                                }}
                            >
                                Daily Reward
                            </Button>
                            <Tooltip title="Refresh balance">
                                <IconButton
                                    onClick={() => fetchCreditData(true)}
                                    disabled={refreshing}
                                    sx={{ color: 'white' }}
                                >
                                    {refreshing ? <CircularProgress size={24} color="inherit" /> : <RefreshIcon />}
                                </IconButton>
                            </Tooltip>
                        </Box>
                    </Grid>
                </Grid>
            </Paper>

            {/* Reward Message */}
            {rewardMessage && (
                <Alert severity={rewardMessage.type} sx={{ mb: 3 }} onClose={() => setRewardMessage(null)}>
                    {rewardMessage.text}
                </Alert>
            )}

            {/* Tabs */}
            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={activeTab}
                    onChange={(_, v) => setActiveTab(v)}
                    variant="fullWidth"
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab icon={<PackageIcon />} label="Buy Credits" />
                    <Tab icon={<ServiceIcon />} label="Services" />
                    <Tab icon={<HistoryIcon />} label="History" />
                </Tabs>
            </Paper>

            {/* Tab Content: Buy Credits */}
            <TabPanel value={activeTab} index={0}>
                <Typography variant="h5" gutterBottom>
                    Credit Packages
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Purchase credits to unlock premium features and AI services
                </Typography>

                <Grid container spacing={3}>
                    {packages.map((pkg) => (
                        <Grid item xs={12} sm={6} md={3} key={pkg.id}>
                            <Card
                                sx={{
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    position: 'relative',
                                    border: pkg.is_popular ? 2 : 0,
                                    borderColor: 'primary.main',
                                }}
                            >
                                {pkg.is_popular && (
                                    <Chip
                                        label="Most Popular"
                                        color="primary"
                                        size="small"
                                        icon={<StarIcon />}
                                        sx={{
                                            position: 'absolute',
                                            top: -12,
                                            left: '50%',
                                            transform: 'translateX(-50%)',
                                        }}
                                    />
                                )}
                                <CardContent sx={{ flexGrow: 1, textAlign: 'center', pt: pkg.is_popular ? 4 : 3 }}>
                                    <Typography variant="h6" gutterBottom>
                                        {pkg.name}
                                    </Typography>
                                    <Typography variant="h3" color="primary" fontWeight="bold">
                                        {pkg.total_credits.toLocaleString()}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        credits
                                    </Typography>
                                    {pkg.bonus_credits > 0 && (
                                        <Chip
                                            label={`+${pkg.bonus_credits} bonus!`}
                                            color="success"
                                            size="small"
                                            sx={{ mt: 1 }}
                                        />
                                    )}
                                    <Divider sx={{ my: 2 }} />
                                    <Typography variant="h4">
                                        ${pkg.price.toFixed(2)}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        ${(pkg.price / pkg.total_credits * 100).toFixed(1)}¢ per credit
                                    </Typography>
                                </CardContent>
                                <CardActions sx={{ p: 2, pt: 0 }}>
                                    <Button
                                        variant={pkg.is_popular ? 'contained' : 'outlined'}
                                        fullWidth
                                        startIcon={<PackageIcon />}
                                    >
                                        Buy Now
                                    </Button>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            </TabPanel>

            {/* Tab Content: Services */}
            <TabPanel value={activeTab} index={1}>
                <Typography variant="h5" gutterBottom>
                    Credit Services
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Spend your credits on powerful features and AI services
                </Typography>

                {Object.entries(servicesByCategory).map(([category, categoryServices]) => (
                    <Box key={category} sx={{ mb: 4 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <Avatar sx={{ bgcolor: 'primary.light', mr: 2 }}>
                                {categoryIcons[category] || <ServiceIcon />}
                            </Avatar>
                            <Typography variant="h6" textTransform="capitalize">
                                {category} Services
                            </Typography>
                        </Box>
                        <Grid container spacing={2}>
                            {categoryServices.map((service) => (
                                <Grid item xs={12} sm={6} md={4} key={service.id}>
                                    <Card variant="outlined" sx={{ height: '100%' }}>
                                        <CardContent>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                                                <Typography variant="subtitle1" fontWeight="medium">
                                                    {service.name}
                                                </Typography>
                                                <Chip
                                                    icon={<CreditsIcon sx={{ fontSize: 16 }} />}
                                                    label={service.credit_cost}
                                                    size="small"
                                                    color="primary"
                                                    variant="outlined"
                                                />
                                            </Box>
                                            <Typography variant="body2" color="text.secondary">
                                                {service.description}
                                            </Typography>
                                        </CardContent>
                                        <CardActions sx={{ px: 2, pb: 2 }}>
                                            <Button
                                                size="small"
                                                variant="outlined"
                                                disabled={balance < service.credit_cost}
                                            >
                                                {balance < service.credit_cost ? 'Not enough credits' : 'Use Service'}
                                            </Button>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                ))}
            </TabPanel>

            {/* Tab Content: History */}
            <TabPanel value={activeTab} index={2}>
                <Typography variant="h5" gutterBottom>
                    Transaction History
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    View your credit transactions and balance changes
                </Typography>

                {transactions.length === 0 ? (
                    <Paper sx={{ p: 4, textAlign: 'center' }}>
                        <HistoryIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                            No transactions yet
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Your credit transactions will appear here
                        </Typography>
                    </Paper>
                ) : (
                    <Paper>
                        <List>
                            {transactions.map((tx, index) => (
                                <React.Fragment key={tx.id}>
                                    {index > 0 && <Divider />}
                                    <ListItem>
                                        <ListItemIcon>
                                            {getTransactionIcon(tx.transaction_type, tx.amount)}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={tx.description}
                                            secondary={
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                                                    <Typography variant="caption" color="text.secondary">
                                                        {formatDate(tx.created_at)}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        Balance: {tx.balance_after.toLocaleString()}
                                                    </Typography>
                                                </Box>
                                            }
                                        />
                                        <Typography
                                            variant="body1"
                                            fontWeight="bold"
                                            color={tx.amount > 0 ? 'success.main' : 'error.main'}
                                            sx={{ ml: 2 }}
                                        >
                                            {tx.amount > 0 ? '+' : ''}{tx.amount.toLocaleString()}
                                        </Typography>
                                    </ListItem>
                                </React.Fragment>
                            ))}
                        </List>
                    </Paper>
                )}
            </TabPanel>
        </Container>
    );
};

export default CreditsPage;
