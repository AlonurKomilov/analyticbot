/**
 * 🏪 Unified Marketplace Page
 *
 * Professional, scalable marketplace with unified architecture:
 * - One page for all categories (AI Models, Themes, Services, Widgets, Bundles)
 * - Unified card design
 * - Shared state management
 * - Easy to extend with new categories
 */

import React, { useState, useMemo } from 'react';
import {
    Container,
    Typography,
    Box,
    Grid,
    Skeleton,
    Alert,
    Snackbar,
} from '@mui/material';
import { MarketplaceCategory, BillingCycle, MarketplaceItem, ServiceSubcategory } from './marketplace/types';
import { useMarketplaceData } from './marketplace/hooks/useMarketplaceData';
import { useCreditBalance } from './marketplace/hooks/useCreditBalance';
import { usePurchase } from './marketplace/hooks/usePurchase';
import { MarketplaceCard } from './marketplace/components/MarketplaceCard';
import { CategoryFilter } from './marketplace/components/CategoryFilter';
import { ServiceSubcategoryFilter } from './marketplace/components/ServiceSubcategoryFilter';
import { SearchBar } from './marketplace/components/SearchBar';
import { CreditBalance } from './marketplace/components/CreditBalance';
import { PurchaseDialog } from './marketplace/components/PurchaseDialog';
import { ItemDetailModal } from './marketplace/components/ItemDetailModal';
import { CATEGORY_CONFIGS, mapBackendToServiceSubcategory } from './marketplace/utils/categoryConfig';

