/**
 * 📋 Item Detail Modal
 *
 * Shows full details about a marketplace item before purchase
 */

import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Box,
    Typography,
    Button,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Rating,
    Divider,
    IconButton,
    Grid,
} from '@mui/material';
import {
    Close as CloseIcon,
    CheckCircle,
    Download,
    Star,
    WorkspacePremium,
    ShoppingCart,
    TrendingUp,
} from '@mui/icons-material';
import { MarketplaceItem, BillingCycle } from '../types';
import { getCategoryConfig, getUseCaseConfig } from '../utils/categoryConfig';
import { getPriceDisplay, getSavingsDisplay } from '../utils/priceFormatter';

interface ItemDetailModalProps {
    open: boolean;
    item: MarketplaceItem | null;
    billingCycle: BillingCycle;
    onClose: () => void;
    onPurchase: (item: MarketplaceItem) => void;
}

export const ItemDetailModal: React.FC<ItemDetailModalProps> = ({
    open,
    item,
    billingCycle,
    onClose,
    onPurchase,
}) => {
    if (!item) return null;

    const categoryConfig = getCategoryConfig(item.category);
    const priceDisplay = getPriceDisplay(item, billingCycle);
    const savingsDisplay = getSavingsDisplay(item);
    const isOwned = item.user_owned || item.user_subscribed;

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
        >
            <DialogTitle>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box
                            sx={{
                                width: 48,
                                height: 48,
                                borderRadius: 2,
                                bgcolor: categoryConfig.color,
                                color: 'white',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            {/* Icon placeholder */}
                        </Box>
                        <Box>
                            <Typography variant="h5" component="h2">
                                {item.name}
                            </Typography>
                            <Chip
                                label={categoryConfig.label}
                                size="small"
                                sx={{
                                    bgcolor: `${categoryConfig.color}20`,
                                    color: categoryConfig.color,
                                }}
                            />
                        </Box>
                    </Box>
                    <IconButton onClick={onClose} size="small">
                        <CloseIcon />
                    </IconButton>
                </Box>
            </DialogTitle>

            <DialogContent dividers>
                {/* Badges */}
                <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
                    {item.is_featured && (
                        <Chip label="Featured" icon={<Star />} color="warning" size="small" />
                    )}
                    {item.is_premium && (
                        <Chip label="Premium" icon={<WorkspacePremium />} color="secondary" size="small" />
                    )}
                    {item.is_new && (
                        <Chip label="New" color="success" size="small" />
                    )}
                    {item.is_beta && (
                        <Chip label="Beta" color="warning" size="small" />
                    )}
                    {isOwned && (
                        <Chip label={item.pricing_model === 'subscription' ? 'Subscribed' : 'Owned'} icon={<CheckCircle />} color="success" size="small" />
                    )}
                </Box>

                {/* Goal-Oriented Use Cases (What's this good for?) */}
                {item.use_cases && item.use_cases.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                            💡 What's this good for?
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {item.use_cases.map((useCase) => {
                                const config = getUseCaseConfig(useCase);
                                return (
                                    <Chip
                                        key={useCase}
                                        label={config.label}
                                        size="small"
                                        icon={<TrendingUp />}
                                        sx={{
                                            bgcolor: `${config.color}15`,
                                            color: config.color,
                                            border: `1px solid ${config.color}40`,
                                            fontWeight: 500,
                                        }}
                                    />
                                );
                            })}
                        </Box>
                    </Box>
                )}

                {/* Description */}
                <Typography variant="body1" paragraph>
                    {item.description}
                </Typography>

                {/* Features */}
                {item.features && item.features.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Includes:
                        </Typography>
                        <List dense>
                            {item.features.map((feature, index) => (
                                <ListItem key={index} disablePadding sx={{ py: 0.5 }}>
                                    <ListItemIcon sx={{ minWidth: 36 }}>
                                        <CheckCircle color="success" />
                                    </ListItemIcon>
                                    <ListItemText primary={feature} />
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}

                {/* Stats */}
                {(item.rating || item.download_count || item.active_subscriptions) && (
                    <Box sx={{ mb: 3 }}>
                        <Divider sx={{ mb: 2 }} />
                        <Grid container spacing={3}>
                            {item.rating && (
                                <Grid item xs={12} sm={4}>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        Rating
                                    </Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <Rating value={item.rating} precision={0.1} size="small" readOnly />
                                        <Typography variant="body2">
                                            {item.rating.toFixed(1)} ({item.rating_count || 0})
                                        </Typography>
                                    </Box>
                                </Grid>
                            )}
                            {item.download_count && (
                                <Grid item xs={12} sm={4}>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        Downloads
                                    </Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <Download fontSize="small" />
                                        <Typography variant="body2">
                                            {item.download_count.toLocaleString()}
                                        </Typography>
                                    </Box>
                                </Grid>
                            )}
                            {item.active_subscriptions && (
                                <Grid item xs={12} sm={4}>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        Active Users
                                    </Typography>
                                    <Typography variant="body2">
                                        {item.active_subscriptions.toLocaleString()}
                                    </Typography>
                                </Grid>
                            )}
                        </Grid>
                    </Box>
                )}

                {/* Pricing */}
                <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="h5" color="primary" sx={{ fontWeight: 600 }}>
                            {priceDisplay}
                        </Typography>
                        {savingsDisplay && billingCycle === 'yearly' && (
                            <Chip label={savingsDisplay} color="success" size="small" />
                        )}
                    </Box>
                </Box>
            </DialogContent>

            <DialogActions sx={{ p: 3 }}>
                <Button onClick={onClose} color="inherit">
                    Close
                </Button>
                <Button
                    variant="contained"
                    size="large"
                    disabled={isOwned}
                    onClick={() => {
                        onClose();
                        onPurchase(item);
                    }}
                    startIcon={<ShoppingCart />}
                    sx={{
                        bgcolor: categoryConfig.color,
                        '&:hover': { bgcolor: categoryConfig.color, opacity: 0.9 },
                    }}
                >
                    {isOwned ? (item.pricing_model === 'subscription' ? 'Subscribed' : 'Owned') : 'Purchase Now'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};
