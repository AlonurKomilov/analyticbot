/**
 * 🏪 Marketplace Page
 *
 * Browse and purchase AI models, themes, widgets, and bundles.
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
    Tabs,
    Tab,
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
    Tooltip,
    Divider,
    Paper,
} from '@mui/material';
import {
    Search as SearchIcon,
    Psychology as AIIcon,
    Palette as ThemeIcon,
    Widgets as WidgetIcon,
    Inventory as BundleIcon,
    Star as StarIcon,
    LocalOffer as PriceIcon,
    CheckCircle as OwnedIcon,
    ShoppingCart as CartIcon,
    Download as DownloadIcon,
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

interface Bundle {
    id: number;
    name: string;
    slug: string;
    description: string;
    price_credits: number;
    original_price: number;
    discount_percent: number;
    is_featured: boolean;
    valid_days: number;
    items?: any[];
}

interface Category {
    category: string;
    item_count: number;
}

// Category configurations
const CATEGORY_CONFIG: Record<string, { icon: React.ReactElement; color: string; label: string }> = {
    ai_models: { icon: <AIIcon />, color: '#9C27B0', label: 'AI Models' },
    themes: { icon: <ThemeIcon />, color: '#2196F3', label: 'Themes' },
    widgets: { icon: <WidgetIcon />, color: '#4CAF50', label: 'Widgets' },
};

const MarketplacePage: React.FC = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState(0);
    const [items, setItems] = useState<MarketplaceItem[]>([]);
    const [bundles, setBundles] = useState<Bundle[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [userPurchases, setUserPurchases] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [creditBalance, setCreditBalance] = useState<number>(user?.credit_balance || 0);

    // Filters
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
    const [showPremiumOnly, setShowPremiumOnly] = useState(false);

    // Purchase dialog
    const [purchaseDialog, setPurchaseDialog] = useState<{
        open: boolean;
        item: MarketplaceItem | Bundle | null;
        type: 'item' | 'bundle';
    }>({ open: false, item: null, type: 'item' });
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
            const [itemsRes, bundlesRes, categoriesRes, purchasesRes] = await Promise.all([
                apiClient.get<{ items: MarketplaceItem[] }>('/marketplace/items', {
                    params: {
                        category: selectedCategory || undefined,
                        is_featured: showFeaturedOnly || undefined,
                        is_premium: showPremiumOnly || undefined,
                        search: searchQuery || undefined,
                    }
                }),
                apiClient.get<{ bundles: Bundle[] }>('/marketplace/bundles'),
                apiClient.get<{ categories: Category[] }>('/marketplace/categories'),
                apiClient.get<{ purchases: { item_id: number }[] }>('/marketplace/purchases'),
            ]);

            setItems(itemsRes.items || []);
            setBundles(bundlesRes.bundles || []);
            setCategories(categoriesRes.categories || []);
            setUserPurchases((purchasesRes.purchases || []).map((p) => p.item_id));
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to load marketplace');
        } finally {
            setLoading(false);
        }
    }, [selectedCategory, showFeaturedOnly, showPremiumOnly, searchQuery]);

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

    // Purchase handlers
    const handlePurchase = async () => {
        if (!purchaseDialog.item) return;

        setPurchasing(true);
        try {
            if (purchaseDialog.type === 'item') {
                await apiClient.post('/marketplace/purchase', {
                    item_id: (purchaseDialog.item as MarketplaceItem).id
                });
            } else {
                await apiClient.post('/marketplace/bundles/purchase', {
                    bundle_id: (purchaseDialog.item as Bundle).id
                });
            }

            setSnackbar({
                open: true,
                message: `Successfully purchased ${purchaseDialog.item.name}!`,
                severity: 'success'
            });
            setPurchaseDialog({ open: false, item: null, type: 'item' });
            refreshBalance(); // Refresh credit balance
            fetchData(); // Refresh purchases
        } catch (err: any) {
            setSnackbar({
                open: true,
                message: err.response?.data?.detail || 'Purchase failed',
                severity: 'error'
            });
        } finally {
            setPurchasing(false);
        }
    };

    // Check if user owns an item
    const isOwned = (itemId: number) => userPurchases.includes(itemId);

    // Render item card
    const renderItemCard = (item: MarketplaceItem) => {
        const owned = isOwned(item.id);
        const config = CATEGORY_CONFIG[item.category] || { icon: <WidgetIcon />, color: '#757575', label: item.category };

        return (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
                <Card
                    sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        position: 'relative',
                        border: item.is_featured ? '2px solid gold' : undefined,
                        opacity: owned ? 0.85 : 1,
                    }}
                >
                    {item.is_featured && (
                        <Chip
                            label="Featured"
                            color="warning"
                            size="small"
                            icon={<StarIcon />}
                            sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}
                        />
                    )}
                    {item.is_premium && (
                        <Chip
                            label="Premium"
                            color="secondary"
                            size="small"
                            icon={<PremiumIcon />}
                            sx={{ position: 'absolute', top: 8, left: 8, zIndex: 1 }}
                        />
                    )}

                    <Box
                        sx={{
                            p: 3,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            bgcolor: `${config.color}15`,
                        }}
                    >
                        <Box sx={{ color: config.color, fontSize: 48 }}>
                            {config.icon}
                        </Box>
                    </Box>

                    <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="h6" component="h3" noWrap>
                                {item.name}
                            </Typography>
                            {owned && (
                                <Tooltip title="You own this">
                                    <OwnedIcon color="success" fontSize="small" />
                                </Tooltip>
                            )}
                        </Box>

                        <Chip
                            label={config.label}
                            size="small"
                            sx={{ mb: 1, bgcolor: `${config.color}20`, color: config.color }}
                        />

                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                            {item.description}
                        </Typography>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Rating value={item.rating} precision={0.1} size="small" readOnly />
                                <Typography variant="caption" color="text.secondary">
                                    ({item.rating_count})
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <DownloadIcon fontSize="small" color="action" />
                                <Typography variant="caption" color="text.secondary">
                                    {item.download_count}
                                </Typography>
                            </Box>
                        </Box>
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', p: 2, pt: 0 }}>
                        <Chip
                            icon={<PriceIcon />}
                            label={`${item.price_credits} Credits`}
                            color="primary"
                            variant="outlined"
                        />
                        <Button
                            variant={owned ? "outlined" : "contained"}
                            color={owned ? "success" : "primary"}
                            disabled={owned}
                            startIcon={owned ? <OwnedIcon /> : <CartIcon />}
                            onClick={() => setPurchaseDialog({ open: true, item, type: 'item' })}
                        >
                            {owned ? 'Owned' : 'Buy'}
                        </Button>
                    </CardActions>
                </Card>
            </Grid>
        );
    };

    // Render bundle card
    const renderBundleCard = (bundle: Bundle) => (
        <Grid item xs={12} sm={6} md={4} key={bundle.id}>
            <Card
                sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    border: bundle.is_featured ? '2px solid gold' : undefined,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                }}
            >
                {bundle.discount_percent > 0 && (
                    <Chip
                        label={`${bundle.discount_percent}% OFF`}
                        color="error"
                        size="small"
                        sx={{ position: 'absolute', top: 8, right: 8 }}
                    />
                )}

                <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <BundleIcon sx={{ fontSize: 32 }} />
                        <Typography variant="h6" component="h3">
                            {bundle.name}
                        </Typography>
                    </Box>

                    <Typography variant="body2" sx={{ mb: 2, opacity: 0.9, minHeight: 40 }}>
                        {bundle.description}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="caption" sx={{ opacity: 0.7, textDecoration: 'line-through' }}>
                            {bundle.original_price} Credits
                        </Typography>
                    </Box>

                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        {bundle.price_credits} Credits
                    </Typography>

                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Valid for {bundle.valid_days} days
                    </Typography>
                </CardContent>

                <CardActions sx={{ p: 2, pt: 0 }}>
                    <Button
                        variant="contained"
                        fullWidth
                        sx={{
                            bgcolor: 'white',
                            color: '#667eea',
                            '&:hover': { bgcolor: '#f5f5f5' }
                        }}
                        startIcon={<CartIcon />}
                        onClick={() => setPurchaseDialog({ open: true, item: bundle, type: 'bundle' })}
                    >
                        Purchase Bundle
                    </Button>
                </CardActions>
            </Card>
        </Grid>
    );

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    🏪 Marketplace
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Enhance your experience with AI models, themes, widgets, and bundles
                </Typography>

                {/* Credit Balance */}
                <Paper sx={{ mt: 2, p: 2, display: 'inline-flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body1">Your Balance:</Typography>
                    <Chip
                        label={`${creditBalance.toLocaleString() || 0} Credits`}
                        color="primary"
                        sx={{ fontWeight: 'bold' }}
                    />
                </Paper>
            </Box>

            {/* Tabs */}
            <Tabs
                value={activeTab}
                onChange={(_, v) => setActiveTab(v)}
                sx={{ mb: 3 }}
            >
                <Tab icon={<AIIcon />} label="All Items" />
                <Tab icon={<BundleIcon />} label="Bundles" />
                <Tab icon={<OwnedIcon />} label="My Purchases" />
            </Tabs>

            {/* Filters (for Items tab) */}
            {activeTab === 0 && (
                <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <TextField
                        placeholder="Search items..."
                        size="small"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon />
                                </InputAdornment>
                            ),
                        }}
                        sx={{ minWidth: 250 }}
                    />

                    <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel>Category</InputLabel>
                        <Select
                            value={selectedCategory}
                            label="Category"
                            onChange={(e) => setSelectedCategory(e.target.value)}
                        >
                            <MenuItem value="">All Categories</MenuItem>
                            {categories.map((cat) => (
                                <MenuItem key={cat.category} value={cat.category}>
                                    {CATEGORY_CONFIG[cat.category]?.label || cat.category} ({cat.item_count})
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <Button
                        variant={showFeaturedOnly ? "contained" : "outlined"}
                        size="small"
                        startIcon={<StarIcon />}
                        onClick={() => setShowFeaturedOnly(!showFeaturedOnly)}
                    >
                        Featured
                    </Button>

                    <Button
                        variant={showPremiumOnly ? "contained" : "outlined"}
                        size="small"
                        color="secondary"
                        startIcon={<PremiumIcon />}
                        onClick={() => setShowPremiumOnly(!showPremiumOnly)}
                    >
                        Premium
                    </Button>
                </Box>
            )}

            {/* Error */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Content */}
            {loading ? (
                <Grid container spacing={3}>
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <Grid item xs={12} sm={6} md={4} key={i}>
                            <Skeleton variant="rectangular" height={300} />
                        </Grid>
                    ))}
                </Grid>
            ) : (
                <>
                    {/* Items Tab */}
                    {activeTab === 0 && (
                        <Grid container spacing={3}>
                            {items.length === 0 ? (
                                <Grid item xs={12}>
                                    <Alert severity="info">No items found</Alert>
                                </Grid>
                            ) : (
                                items.map(renderItemCard)
                            )}
                        </Grid>
                    )}

                    {/* Bundles Tab */}
                    {activeTab === 1 && (
                        <Grid container spacing={3}>
                            {bundles.length === 0 ? (
                                <Grid item xs={12}>
                                    <Alert severity="info">No bundles available</Alert>
                                </Grid>
                            ) : (
                                bundles.map(renderBundleCard)
                            )}
                        </Grid>
                    )}

                    {/* My Purchases Tab */}
                    {activeTab === 2 && (
                        <Box>
                            {userPurchases.length === 0 ? (
                                <Alert severity="info">
                                    You haven't purchased any items yet. Browse the marketplace to find something useful!
                                </Alert>
                            ) : (
                                <Grid container spacing={3}>
                                    {items.filter(item => isOwned(item.id)).map(renderItemCard)}
                                </Grid>
                            )}
                        </Box>
                    )}
                </>
            )}

            {/* Purchase Dialog */}
            <Dialog
                open={purchaseDialog.open}
                onClose={() => !purchasing && setPurchaseDialog({ open: false, item: null, type: 'item' })}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    Confirm Purchase
                </DialogTitle>
                <DialogContent>
                    {purchaseDialog.item && (
                        <Box>
                            <Typography variant="h6" gutterBottom>
                                {purchaseDialog.item.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                                {purchaseDialog.item.description}
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography>Price:</Typography>
                                <Typography fontWeight="bold">
                                    {purchaseDialog.item.price_credits} Credits
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography>Your Balance:</Typography>
                                <Typography>
                                    {creditBalance.toLocaleString() || 0} Credits
                                </Typography>
                            </Box>
                            <Divider sx={{ my: 2 }} />
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography>After Purchase:</Typography>
                                <Typography
                                    fontWeight="bold"
                                    color={(creditBalance || 0) >= purchaseDialog.item.price_credits ? 'success.main' : 'error.main'}
                                >
                                    {((creditBalance || 0) - purchaseDialog.item.price_credits).toLocaleString()} Credits
                                </Typography>
                            </Box>

                            {(creditBalance || 0) < purchaseDialog.item.price_credits && (
                                <Alert severity="error" sx={{ mt: 2 }}>
                                    Insufficient credits. You need {purchaseDialog.item.price_credits - (creditBalance || 0)} more credits.
                                </Alert>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={() => setPurchaseDialog({ open: false, item: null, type: 'item' })}
                        disabled={purchasing}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handlePurchase}
                        disabled={purchasing || (creditBalance || 0) < (purchaseDialog.item?.price_credits || 0)}
                        startIcon={<CartIcon />}
                    >
                        {purchasing ? 'Processing...' : 'Confirm Purchase'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={5000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
            >
                <Alert
                    severity={snackbar.severity}
                    onClose={() => setSnackbar({ ...snackbar, open: false })}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default MarketplacePage;