const MarketplacePage: React.FC = () => {
    // State
    const [selectedCategory, setSelectedCategory] = useState<MarketplaceCategory>('services');
    const [selectedSubcategory, setSelectedSubcategory] = useState<ServiceSubcategory>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [billingCycle] = useState<BillingCycle>('monthly');
    const [purchaseDialogOpen, setPurchaseDialogOpen] = useState(false);
    const [detailModalOpen, setDetailModalOpen] = useState(false);
    const [selectedItem, setSelectedItem] = useState<MarketplaceItem | null>(null);
    const [snackbar, setSnackbar] = useState<{
        open: boolean;
        message: string;
        severity: 'success' | 'error' | 'info';
    }>({ open: false, message: '', severity: 'info' });

    // Hooks
    const { balance, refreshBalance, loading: balanceLoading } = useCreditBalance();
    const { items, loading, error, refetch } = useMarketplaceData({
        category: selectedCategory,
        searchQuery,
    });
    const { purchaseItem, purchasing } = usePurchase();

    // Check if current category supports subscriptions
    const isServicesCategory = selectedCategory === 'services';

    // Filter items by subcategory (for services)
    const filteredItems = useMemo(() => {
        if (selectedCategory !== 'services' || selectedSubcategory === 'all') {
            return items;
        }
        
        // Filter by service subcategory (bot, mtproto, analytics, ai)
        return items.filter(item => {
            const itemSubcategory = mapBackendToServiceSubcategory(item.category);
            return itemSubcategory === selectedSubcategory;
        });
    }, [items, selectedCategory, selectedSubcategory]);

    // Calculate subcategory counts for services
    const subcategoryCounts = useMemo((): Record<ServiceSubcategory, number> => {
        const counts: Record<ServiceSubcategory, number> = {
            all: items.length,
            bot: 0,
            mtproto: 0,
            ai: 0,
        };
        
        if (selectedCategory !== 'services') return counts;
        
        items.forEach(item => {
            const subcategory = mapBackendToServiceSubcategory(item.category);
            if (subcategory !== 'all') {
                counts[subcategory]++;
            }
        });
        
        return counts;
    }, [items, selectedCategory]);

    // Handlers
    const handleCategoryChange = (category: MarketplaceCategory) => {
        setSelectedCategory(category);
        setSelectedSubcategory('all'); // Reset subcategory when category changes
        setSearchQuery(''); // Clear search when changing category
    };

    const handleSubcategoryChange = (subcategory: ServiceSubcategory) => {
        setSelectedSubcategory(subcategory);
    };

    const handlePurchaseClick = (item: MarketplaceItem) => {
        setSelectedItem(item);
        setPurchaseDialogOpen(true);
    };

    const handleViewDetails = (item: MarketplaceItem) => {
        setSelectedItem(item);
        setDetailModalOpen(true);
    };

    const handlePurchaseConfirm = async (item: MarketplaceItem, cycle: BillingCycle) => {
        try {
            const result = await purchaseItem(item, cycle);
            
            // Update balance
            if (result.new_balance !== undefined) {
                refreshBalance();
            }

            // Show success message
            setSnackbar({
                open: true,
                message: result.message,
                severity: 'success',
            });

            // Close dialog
            setPurchaseDialogOpen(false);
            setSelectedItem(null);

            // Refresh items to update ownership status
            refetch();
        } catch (err: any) {
            setSnackbar({
                open: true,
                message: err.message || 'Purchase failed',
                severity: 'error',
            });
        }
    };

    const handleDialogClose = () => {
        if (!purchasing) {
            setPurchaseDialogOpen(false);
            setSelectedItem(null);
        }
    };

    // Filter items by search (additional client-side filtering on top of subcategory)
    const searchFilteredItems = filteredItems.filter(item => {
        if (!searchQuery) return true;
        const query = searchQuery.toLowerCase();
        return (
            item.name.toLowerCase().includes(query) ||
            item.description.toLowerCase().includes(query)
        );
    });

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    🏪 Marketplace
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Discover and purchase premium items, themes, and services for your bot
                </Typography>
            </Box>

            {/* Credit Balance */}
            <CreditBalance
                balance={balance}
                onRefresh={refreshBalance}
                refreshing={balanceLoading}
            />

            {/* Search Bar */}
            <Box sx={{ mb: 3 }}>
                <SearchBar
                    value={searchQuery}
                    onChange={setSearchQuery}
                    placeholder={`Search ${CATEGORY_CONFIGS[selectedCategory].label.toLowerCase()}...`}
                />
            </Box>

            {/* Category Filter */}
            <CategoryFilter
                selectedCategory={selectedCategory}
                onCategoryChange={handleCategoryChange}
            />

            {/* Service Subcategory Filter (only for services category) */}
            {isServicesCategory && (
                <ServiceSubcategoryFilter
                    selectedSubcategory={selectedSubcategory}
                    onSubcategoryChange={handleSubcategoryChange}
                    itemCounts={subcategoryCounts}
                />
            )}

            {/* Error Alert */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => refetch()}>
                    {error}
                </Alert>
            )}

            {/* Items Grid */}
            {loading ? (
                <Grid container spacing={3}>
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
                            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
                        </Grid>
                    ))}
                </Grid>
            ) : searchFilteredItems.length === 0 ? (
                <Alert 
                    severity="info" 
                    sx={{ 
                        textAlign: 'center',
                        py: 6,
                    }}
                >
                    <Typography variant="h6" gutterBottom>
                        {searchQuery 
                            ? `No items found for "${searchQuery}"`
                            : selectedCategory === 'services'
                                ? 'No services available'
                                : '🚀 Coming Soon!'
                        }
                    </Typography>
                    {!searchQuery && selectedCategory !== 'services' && (
                        <Typography variant="body2" color="text.secondary">
                            We're working on adding {CATEGORY_CONFIGS[selectedCategory].label.toLowerCase()} to the marketplace.
                            <br />
                            Check back soon for amazing new items!
                        </Typography>
                    )}
                </Alert>
            ) : (
                <Grid container spacing={3}>
                    {searchFilteredItems.map((item) => (
                        <Grid item xs={12} sm={6} md={4} lg={3} key={item.unique_key || `${item.category}-${item.id}`}>
                            <MarketplaceCard
                                item={item}
                                billingCycle={billingCycle}
                                onPurchase={handlePurchaseClick}
                                onViewDetails={handleViewDetails}
                            />
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Item Detail Modal */}
            <ItemDetailModal
                open={detailModalOpen}
                item={selectedItem}
                billingCycle={billingCycle}
                onClose={() => setDetailModalOpen(false)}
                onPurchase={handlePurchaseClick}
            />

            {/* Purchase Dialog */}
            <PurchaseDialog
                open={purchaseDialogOpen}
                item={selectedItem}
                balance={balance}
                onClose={handleDialogClose}
                onConfirm={handlePurchaseConfirm}
                purchasing={purchasing}
            />

            {/* Snackbar for notifications */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={5000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert
                    severity={snackbar.severity}
                    onClose={() => setSnackbar({ ...snackbar, open: false })}
                    sx={{ width: '100%' }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default MarketplacePage;
