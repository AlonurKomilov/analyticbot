/**
 * 📦 Marketplace Items Tab
 *
 * Browse and purchase AI models, themes, widgets, and bundles.
 * This is the original marketplace content extracted into a tab.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    CardActions,
    Button,
    Chip,
    TextField,
    InputAdornment,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Rating,
    Skeleton,
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Snackbar,
} from '@mui/material';
import {
    Search as SearchIcon,
    Psychology as AIIcon,
    Palette as ThemeIcon,
    Widgets as WidgetIcon,
    CheckCircle as OwnedIcon,
    ShoppingCart as CartIcon,
    WorkspacePremium as PremiumIcon,
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/api/client';

// Types
interface MarketplaceItem {
    id: number;
    name: string;
    slug: string;
    description: string;
    category: string;
    subcategory: string;
    price_credits: number;
    is_premium: boolean;
    is_featured: boolean;
    preview_url: string | null;
    icon_url: string | null;
    metadata: Record<string, any>;
    download_count: number;
    rating: number;
    rating_count: number;
}

// Category configurations
const CATEGORY_CONFIG: Record<string, { icon: React.ReactElement; color: string; label: string }> = {
    ai_models: { icon: <AIIcon />, color: '#9C27B0', label: 'AI Models' },
    themes: { icon: <ThemeIcon />, color: '#2196F3', label: 'Themes' },
    widgets: { icon: <WidgetIcon />, color: '#4CAF50', label: 'Widgets' },
};

const MarketplaceItemsTab: React.FC = () => {
    const { user } = useAuth();
    const [items, setItems] = useState<MarketplaceItem[]>([]);
    const [userPurchases, setUserPurchases] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [creditBalance, setCreditBalance] = useState<number>(user?.credit_balance || 0);

    // Filters
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string>('');

    // Purchase dialog
    const [purchaseDialog, setPurchaseDialog] = useState<{
        open: boolean;
        item: MarketplaceItem | null;
    }>({ open: false, item: null });
    const [purchasing, setPurchasing] = useState(false);

    // Snackbar
    const [snackbar, setSnackbar] = useState<{
        open: boolean;
        message: string;
        severity: 'success' | 'error' | 'info';
    }>({ open: false, message: '', severity: 'info' });

    // Fetch data
    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [itemsRes, purchasesRes] = await Promise.all([
                apiClient.get<{ items: MarketplaceItem[] }>('/marketplace/items', {
                    params: {
                        category: selectedCategory || undefined,
                        search: searchQuery || undefined,
                    }
                }),
                apiClient.get<{ purchases: { item_id: number }[] }>('/marketplace/purchases'),
            ]);

            setItems(itemsRes.items || []);
            setUserPurchases((purchasesRes.purchases || []).map((p) => p.item_id));
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to load marketplace');
        } finally {
            setLoading(false);
        }
    }, [selectedCategory, searchQuery]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Refresh credit balance
    const refreshBalance = async () => {
        try {
            const res = await apiClient.get<{ balance: number }>('/credits/balance');
            setCreditBalance(res.balance);
        } catch (err) {
            console.error('Failed to refresh balance', err);
        }
    };

    // Purchase handler
    const handlePurchase = async () => {
        if (!purchaseDialog.item) return;

        setPurchasing(true);
        try {
            await apiClient.post('/marketplace/purchase', {
                item_id: purchaseDialog.item.id
            });

            setSnackbar({
                open: true,
                message: `Successfully purchased ${purchaseDialog.item.name}!`,
                severity: 'success'
            });
            setPurchaseDialog({ open: false, item: null });
            refreshBalance();
            fetchData();
        } catch (err: any) {
            setSnackbar({
                open: true,
                message: err.response?.data?.detail || 'Failed to purchase item',
                severity: 'error'
            });
        } finally {
            setPurchasing(false);
        }
    };

    // Filter items
    const filteredItems = items.filter((item) => {
        if (searchQuery && !item.name.toLowerCase().includes(searchQuery.toLowerCase())) {
            return false;
        }
        return true;
    });

    return (
        <Box>
            {/* Filters */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                    <TextField
                        fullWidth
                        placeholder="Search items..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon />
                                </InputAdornment>
                            ),
                        }}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                        <InputLabel>Category</InputLabel>
                        <Select
                            value={selectedCategory}
                            label="Category"
                            onChange={(e) => setSelectedCategory(e.target.value)}
                        >
                            <MenuItem value="">All Categories</MenuItem>
                            <MenuItem value="ai_models">AI Models</MenuItem>
                            <MenuItem value="themes">Themes</MenuItem>
                            <MenuItem value="widgets">Widgets</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Items Grid */}
            {loading ? (
                <Grid container spacing={3}>
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <Grid item xs={12} md={6} lg={4} key={i}>
                            <Card>
                                <CardContent>
                                    <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
                                    <Skeleton variant="text" />
                                    <Skeleton variant="text" />
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : filteredItems.length === 0 ? (
                <Alert severity="info">No items found.</Alert>
            ) : (
                <Grid container spacing={3}>
                    {filteredItems.map((item) => {
                        const isOwned = userPurchases.includes(item.id);

                        return (
                            <Grid item xs={12} md={6} lg={4} key={item.id}>
                                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                    <CardContent sx={{ flexGrow: 1 }}>
                                        {/* Icon & Title */}
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                            <Box
                                                sx={{
                                                    width: 50,
                                                    height: 50,
                                                    borderRadius: 2,
                                                    bgcolor: CATEGORY_CONFIG[item.category]?.color || '#667eea',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    color: 'white',
                                                }}
                                            >
                                                {CATEGORY_CONFIG[item.category]?.icon || <WidgetIcon />}
                                            </Box>
                                            <Box sx={{ flex: 1 }}>
                                                <Typography variant="h6">{item.name}</Typography>
                                                {item.is_premium && (
                                                    <Chip
                                                        label="Premium"
                                                        size="small"
                                                        icon={<PremiumIcon />}
                                                        color="warning"
                                                    />
                                                )}
                                            </Box>
                                        </Box>

                                        {/* Description */}
                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                            {item.description}
                                        </Typography>

                                        {/* Rating */}
                                        {item.rating_count > 0 && (
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                                <Rating value={item.rating} readOnly size="small" />
                                                <Typography variant="caption" color="text.secondary">
                                                    ({item.rating_count})
                                                </Typography>
                                            </Box>
                                        )}

                                        {/* Price */}
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="h5" color="primary">
                                                {item.price_credits}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary">
                                                credits
                                            </Typography>
                                        </Box>
                                    </CardContent>

                                    <CardActions>
                                        {isOwned ? (
                                            <Button fullWidth disabled startIcon={<OwnedIcon />}>
                                                Owned
                                            </Button>
                                        ) : (
                                            <Button
                                                fullWidth
                                                variant="contained"
                                                startIcon={<CartIcon />}
                                                onClick={() => setPurchaseDialog({ open: true, item })}
                                            >
                                                Purchase
                                            </Button>
                                        )}
                                    </CardActions>
                                </Card>
                            </Grid>
                        );
                    })}
                </Grid>
            )}

            {/* Purchase Dialog */}
            <Dialog
                open={purchaseDialog.open}
                onClose={() => setPurchaseDialog({ open: false, item: null })}
            >
                <DialogTitle>Confirm Purchase</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to purchase <strong>{purchaseDialog.item?.name}</strong> for{' '}
                        <strong>{purchaseDialog.item?.price_credits} credits</strong>?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Your balance: {creditBalance.toLocaleString()} credits
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setPurchaseDialog({ open: false, item: null })}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handlePurchase}
                        variant="contained"
                        disabled={purchasing}
                    >
                        {purchasing ? 'Purchasing...' : 'Confirm Purchase'}
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
        </Box>
    );
};

export default MarketplaceItemsTab;
