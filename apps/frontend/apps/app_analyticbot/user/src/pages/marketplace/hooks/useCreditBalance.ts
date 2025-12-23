/**
 * 💰 Credit Balance Hook
 *
 * Manages user credit balance with refresh capability
 */

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/api/client';

export const useCreditBalance = () => {
    const { user } = useAuth();
    const [balance, setBalance] = useState<number>(user?.credit_balance || 0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Refresh balance from API
    const refreshBalance = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get<{ balance: number }>('/credits/balance');
            setBalance(response.balance);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch balance');
            console.error('Failed to refresh balance:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Initialize balance from user context
    useEffect(() => {
        if (user?.credit_balance !== undefined) {
            setBalance(user.credit_balance);
        }
    }, [user?.credit_balance]);

    return {
        balance,
        loading,
        error,
        refreshBalance,
        setBalance, // Allow manual updates after purchases
    };
};
