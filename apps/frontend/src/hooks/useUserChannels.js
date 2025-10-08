/**
 * 🔐 User Channels Hooks
 *
 * Hooks for managing user channels with authentication.
 * Provides channel selection, creation, and management functionality.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAuthenticatedDataProvider } from './useAuthenticatedDataSource';

/**
 * Hook to fetch and manage user's channels
 * @param {Object} options - Hook options
 * @returns {Object} User channels data and management functions
 */
export const useUserChannels = (options = {}) => {
    const { autoFetch = true, onChannelChange = null } = options;
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();

    const [channels, setChannels] = useState([]);
    const [selectedChannel, setSelectedChannel] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastFetch, setLastFetch] = useState(null);

    // Fetch user's channels
    const fetchChannels = useCallback(async () => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await dataProvider._makeRequest('/analytics/channels');
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
            setError(err.message || 'Failed to fetch channels');
        } finally {
            setLoading(false);
        }
    }, [dataProvider, isAuthenticated, selectedChannel, onChannelChange]);

    // Create a new channel
    const createChannel = useCallback(async (channelData) => {
        if (!isAuthenticated) {
            throw new Error('Authentication required');
        }

        setLoading(true);
        setError(null);

        try {
            const newChannel = await dataProvider._makeRequest('/analytics/channels', {
                method: 'POST',
                body: JSON.stringify(channelData)
            });

            // Add new channel to local state
            setChannels(prev => [...prev, newChannel]);

            // Auto-select the new channel
            setSelectedChannel(newChannel);
            onChannelChange?.(newChannel);

            return newChannel;
        } catch (err) {
            console.error('Failed to create channel:', err);
            setError(err.message || 'Failed to create channel');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [dataProvider, isAuthenticated, onChannelChange]);

    // Select a channel
    const selectChannel = useCallback((channel) => {
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
    const getChannel = useCallback(async (channelId) => {
        if (!isAuthenticated) {
            throw new Error('Authentication required');
        }

        try {
            const channel = await dataProvider._makeRequest(`/analytics/channels/${channelId}`);
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
 * Simple hook to get the current selected channel
 * @returns {Object} Selected channel info
 */
export const useSelectedChannel = () => {
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
 * Hook to validate if user has access to a specific channel
 * @param {number|string} channelId - Channel ID to validate
 * @returns {Object} Access validation result
 */
export const useChannelAccess = (channelId) => {
    const { channels, isAuthenticated } = useUserChannels();
    const [hasAccess, setHasAccess] = useState(false);
    const [checking, setChecking] = useState(true);

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
