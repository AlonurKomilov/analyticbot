/**
 * MTProto Monitoring Page Hooks
 * Custom hooks for the MTProto monitoring dashboard
 */
import { useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/api/client';
import type { ActiveMTProtoService } from './components/ActiveMTProtoServicesCard';
import type { AvailableMTProtoService } from './components/AvailableMTProtoUpgradesCard';

/**
 * Hook for fetching user's active MTProto services and available upgrades
 */
export const useMTProtoServices = () => {
  const [activeServices, setActiveServices] = useState<ActiveMTProtoService[]>([]);
  const [availableServices, setAvailableServices] = useState<AvailableMTProtoService[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch user's active subscriptions and available services in parallel
      const [activeResponse, catalogResponse] = await Promise.all([
        apiClient.get<{ subscriptions: ActiveMTProtoService[] }>('/services/user/active').catch(() => ({ subscriptions: [] })),
        apiClient.get<{ services: AvailableMTProtoService[] }>('/services').catch(() => ({ services: [] })),
      ]);

      // Filter only MTProto services
      const mtprotoActive = (activeResponse.subscriptions || []).filter(
        s => s.service_key.startsWith('mtproto_')
      );
      const mtprotoAvailable = (catalogResponse.services || []).filter(
        s => s.service_key.startsWith('mtproto_')
      );

      setActiveServices(mtprotoActive);
      setAvailableServices(mtprotoAvailable);
    } catch (err: any) {
      setError(err.message || 'Failed to load MTProto services');
      console.error('Failed to fetch MTProto services:', err);
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

/**
 * Hook for testing MTProto connection
 */
export const useMTProtoConnection = () => {
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const testConnection = useCallback(async () => {
    setIsTesting(true);
    setTestResult(null);

    try {
      const response = await apiClient.post<{ success: boolean; message: string }>('/user-mtproto/test-connection');
      setTestResult({
        success: true,
        message: response.message || 'Connection successful!',
      });
      return response;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Connection test failed';
      setTestResult({
        success: false,
        message,
      });
      throw err;
    } finally {
      setIsTesting(false);
    }
  }, []);

  return {
    isTesting,
    testResult,
    testConnection,
    clearResult: () => setTestResult(null),
  };
};
