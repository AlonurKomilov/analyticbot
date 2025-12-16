/**
 * 💰 Price Formatting Utilities
 *
 * Helpers for displaying prices, savings, and billing information
 */

import { MarketplaceItem, BillingCycle } from '../types';

/**
 * Format credit amount with commas
 */
export const formatCredits = (amount: number): string => {
    return amount.toLocaleString();
};

/**
 * Get price for item based on billing cycle
 */
export const getPrice = (item: MarketplaceItem, billingCycle: BillingCycle): number => {
    // For one-time purchases, always return the base price
    if (item.pricing_model === 'one_time') {
        return item.price_credits || item.price_monthly || 0;
    }

    // For subscriptions, return based on billing cycle
    if (billingCycle === 'yearly' && item.price_yearly) {
        return item.price_yearly;
    }
    return item.price_credits || item.price_monthly || 0;
};

/**
 * Get price display text
 */
export const getPriceDisplay = (item: MarketplaceItem, billingCycle: BillingCycle): string => {
    const price = getPrice(item, billingCycle);
    const formattedPrice = formatCredits(price);

    if (item.pricing_model === 'one_time') {
        return `${formattedPrice} Credits`;
    }

    if (billingCycle === 'yearly') {
        return `${formattedPrice} Credits/year`;
    }
    return `${formattedPrice} Credits/month`;
};

/**
 * Calculate savings percentage for yearly billing
 */
export const calculateYearlySavings = (item: MarketplaceItem): number => {
    if (!item.price_yearly) return 0;
    
    const monthlyPrice = item.price_credits || item.price_monthly || 0;
    const monthlyTotal = monthlyPrice * 12;
    const yearlySavings = monthlyTotal - item.price_yearly;
    
    if (yearlySavings <= 0) return 0;
    return Math.round((yearlySavings / monthlyTotal) * 100);
};

/**
 * Get savings display text
 */
export const getSavingsDisplay = (item: MarketplaceItem): string | null => {
    const savings = calculateYearlySavings(item);
    if (savings <= 0) return null;
    return `Save ${savings}%`;
};

/**
 * Check if user can afford item
 */
export const canAfford = (item: MarketplaceItem, balance: number, billingCycle: BillingCycle): boolean => {
    const price = getPrice(item, billingCycle);
    return balance >= price;
};

/**
 * Calculate remaining balance after purchase
 */
export const getRemainingBalance = (item: MarketplaceItem, balance: number, billingCycle: BillingCycle): number => {
    const price = getPrice(item, billingCycle);
    return balance - price;
};
