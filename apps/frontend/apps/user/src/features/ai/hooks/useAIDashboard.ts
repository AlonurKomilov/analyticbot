/**
 * User AI Dashboard Hooks
 * Custom hooks for AI dashboard state management
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/api/client';
import toast from 'react-hot-toast';
import { UserAIAPI } from '../api';
import type { 
  AIStatus, 
  AISettings, 
  AILimits, 
  AIUsage,
  ActiveAIService,
  AvailableAIService 
} from '../types';

// =====================================
// Main AI Dashboard Hook
// =====================================

export interface UseAIDashboardReturn {
  status: AIStatus | null;
  settings: AISettings | null;
  limits: AILimits | null;
  usage: AIUsage | null;
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
  refresh: () => Promise<void>;
  updateSettings: (newSettings: Partial<AISettings>) => Promise<void>;
  isUpdating: boolean;
}

export const useAIDashboard = (): UseAIDashboardReturn => {
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [settings, setSettings] = useState<AISettings | null>(null);
  const [limits, setLimits] = useState<AILimits | null>(null);
  const [usage, setUsage] = useState<AIUsage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => setError(null), []);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch status and settings in parallel
      const [statusResponse, settingsResponse] = await Promise.all([
        UserAIAPI.getStatus(),
        UserAIAPI.getSettings(),
      ]);

      setStatus(statusResponse);
      
      setSettings(settingsResponse.settings);
      setLimits(settingsResponse.limits);
      setUsage(settingsResponse.usage);

    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load AI dashboard data';
      setError(errorMessage);
      console.error('AI Dashboard fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateSettings = useCallback(async (newSettings: Partial<AISettings>) => {
    setIsUpdating(true);
    try {
      const response = await UserAIAPI.updateSettings(newSettings);
      setSettings(response.settings);
      toast.success('✅ AI settings updated');
    } catch (err: any) {
      toast.error(err.message || 'Failed to update settings');
      throw err;
    } finally {
      setIsUpdating(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    status,
    settings,
    limits,
    usage,
    isLoading,
    error,
    clearError,
    refresh: fetchData,
    updateSettings,
    isUpdating,
  };
};

// =====================================
// AI Services Hook (Active & Available)
// =====================================

export interface UseAIServicesReturn {
  activeServices: ActiveAIService[];
  availableServices: AvailableAIService[];
  activeServiceKeys: string[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useAIServices = (): UseAIServicesReturn => {
  const [activeServices, setActiveServices] = useState<ActiveAIService[]>([]);
  const [availableServices, setAvailableServices] = useState<AvailableAIService[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch user's active subscriptions and available services in parallel
      const [activeResponse, aiServicesResponse] = await Promise.all([
        // Get user's active service subscriptions (only AI related)
        apiClient.get<{ subscriptions: ActiveAIService[] }>('/services/user/active')
          .then(res => res.subscriptions?.filter(s => s.service_key.startsWith('ai_')) || [])
          .catch(() => []),
        // Get available AI services from User AI API
        UserAIAPI.getServices()
          .then(res => res.services || [])
          .catch(() => []),
      ]);

      setActiveServices(activeResponse);
      setAvailableServices(aiServicesResponse);
    } catch (err: any) {
      setError(err.message || 'Failed to load services');
      console.error('Failed to fetch AI services:', err);
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

// =====================================
// Combined Hook for Full Dashboard
// =====================================

export const useFullAIDashboard = () => {
  const dashboard = useAIDashboard();
  const services = useAIServices();

  const refreshAll = useCallback(async () => {
    await Promise.all([
      dashboard.refresh(),
      services.refetch(),
    ]);
  }, [dashboard, services]);

  return {
    ...dashboard,
    activeServices: services.activeServices,
    availableServices: services.availableServices,
    activeServiceKeys: services.activeServiceKeys,
    isLoadingServices: services.isLoading,
    servicesError: services.error,
    refreshAll,
    refetchServices: services.refetch,
  };
};

export default useAIDashboard;
