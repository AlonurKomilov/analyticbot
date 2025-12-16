/**
 * UserBotDashboard Custom Hooks
 */
import { useEffect, useState, useCallback } from 'react';
import { useUserBotStore, useChannelStore } from '@/store';
import { apiClient } from '@/api/client';
import toast from 'react-hot-toast';
import { DialogState, TestMessageState, RateLimitState } from './types';
import { ActiveService } from './ActiveServicesCard';
import { AvailableService } from './AvailableUpgradesCard';

// Hook for fetching user's active services and available upgrades
export const useBotServices = () => {
  const [activeServices, setActiveServices] = useState<ActiveService[]>([]);
  const [availableServices, setAvailableServices] = useState<AvailableService[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch user's active subscriptions and available services in parallel
      const [activeResponse, catalogResponse] = await Promise.all([
        apiClient.get<{ subscriptions: ActiveService[] }>('/services/user/active').catch(() => ({ subscriptions: [] })),
        apiClient.get<{ services: AvailableService[] }>('/services').catch(() => ({ services: [] })),
      ]);

      setActiveServices(activeResponse.subscriptions || []);
      setAvailableServices(catalogResponse.services || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load services');
      console.error('Failed to fetch bot services:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  const activeServiceKeys = activeServices.map(s => s.service_key);

  return {
    activeServices,
    availableServices,
    activeServiceKeys,
    isLoading,
    error,
    refetch: fetchServices,
  };
};

export const useBotDashboard = () => {
  const {
    bot,
    fetchBotStatus,
    removeBot,
    updateRateLimits,
    verifyBot,
    isLoading,
    isRemoving,
    isUpdating,
    isVerifying,
    error,
    clearError,
  } = useUserBotStore();

  const { channels, fetchChannels, isLoading: isLoadingChannels } = useChannelStore();

  // Dialog states
  const [dialogs, setDialogs] = useState<DialogState>({
    showRemoveDialog: false,
    showRateLimitDialog: false,
    showTestMessageDialog: false,
  });

  // Test message state
  const [testMessageState, setTestMessageState] = useState<TestMessageState>({
    testMessage: 'Hello! This is a test message from your bot.',
    selectedChannelId: '',
    manualChatId: '',
    useManualInput: false,
  });

  // Rate limit state
  const [rateLimitState, setRateLimitState] = useState<RateLimitState>({
    rateLimitRps: '',
    maxConcurrent: '',
  });

  // Fetch bot status only once on mount
  useEffect(() => {
    const loadBotStatus = async () => {
      if (isLoading || bot) return;

      try {
        const result = await fetchBotStatus();
        if (result) {
          toast.success('✅ Bot status loaded');
        }
      } catch (err) {
        console.error('Failed to load bot status:', err);
      }
    };
    loadBotStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch user channels for the selector
  useEffect(() => {
    if (dialogs.showTestMessageDialog && channels.length === 0 && !isLoadingChannels) {
      fetchChannels().catch(err => {
        console.error('Failed to load channels:', err);
        toast.error('Failed to load channels. You can use manual input instead.');
      });
    }
  }, [dialogs.showTestMessageDialog, channels.length, isLoadingChannels, fetchChannels]);

  // Sync rate limit state with bot data
  useEffect(() => {
    if (bot) {
      setRateLimitState({
        rateLimitRps: bot.max_requests_per_second.toString(),
        maxConcurrent: bot.max_concurrent_requests.toString(),
      });
    }
  }, [bot]);

  // Dialog handlers
  const openDialog = (dialog: keyof DialogState) => {
    setDialogs(prev => ({ ...prev, [dialog]: true }));
  };

  const closeDialog = (dialog: keyof DialogState) => {
    setDialogs(prev => ({ ...prev, [dialog]: false }));
  };

  return {
    // Store data
    bot,
    channels,
    error,
    clearError,
    // Loading states
    isLoading,
    isLoadingChannels,
    isRemoving,
    isUpdating,
    isVerifying,
    // Actions
    fetchBotStatus,
    removeBot,
    updateRateLimits,
    verifyBot,
    // Dialog state
    dialogs,
    openDialog,
    closeDialog,
    // Test message state
    testMessageState,
    setTestMessageState,
    // Rate limit state
    rateLimitState,
    setRateLimitState,
  };
};
