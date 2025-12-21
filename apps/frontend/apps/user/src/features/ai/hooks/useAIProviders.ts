/**
 * AI Providers Hook
 * Manages AI provider configurations and spending
 */

import { useState, useEffect, useCallback } from 'react';
import AIProvidersAPI, {
  AIProvider,
  UserAIProvider,
  AIProviderSpending,
  AddProviderRequest,
} from '../api/aiProvidersAPI';
import toast from 'react-hot-toast';

export const useAIProviders = () => {
  const [availableProviders, setAvailableProviders] = useState<AIProvider[]>([]);
  const [userProviders, setUserProviders] = useState<UserAIProvider[]>([]);
  const [spending, setSpending] = useState<Record<string, AIProviderSpending>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);

  // Load available providers
  const loadAvailableProviders = useCallback(async () => {
    try {
      const data = await AIProvidersAPI.getAvailableProviders();
      setAvailableProviders(data.providers);
    } catch (error) {
      console.error('Failed to load available providers:', error);
      toast.error('Failed to load available providers');
    }
  }, []);

  // Load user's configured providers
  const loadUserProviders = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await AIProvidersAPI.getMyProviders();
      setUserProviders(data.providers);
    } catch (error) {
      console.error('Failed to load user providers:', error);
      toast.error('Failed to load your providers');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load spending for a provider
  const loadSpending = useCallback(async (provider: string) => {
    try {
      const data = await AIProvidersAPI.getProviderSpending(provider);
      setSpending((prev) => ({ ...prev, [provider]: data }));
    } catch (error) {
      console.error(`Failed to load spending for ${provider}:`, error);
    }
  }, []);

  // Load all spending data
  const loadAllSpending = useCallback(async () => {
    for (const provider of userProviders) {
      await loadSpending(provider.provider);
    }
  }, [userProviders, loadSpending]);

  // Add a new provider
  const addProvider = useCallback(async (data: AddProviderRequest) => {
    setIsAdding(true);
    try {
      const response = await AIProvidersAPI.addProvider(data);
      toast.success(response.message || 'Provider added successfully');
      await loadUserProviders();
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to add provider';
      toast.error(message);
      throw error;
    } finally {
      setIsAdding(false);
    }
  }, [loadUserProviders]);

  // Set default provider
  const setDefaultProvider = useCallback(async (provider: string) => {
    try {
      const response = await AIProvidersAPI.setDefaultProvider(provider);
      toast.success(response.message || 'Default provider updated');
      await loadUserProviders();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to set default provider';
      toast.error(message);
      throw error;
    }
  }, [loadUserProviders]);

  // Remove a provider
  const removeProvider = useCallback(async (provider: string) => {
    try {
      const response = await AIProvidersAPI.removeProvider(provider);
      toast.success(response.message || 'Provider removed successfully');
      await loadUserProviders();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to remove provider';
      toast.error(message);
      throw error;
    }
  }, [loadUserProviders]);

  // Initial load
  useEffect(() => {
    loadAvailableProviders();
    loadUserProviders();
  }, [loadAvailableProviders, loadUserProviders]);

  // Load spending when user providers change
  useEffect(() => {
    if (userProviders.length > 0) {
      loadAllSpending();
    }
  }, [userProviders.length]); // Only reload when count changes

  return {
    availableProviders,
    userProviders,
    spending,
    isLoading,
    isAdding,
    addProvider,
    setDefaultProvider,
    removeProvider,
    loadSpending,
    refreshProviders: loadUserProviders,
  };
};
