/**
 * 🛒 Purchase Dialog Component
 *
 * Unified purchase confirmation dialog for all marketplace items
 */

import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Box,
    Typography,
    Button,
    Divider,
    Alert,
    ToggleButtonGroup,
    ToggleButton,
    Chip,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
} from '@mui/material';
import {
    ShoppingCart,
    CheckCircle,
} from '@mui/icons-material';
import { MarketplaceItem, BillingCycle } from '../types';
import { getPrice, formatCredits, getSavingsDisplay } from '../utils/priceFormatter';

interface PurchaseDialogProps {
    open: boolean;
    item: MarketplaceItem | null;
    balance: number;
    onClose: () => void;
    onConfirm: (item: MarketplaceItem, billingCycle: BillingCycle) => void;
    purchasing?: boolean;
}

export const PurchaseDialog: React.FC<PurchaseDialogProps> = ({
    open,
    item,
    balance,
    onClose,
    onConfirm,
    purchasing = false,
}) => {
    const [billingCycle, setBillingCycle] = useState<BillingCycle>('monthly');

    if (!item) return null;

    const isSubscription = item.pricing_model === 'subscription';
    const price = getPrice(item, billingCycle);
    const canAfford = balance >= price;
    const remainingBalance = balance - price;
    const savingsDisplay = getSavingsDisplay(item);
    const showBillingToggle = isSubscription && item.price_yearly;

    const handleConfirm = () => {
        onConfirm(item, billingCycle);
    };

    return (
        <Dialog
            open={open}
            onClose={purchasing ? undefined : onClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                sx: {
                    bgcolor: '#1a1d2e',
                    backgroundImage: 'none',
                }
            }}
        >
            <DialogTitle sx={{ pb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <ShoppingCart sx={{ fontSize: 28 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {isSubscription ? 'Subscribe to Service' : 'Purchase Item'}
                    </Typography>
                </Box>
            </DialogTitle>

            <DialogContent sx={{ pt: 2 }}>
                {/* Item Details */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, fontSize: '1.25rem' }}>
                        {item.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                        {item.short_description || item.description}
                    </Typography>
                </Box>

                {/* Features (if available) */}
                {item.features && item.features.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mb: 1.5 }}>
                            Includes:
                        </Typography>
                        <List dense disablePadding>
                            {item.features.map((feature, index) => (
                                <ListItem key={index} disablePadding sx={{ py: 0.75 }}>
                                    <ListItemIcon sx={{ minWidth: 36 }}>
                                        <CheckCircle sx={{ color: '#4ade80', fontSize: 22 }} />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={feature}
                                        primaryTypographyProps={{ 
                                            variant: 'body2',
                                            sx: { fontWeight: 400 }
                                        }}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}

                {/* Billing Cycle Toggle (for subscriptions with yearly option) */}
                {showBillingToggle && (
                    <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
                        <ToggleButtonGroup
                            value={billingCycle}
                            exclusive
                            onChange={(_, value) => value && setBillingCycle(value)}
                            sx={{
                                bgcolor: '#2d3142',
                                '& .MuiToggleButton-root': {
                                    border: 'none',
                                    color: '#9ca3af',
                                    textTransform: 'uppercase',
                                    fontSize: '0.875rem',
                                    fontWeight: 600,
                                    px: 3,
                                    py: 1,
                                    '&.Mui-selected': {
                                        bgcolor: '#374151',
                                        color: 'white',
                                    },
                                },
                            }}
                        >
                            <ToggleButton value="monthly">
                                Monthly
                            </ToggleButton>
                            <ToggleButton value="yearly">
                                Yearly
                            </ToggleButton>
                            {savingsDisplay && billingCycle === 'yearly' && (
                                <Chip
                                    label={savingsDisplay.toUpperCase()}
                                    size="small"
                                    sx={{
                                        position: 'absolute',
                                        right: -8,
                                        top: -8,
                                        bgcolor: '#10b981',
                                        color: 'white',
                                        fontWeight: 700,
                                        fontSize: '0.75rem',
                                        height: 24,
                                    }}
                                />
                            )}
                        </ToggleButtonGroup>
                    </Box>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Pricing Breakdown */}
                <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography>Price:</Typography>
                        <Typography fontWeight="bold">
                            {formatCredits(price)} Credits
                            {isSubscription && ` / ${billingCycle === 'yearly' ? 'year' : 'month'}`}
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography>Your Balance:</Typography>
                        <Typography>
                            {formatCredits(balance)} Credits
                        </Typography>
                    </Box>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography fontWeight="bold">After Purchase:</Typography>
                        <Typography
                            fontWeight="bold"
                            color={canAfford ? 'success.main' : 'error.main'}
                        >
                            {formatCredits(remainingBalance)} Credits
                        </Typography>
                    </Box>
                </Box>

                {/* Insufficient Credits Warning */}
                {!canAfford && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                        Insufficient credits. You need {formatCredits(price - balance)} more credits.
                    </Alert>
                )}

                {/* Subscription Note */}
                {isSubscription && (
                    <Alert 
                        severity="info" 
                        sx={{ 
                            mt: 2,
                            bgcolor: 'rgba(59, 130, 246, 0.1)',
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            '& .MuiAlert-icon': {
                                color: '#3b82f6'
                            }
                        }}
                    >
                        This is a recurring subscription. You'll be charged {formatCredits(price)} credits {billingCycle === 'yearly' ? 'annually' : 'monthly'}.
                    </Alert>
                )}
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 3, pt: 2 }}>
                <Button
                    onClick={onClose}
                    disabled={purchasing}
                    sx={{
                        color: '#9ca3af',
                        textTransform: 'none',
                        fontSize: '1rem',
                        fontWeight: 500,
                    }}
                >
                    Cancel
                </Button>
                <Button
                    variant="contained"
                    onClick={handleConfirm}
                    disabled={purchasing || !canAfford}
                    startIcon={<ShoppingCart />}
                    sx={{
                        bgcolor: '#3b82f6',
                        textTransform: 'none',
                        fontSize: '1rem',
                        fontWeight: 600,
                        px: 3,
                        py: 1.25,
                        '&:hover': {
                            bgcolor: '#2563eb',
                        },
                        '&:disabled': {
                            bgcolor: '#374151',
                            color: '#6b7280',
                        },
                    }}
                >
                    {purchasing ? 'Processing...' : 'Confirm Purchase'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};
