/**
 * useOverview Hook
 * =================
 *
 * React hook for fetching channel overview data.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { overviewService } from './overviewService';
import type {
  ChannelOverviewData,
  OverviewPeriod,
  UseOverviewOptions,
  UseOverviewReturn,
  TelegramStats,
} from './types';

/**
 * Hook for fetching complete channel overview dashboard data
 */
export function useOverview(
  channelId: string | number | null | undefined,
  options: UseOverviewOptions = {}
): UseOverviewReturn {
  const {
    period = 'last_7_days',
    refreshInterval = 60000, // 1 minute default
    enabled = true,
  } = options;

  const [data, setData] = useState<ChannelOverviewData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const isMountedRef = useRef<boolean>(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    if (!channelId || !enabled) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setIsError(false);
      setError(null);

      const result = await overviewService.getDashboard(channelId, period);

      if (isMountedRef.current) {
        setData(result);
        setIsLoading(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        const errorObj = err instanceof Error ? err : new Error(String(err));
        setError(errorObj);
        setIsError(true);
        setIsLoading(false);
        console.error('[useOverview] Failed to fetch overview:', err);
      }
    }
  }, [channelId, period, enabled]);

  // Initial fetch and when dependencies change
  useEffect(() => {
    isMountedRef.current = true;
    fetchData();

    return () => {
      isMountedRef.current = false;
    };
  }, [fetchData]);

  // Set up refresh interval
  useEffect(() => {
    if (!enabled || !channelId || refreshInterval <= 0) {
      return;
    }

    intervalRef.current = setInterval(() => {
      fetchData();
    }, refreshInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, channelId, refreshInterval, fetchData]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch,
  };
}

/**
 * Hook for fetching quick stats only (no charts)
 */
export function useQuickStats(
  channelId: string | number | null | undefined,
  options: Pick<UseOverviewOptions, 'refreshInterval' | 'enabled'> = {}
) {
  const { refreshInterval = 30000, enabled = true } = options;

  const [data, setData] = useState<Omit<ChannelOverviewData, 'subscribers_history' | 'views_history' | 'posts_history'> | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const isMountedRef = useRef<boolean>(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    if (!channelId || !enabled) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setIsError(false);

      const result = await overviewService.getQuickStats(channelId);

      if (isMountedRef.current) {
        setData(result);
        setIsLoading(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        const errorObj = err instanceof Error ? err : new Error(String(err));
        setError(errorObj);
        setIsError(true);
        setIsLoading(false);
      }
    }
  }, [channelId, enabled]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchData();
    return () => { isMountedRef.current = false; };
  }, [fetchData]);

  useEffect(() => {
    if (!enabled || !channelId || refreshInterval <= 0) return;
    intervalRef.current = setInterval(fetchData, refreshInterval);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [enabled, channelId, refreshInterval, fetchData]);

  return { data, isLoading, isError, error };
}

/**
 * Hook for fetching chart data with custom day range
 */
export function useOverviewCharts(
  channelId: string | number | null | undefined,
  days: number = 30,
  options: Pick<UseOverviewOptions, 'enabled'> = {}
) {
  const { enabled = true } = options;

  type ChartData = {
    views_history: ChannelOverviewData['views_history'];
    posts_history: ChannelOverviewData['posts_history'];
    subscribers_history: ChannelOverviewData['subscribers_history'];
  };

  const [data, setData] = useState<ChartData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const isMountedRef = useRef<boolean>(true);

  const fetchData = useCallback(async () => {
    if (!channelId || !enabled) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setIsError(false);

      const result = await overviewService.getCharts(channelId, days);

      if (isMountedRef.current) {
        setData(result);
        setIsLoading(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        const errorObj = err instanceof Error ? err : new Error(String(err));
        setError(errorObj);
        setIsError(true);
        setIsLoading(false);
      }
    }
  }, [channelId, days, enabled]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchData();
    return () => { isMountedRef.current = false; };
  }, [fetchData]);

  return { data, isLoading, isError, error };
}

/**
 * Prefetch overview data for a channel (utility function)
 */
export async function prefetchOverview(
  channelId: string | number,
  period: OverviewPeriod = 'last_7_days'
): Promise<ChannelOverviewData> {
  return overviewService.getDashboard(channelId, period);
}

/**
 * Hook for fetching Telegram Stats API data (demographics, traffic sources, growth)
 * Only available for channels with 500+ subscribers
 */
export function useTelegramStats(
  channelId: string | number | null | undefined,
  options: Pick<UseOverviewOptions, 'refreshInterval' | 'enabled'> = {}
) {
  const { refreshInterval = 300000, enabled = true } = options; // 5 min default (stats don't update often)

  const [data, setData] = useState<TelegramStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const isMountedRef = useRef<boolean>(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    if (!channelId || !enabled) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setIsError(false);
      setError(null);

      const result = await overviewService.getTelegramStats(channelId);

      if (isMountedRef.current) {
        setData(result);
        setIsLoading(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        const errorObj = err instanceof Error ? err : new Error(String(err));
        setError(errorObj);
        setIsError(true);
        setIsLoading(false);
        console.error('[useTelegramStats] Failed to fetch Telegram stats:', err);
      }
    }
  }, [channelId, enabled]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchData();
    return () => { isMountedRef.current = false; };
  }, [fetchData]);

  useEffect(() => {
    if (!enabled || !channelId || refreshInterval <= 0) return;
    intervalRef.current = setInterval(fetchData, refreshInterval);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [enabled, channelId, refreshInterval, fetchData]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  return { data, isLoading, isError, error, refetch };
}

export default useOverview;
