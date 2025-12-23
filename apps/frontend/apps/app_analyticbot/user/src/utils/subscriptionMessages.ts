/**
 * Subscription Status Messages
 *
 * Provides user-friendly messages and action guidance for subscription statuses
 */

import { SubscriptionStatus } from '@/types';

/**
 * Status message interface
 */
export interface StatusMessage {
    title: string;
    description: string;
    action?: string;
    severity: 'success' | 'info' | 'warning' | 'error';
}

/**
 * Get subscription status message
 *
 * Provides user-friendly messaging for each subscription status
 *
 * @param status - The subscription status
 * @param daysUntilDue - Optional days until payment is due (for past_due status)
 * @returns StatusMessage object with title, description, action, and severity
 */
export const getSubscriptionStatusMessage = (
    status: SubscriptionStatus,
    daysUntilDue?: number
): StatusMessage => {
    switch (status) {
        case 'active':
            return {
                title: 'Subscription Active',
                description: 'Your subscription is active and all features are available.',
                severity: 'success'
            };

        case 'trialing':
            return {
                title: 'Trial Period',
                description: 'You are currently in your free trial period. Enjoy full access to all features!',
                action: 'Upgrade to continue after trial',
                severity: 'info'
            };

        case 'past_due':
            return {
                title: 'Payment Past Due',
                description: daysUntilDue !== undefined
                    ? `Your payment is overdue. Your subscription will be canceled in ${daysUntilDue} day${daysUntilDue !== 1 ? 's' : ''} if payment is not received.`
                    : 'Your payment is overdue. Please update your payment method to avoid service interruption.',
                action: 'Update payment method',
                severity: 'warning'
            };

        case 'unpaid':
            return {
                title: 'Payment Required',
                description: 'Your subscription has unpaid invoices. Please settle your balance to continue using the service.',
                action: 'Pay now',
                severity: 'warning'
            };

        case 'incomplete':
            return {
                title: 'Subscription Incomplete',
                description: 'Your subscription setup is incomplete. Please complete the payment process to activate your subscription.',
                action: 'Complete payment',
                severity: 'error'
            };

        case 'canceled':
            return {
                title: 'Subscription Canceled',
                description: 'Your subscription has been canceled. You will have access until the end of your current billing period.',
                action: 'Reactivate subscription',
                severity: 'error'
            };

        default:
            return {
                title: 'Unknown Status',
                description: 'Subscription status is unknown. Please contact support.',
                action: 'Contact support',
                severity: 'error'
            };
    }
};

/**
 * Check if subscription status requires user action
 *
 * @param status - The subscription status
 * @returns true if user action is required
 */
export const requiresUserAction = (status: SubscriptionStatus): boolean => {
    return ['past_due', 'unpaid', 'incomplete'].includes(status);
};

/**
 * Get action button text for subscription status
 *
 * @param status - The subscription status
 * @returns Action button text or undefined if no action needed
 */
export const getActionButtonText = (status: SubscriptionStatus): string | undefined => {
    const message = getSubscriptionStatusMessage(status);
    return message.action;
};

/**
 * Check if subscription allows feature access
 *
 * @param status - The subscription status
 * @returns true if features should be accessible
 */
export const allowsFeatureAccess = (status: SubscriptionStatus): boolean => {
    return ['active', 'trialing', 'past_due'].includes(status);
};

export default {
    getSubscriptionStatusMessage,
    requiresUserAction,
    getActionButtonText,
    allowsFeatureAccess
};
