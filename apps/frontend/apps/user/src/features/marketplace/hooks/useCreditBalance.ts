/**
 * useCreditBalance Hook
 * 
 * Fetch and manage user's credit balance.
 * 
 * @module features/marketplace/hooks/useCreditBalance
 */

import { useState, useEffect, useCallback } from 'react';
import { getCreditBalance, type CreditBalanceData } from '../api/credits';

// Local type alias for backward compatibility
type CreditBalance = CreditBalanceData;

interface UseCreditBalanceResult {
  balance: number;
  fullBalance: CreditBalance | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

/**
 * Hook for fetching and managing credit balance
 */
export function useCreditBalance(): UseCreditBalanceResult {
  const [fullBalance, setFullBalance] = useState<CreditBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBalance = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getCreditBalance();
      setFullBalance(data);
    } catch (err) {
      console.error('Failed to fetch credit balance:', err);
      setError(err instanceof Error ? err.message : 'Failed to load balance');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchBalance();
  }, [fetchBalance]);

  return {
    balance: fullBalance?.balance ?? 0,
    fullBalance,
    loading,
    error,
    refresh: fetchBalance,
  };
}
