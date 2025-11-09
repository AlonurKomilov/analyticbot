/**
 * 🔐 User Channels Hooks
 *
 * Hooks for managing user channels with authentication.
 * Provides channel selection, creation, and management functionality.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useAuthenticatedDataProvider } from './useAuthenticatedDataSource';

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
    fetchChannels: () => Promise<void>;
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

    // Fetch user's channels
    const fetchChannels = useCallback(async (): Promise<void> => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = (await (dataProvider as any)._makeRequest('/channels')) as Channel[];

            setChannels(response || []);
            setLastFetch(new Date().toISOString());

            // Auto-select first channel if none selected and channels exist
            if (!selectedChannel && response && response.length > 0) {
                const firstChannel = response[0];
                setSelectedChannel(firstChannel);
                onChannelChange?.(firstChannel);
            }
        } catch (err) {
            console.error('Failed to fetch user channels:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch channels';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }, [dataProvider, isAuthenticated, selectedChannel, onChannelChange]);

    // Create a new channel
    const createChannel = useCallback(async (channelData: Partial<Channel>): Promise<Channel> => {
        if (!isAuthenticated) {
            throw new Error('Authentication required');
        }

        setLoading(true);
        setError(null);

        try {
            const newChannel = (await (dataProvider as any)._makeRequest('/channels', {
                method: 'POST',
                body: JSON.stringify(channelData)
            })) as Channel;

            // Add new channel to local state
            setChannels(prev => [...prev, newChannel]);

            // Auto-select the new channel
            setSelectedChannel(newChannel);
            onChannelChange?.(newChannel);

            return newChannel;
        } catch (err) {
            console.error('Failed to create channel:', err);
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
            console.warn('Failed to save selected channel to localStorage:', e);
        }
    }, [onChannelChange]);

    // Get channel by ID
    const getChannel = useCallback(async (channelId: number | string): Promise<Channel> => {
        if (!isAuthenticated) {
            throw new Error('Authentication required');
        }

        try {
            const channel = (await (dataProvider as any)._makeRequest(`/channels/${channelId}`)) as Channel;
            return channel;
        } catch (err) {
            console.error(`Failed to fetch channel ${channelId}:`, err);
            throw err;
        }
    }, [dataProvider, isAuthenticated]);

    // Auto-fetch on mount and auth changes
    useEffect(() => {
        if (isAuthenticated && autoFetch) {
            fetchChannels();
        }
    }, [isAuthenticated, autoFetch, fetchChannels]);

    // Restore selected channel from localStorage
    useEffect(() => {
        if (channels.length > 0 && !selectedChannel) {
            try {
                const savedChannelId = localStorage.getItem('selectedChannelId');
                if (savedChannelId) {
                    const saved = channels.find(ch => ch.id?.toString() === savedChannelId);
                    if (saved) {
                        setSelectedChannel(saved);
                        onChannelChange?.(saved);
                        return;
                    }
                }

                // Fallback to first channel
                const firstChannel = channels[0];
                setSelectedChannel(firstChannel);
                onChannelChange?.(firstChannel);
            } catch (e) {
                console.warn('Failed to restore selected channel:', e);
                // Fallback to first channel
                const firstChannel = channels[0];
                setSelectedChannel(firstChannel);
                onChannelChange?.(firstChannel);
            }
        }
    }, [channels, selectedChannel, onChannelChange]);

    return {
        channels,
        selectedChannel,
        loading,
        error,
        lastFetch,
        fetchChannels,
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
