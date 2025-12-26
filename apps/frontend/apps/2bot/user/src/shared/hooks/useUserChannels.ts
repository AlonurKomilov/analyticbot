/**
 * 🔐 User Channels Hooks
 *
 * Hooks for managing user channels with authentication.
 * Provides channel selection, creation, and management functionality.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useAuthenticatedDataProvider } from './useAuthenticatedDataSource';
import { apiClient } from '@/api/client';
import { logger } from '@/utils/logger';

// Global request deduplication map
// Prevents multiple simultaneous requests to the same endpoint
const activeRequests = new Map<string, Promise<any>>();

/**
 * Channel interface
 */
export interface Channel {
    id: number | string;
    name?: string;
    title?: string;
    username?: string;
    type?: string;
    [key: string]: any;
}

/**
 * User channels hook options
 */
export interface UseUserChannelsOptions {
    autoFetch?: boolean;
    onChannelChange?: ((channel: Channel | null) => void) | null;
}

/**
 * User channels return type
 */
export interface UseUserChannelsReturn {
    channels: Channel[];
    selectedChannel: Channel | null;
    loading: boolean;
    error: string | null;
    lastFetch: string | null;
    retrying: boolean;
    fetchChannels: () => Promise<void>;
    retryFetch: () => Promise<void>;
    createChannel: (channelData: Partial<Channel>) => Promise<Channel>;
    selectChannel: (channel: Channel | null) => void;
    getChannel: (channelId: number | string) => Promise<Channel>;
    user: any;
    isAuthenticated: boolean;
}

/**
 * Hook to fetch and manage user's channels
 * @param options - Hook options
 * @returns User channels data and management functions
 */
