/**
 * useServiceAccess Hook
 * 
 * Check if user has access to specific services.
 * 
 * @module features/marketplace/hooks/useServiceAccess
 */

import { useState, useEffect, useCallback } from 'react';
import { checkServiceAccess, checkServiceQuota, getUserFeatures } from '../api/services';

interface QuotaInfo {
  limit: number | null;
  used: number;
  remaining: number | null;
  exceeded: boolean;
}

interface UseServiceAccessResult {
  hasAccess: boolean;
  quota: QuotaInfo | null;
  loading: boolean;
  error: string | null;
  checkAccess: () => Promise<boolean>;
  checkQuota: (type?: 'daily' | 'monthly') => Promise<QuotaInfo | null>;
}

/**
 * Hook for checking access to a specific service
 */
export function useServiceAccess(serviceKey: string): UseServiceAccessResult {
  const [hasAccess, setHasAccess] = useState(false);
  const [quota, setQuota] = useState<QuotaInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAccess = useCallback(async (): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await checkServiceAccess(serviceKey);
      setHasAccess(result.has_access);
      return result.has_access;
    } catch (err) {
      console.error('Failed to check service access:', err);
      setError(err instanceof Error ? err.message : 'Failed to check access');
      return false;
    } finally {
      setLoading(false);
    }
  }, [serviceKey]);

  const fetchQuota = useCallback(async (type: 'daily' | 'monthly' = 'daily'): Promise<QuotaInfo | null> => {
    try {
      const result = await checkServiceQuota(serviceKey, type);
      const quotaInfo: QuotaInfo = {
        limit: result.limit,
        used: result.used,
        remaining: result.remaining,
        exceeded: result.exceeded,
      };
      setQuota(quotaInfo);
      return quotaInfo;
    } catch (err) {
      console.error('Failed to check service quota:', err);
      return null;
    }
  }, [serviceKey]);

  // Fetch on mount
  useEffect(() => {
    fetchAccess();
  }, [fetchAccess]);

  return {
    hasAccess,
    quota,
    loading,
    error,
    checkAccess: fetchAccess,
    checkQuota: fetchQuota,
  };
}

/**
 * Hook for getting all user's feature access
 */
export function useUserFeatures() {
  const [features, setFeatures] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFeatures = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getUserFeatures();
      setFeatures(result.features);
    } catch (err) {
      console.error('Failed to fetch user features:', err);
      setError(err instanceof Error ? err.message : 'Failed to load features');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFeatures();
  }, [fetchFeatures]);

  const hasFeature = useCallback((serviceKey: string): boolean => {
    return features.includes(serviceKey);
  }, [features]);

  return {
    features,
    loading,
    error,
    refresh: fetchFeatures,
    hasFeature,
  };
}
