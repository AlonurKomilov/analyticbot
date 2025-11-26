/**
 * useChannelAdminStatus Hook
 *
 * Custom hook to fetch and manage channel admin status.
 * Checks if bot/MTProto sessions have admin access to channels.
 */

import { useState, useCallback } from 'react';
import { apiClient } from '@/api/client';

export interface ChannelAdminStatus {
    bot_is_admin: boolean | null;
    mtproto_is_admin: boolean | null;
    mtproto_disabled?: boolean;
    is_inactive?: boolean;
    message?: string;
}

interface UseChannelAdminStatusReturn {
    adminStatus: Record<number, ChannelAdminStatus>;
    isLoading: boolean;
    error: string | null;
    fetchAdminStatus: () => Promise<void>;
    refreshAdminStatus: () => Promise<void>;
}

export const useChannelAdminStatus = (): UseChannelAdminStatusReturn => {
    const [adminStatus, setAdminStatus] = useState<Record<number, ChannelAdminStatus>>({});
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchAdminStatus = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response: any = await apiClient.get('/channels/admin-status/check-all');

            if (response && response.results) {
                const statusMap: Record<number, ChannelAdminStatus> = {};

                Object.values(response.results).forEach((result: any) => {
                    console.log('📊 Admin Status Result:', result); // DEBUG
                    statusMap[result.channel_id] = {
                        bot_is_admin: result.bot_is_admin,
                        mtproto_is_admin: result.mtproto_is_admin,
                        mtproto_disabled: result.mtproto_disabled,
                        is_inactive: result.is_inactive,
                        message: result.message
                    };
                });

                console.log('✅ Final Admin Status Map:', statusMap); // DEBUG
                setAdminStatus(statusMap);
            }
        } catch (err: any) {
            console.error('Failed to fetch admin status:', err);
            setError(err.message || 'Failed to fetch admin status');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const refreshAdminStatus = useCallback(async () => {
        await fetchAdminStatus();
    }, [fetchAdminStatus]);

    return {
        adminStatus,
        isLoading,
        error,
        fetchAdminStatus,
        refreshAdminStatus
    };
};

export default useChannelAdminStatus;