export const useUserChannels = (options: UseUserChannelsOptions = {}): UseUserChannelsReturn => {
    const { autoFetch = true, onChannelChange = null } = options;
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();

    const [channels, setChannels] = useState<Channel[]>([]);
    const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastFetch, setLastFetch] = useState<string | null>(null);
    const [retrying, setRetrying] = useState<boolean>(false);
    const isMounted = useRef<boolean>(true); // Track if component is mounted

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            isMounted.current = false;
        };
    }, []);

    // Fetch user's channels with request deduplication
    const fetchChannels = useCallback(async (): Promise<void> => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        // Check if request is already in progress
        const requestKey = `/channels-${user?.id || 'unknown'}`;
        if (activeRequests.has(requestKey)) {
            logger.debug('[useUserChannels] Request already in progress, waiting for existing request');
            try {
                const response = await activeRequests.get(requestKey);
                if (isMounted.current) {
                    setChannels(response || []);
                    setLastFetch(new Date().toISOString());
                    logger.debug('[useUserChannels] Used cached response', { count: response?.length || 0 });
                }
                return;
            } catch (err) {
                // Let the error be handled by the active request
                throw err;
            }
        }

        setLoading(true);
        setError(null);

        // Create the request promise and store it
        const requestPromise = (async () => {
            try {
                logger.info('[useUserChannels] Fetching channels from backend');
                const response = await apiClient.get<Channel[]>('/channels/');
                logger.info('[useUserChannels] Channels fetched successfully', { count: response?.length || 0 });
                return response;
            } finally {
                // Remove from active requests when done
                activeRequests.delete(requestKey);
            }
        })();

        // Store the promise
        activeRequests.set(requestKey, requestPromise);

        try {
            const response = await requestPromise;

            if (isMounted.current) {
                setChannels(response || []);
                setLastFetch(new Date().toISOString());
            }

            // Don't auto-select here - let the separate useEffect handle it
            // This prevents infinite loop caused by selectedChannel dependency
        } catch (err) {
            logger.error('[useUserChannels] Failed to fetch user channels', err);
            if (isMounted.current) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to fetch channels';
                setError(errorMessage);
            }
        } finally {
            if (isMounted.current) {
                setLoading(false);
            }
        }
    }, [dataProvider, isAuthenticated, user?.id]); // ✅ Removed selectedChannel and onChannelChange to break infinite loop

    // Retry with exponential backoff
    const retryFetch = useCallback(async (maxRetries = 3): Promise<void> => {
        setRetrying(true);

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                logger.info('[useUserChannels] Retry attempt', { attempt, maxRetries });
                await fetchChannels();
                logger.info('[useUserChannels] Retry successful', { attempt });
                break; // Success, exit retry loop
            } catch (err) {
                if (attempt === maxRetries) {
                    logger.error('[useUserChannels] All retry attempts failed', { maxRetries });
                    throw err;
                }

                // Exponential backoff: 1s, 2s, 4s
                const delay = Math.pow(2, attempt - 1) * 1000;
                logger.debug('[useUserChannels] Waiting before retry', { delay, attempt: attempt + 1, maxRetries });
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        setRetrying(false);
    }, [fetchChannels]);

    // Create a new channel
    const createChannel = useCallback(async (channelData: Partial<Channel>): Promise<Channel> => {
        if (!isAuthenticated) {
            throw new Error('Authentication required');
        }

        setLoading(true);
        setError(null);

        try {
            const newChannel = await apiClient.post<Channel>('/channels/', channelData);

            // Add new channel to local state
            setChannels(prev => [...prev, newChannel]);

            // Auto-select the new channel
            setSelectedChannel(newChannel);
            onChannelChange?.(newChannel);

            return newChannel;
        } catch (err) {
            logger.error('Failed to create channel', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to create channel';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dataProvider, isAuthenticated, onChannelChange]);

    // Select a channel
    const selectChannel = useCallback((channel: Channel | null): void => {
        setSelectedChannel(channel);
        onChannelChange?.(channel);

        // Store in localStorage for persistence
        try {
            localStorage.setItem('selectedChannelId', channel?.id?.toString() || '');
        } catch (e) {
            logger.warn('Failed to save selected channel to localStorage', e);
        }
    }, [onChannelChange]);

    // Get channel by ID
    const getChannel = useCallback(async (channelId: number | string): Promise<Channel> => {
        if (!isAuthenticated) {
            throw new Error('Authentication required');
        }

        try {
            const channel = await apiClient.get<Channel>(`/channels/${channelId}`);
            return channel;
        } catch (err) {
            logger.error(`Failed to fetch channel ${channelId}`, err);
            throw err;
        }
    }, [dataProvider, isAuthenticated]);

    // Auto-fetch on mount and auth changes
    useEffect(() => {
        if (isAuthenticated && autoFetch) {
            fetchChannels();
        }
    }, [isAuthenticated, autoFetch, fetchChannels]);

    // Restore selected channel from localStorage (separate from fetch to prevent loops)
    useEffect(() => {
        // Only run when channels change and no channel is selected
        if (channels.length > 0 && !selectedChannel) {
            logger.debug('[useUserChannels] Auto-selecting channel');
            try {
                const savedChannelId = localStorage.getItem('selectedChannelId');
                if (savedChannelId) {
                    const saved = channels.find(ch => ch.id?.toString() === savedChannelId);
                    if (saved) {
                        logger.info('[useUserChannels] Restored channel from localStorage', { channel: saved.title || saved.name });
                        setSelectedChannel(saved);
                        onChannelChange?.(saved);
                        return;
                    }
                }

                // Fallback to first channel
                const firstChannel = channels[0];
                logger.info('[useUserChannels] Auto-selected first channel', { channel: firstChannel.title || firstChannel.name });
                setSelectedChannel(firstChannel);
                onChannelChange?.(firstChannel);
            } catch (e) {
                logger.warn('[useUserChannels] Failed to restore selected channel', e);
                // Fallback to first channel
                const firstChannel = channels[0];
                setSelectedChannel(firstChannel);
                onChannelChange?.(firstChannel);
            }
        }
    }, [channels]); // ✅ Only depend on channels array, not selectedChannel or onChannelChange

    return {
        channels,
        selectedChannel,
        loading,
        error,
        lastFetch,
        retrying,
        fetchChannels,
        retryFetch,
        createChannel,
        selectChannel,
        getChannel,
        user,
        isAuthenticated
    };
};

/**
 * Selected channel return type
 */
export interface UseSelectedChannelReturn {
    channel: Channel | null;
    channelId: number | string | undefined;
    channelName: string | undefined;
    selectChannel: (channel: Channel | null) => void;
    hasChannels: boolean;
}

/**
 * Simple hook to get the current selected channel
 * @returns Selected channel info
 */
export const useSelectedChannel = (): UseSelectedChannelReturn => {
    const { selectedChannel, selectChannel, channels } = useUserChannels();

    return {
        channel: selectedChannel,
        channelId: selectedChannel?.id,
        channelName: selectedChannel?.name || selectedChannel?.title,
        selectChannel,
        hasChannels: channels.length > 0
    };
};

/**
 * Channel access return type
 */
export interface UseChannelAccessReturn {
    hasAccess: boolean;
    checking: boolean;
    isAuthenticated: boolean;
}

/**
 * Hook to validate if user has access to a specific channel
 * @param channelId - Channel ID to validate
 * @returns Access validation result
 */
export const useChannelAccess = (channelId: number | string | undefined): UseChannelAccessReturn => {
    const { channels, isAuthenticated } = useUserChannels();
    const [hasAccess, setHasAccess] = useState<boolean>(false);
    const [checking, setChecking] = useState<boolean>(true);

    useEffect(() => {
        if (!isAuthenticated) {
            setHasAccess(false);
            setChecking(false);
            return;
        }

        if (channels.length === 0) {
            setChecking(true);
            return;
        }

        // Check if user owns this channel
        const hasChannelAccess = channels.some(
            channel => channel.id?.toString() === channelId?.toString()
        );

        setHasAccess(hasChannelAccess);
        setChecking(false);
    }, [channelId, channels, isAuthenticated]);

    return {
        hasAccess,
        checking,
        isAuthenticated
    };
};
