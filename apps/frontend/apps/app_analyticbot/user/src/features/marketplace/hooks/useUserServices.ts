/**
 * useUserServices Hook
 * 
 * Manage user's service subscriptions.
 * 
 * @module features/marketplace/hooks/useUserServices
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  getUserSubscriptions, 
  getActiveSubscriptions,
  cancelSubscription,
  toggleAutoRenew,
} from '../api/services';
import type { UserSubscription } from '../types';

// Local alias for readability
type ServiceSubscription = UserSubscription;

interface UseUserServicesOptions {
  includeExpired?: boolean;
  activeOnly?: boolean;
  autoFetch?: boolean;
}

interface UseUserServicesResult {
  subscriptions: ServiceSubscription[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  cancel: (subscriptionId: number, reason?: string) => Promise<boolean>;
  setAutoRenew: (subscriptionId: number, autoRenew: boolean) => Promise<boolean>;
  isSubscribed: (serviceKey: string) => boolean;
  getSubscription: (serviceKey: string) => ServiceSubscription | undefined;
}

/**
 * Hook for managing user's service subscriptions
 */
export function useUserServices(options: UseUserServicesOptions = {}): UseUserServicesResult {
  const { 
    includeExpired = false, 
    activeOnly = false,
    autoFetch = true,
  } = options;

  const [subscriptions, setSubscriptions] = useState<ServiceSubscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptions = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = activeOnly 
        ? await getActiveSubscriptions()
        : await getUserSubscriptions(includeExpired);
      setSubscriptions(data);
    } catch (err) {
      console.error('Failed to fetch subscriptions:', err);
      setError(err instanceof Error ? err.message : 'Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  }, [includeExpired, activeOnly]);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      fetchSubscriptions();
    }
  }, [fetchSubscriptions, autoFetch]);

  // Cancel a subscription
  const cancel = useCallback(async (subscriptionId: number, reason?: string): Promise<boolean> => {
    try {
      await cancelSubscription({ subscription_id: subscriptionId, reason });
      // Refresh subscriptions after cancellation
      await fetchSubscriptions();
      return true;
    } catch (err) {
      console.error('Failed to cancel subscription:', err);
      return false;
    }
  }, [fetchSubscriptions]);

  // Toggle auto-renew
  const setAutoRenew = useCallback(async (subscriptionId: number, autoRenew: boolean): Promise<boolean> => {
    try {
      await toggleAutoRenew(subscriptionId, autoRenew);
      // Update local state
      setSubscriptions(prev => 
        prev.map(sub => 
          sub.id === subscriptionId 
            ? { ...sub, auto_renew: autoRenew }
            : sub
        )
      );
      return true;
    } catch (err) {
      console.error('Failed to toggle auto-renew:', err);
      return false;
    }
  }, []);

  // Check if subscribed to a service
  const isSubscribed = useCallback((serviceKey: string): boolean => {
    return subscriptions.some(
      sub => sub.service_key === serviceKey && sub.status === 'active'
    );
  }, [subscriptions]);

  // Get subscription by service key
  const getSubscription = useCallback((serviceKey: string): ServiceSubscription | undefined => {
    return subscriptions.find(sub => sub.service_key === serviceKey);
  }, [subscriptions]);

  return {
    subscriptions,
    loading,
    error,
    refetch: fetchSubscriptions,
    cancel,
    setAutoRenew,
    isSubscribed,
    getSubscription,
  };
}
