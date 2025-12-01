/**
 * usePostDynamics Hook
 * Manages state and data fetching for post view dynamics
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAnalyticsStore, useChannelStore, useUIStore } from '@store';
import { DEFAULT_DEMO_CHANNEL_ID } from '@/__mocks__/constants';
import { uiLogger } from '@/utils/logger';
import { TimeRange, RefreshInterval, MetricFilter, DataPoint } from './types';
import type { TimePeriod } from '@/types/models';

interface UsePostDynamicsReturn {
    // State
    data: DataPoint[];
    timeRange: TimeRange;
    refreshInterval: RefreshInterval;
    metricFilter: MetricFilter;
    drillDownDate: string | null;
    drillDownHour: string | null;
    error: string | null;
    isLoading: boolean;

    // Handlers
    handleTimeRangeChange: (value: TimeRange) => void;
    handleRefreshIntervalChange: (value: RefreshInterval) => void;
    handleMetricFilterChange: (value: MetricFilter) => void;
    handleChartClick: (data: any) => void;
    handleBackClick: () => void;
    loadData: () => Promise<void>;
}

export function usePostDynamics(): UsePostDynamicsReturn {
    // Main component state
    const [timeRange, setTimeRange] = useState<TimeRange>('all');
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<DataPoint[]>([]);
    const [refreshInterval, setRefreshInterval] = useState<RefreshInterval>('30s');
    const [metricFilter, setMetricFilter] = useState<MetricFilter>('all');
    const [drillDownDate, setDrillDownDate] = useState<string | null>(null);
    const [drillDownHour, setDrillDownHour] = useState<string | null>(null);

    // Store access
    const { isLoadingPostDynamics } = useAnalyticsStore();
    const fetchPostDynamicsFromStore = useAnalyticsStore.getState().fetchPostDynamics;
    const { selectedChannel } = useChannelStore();
    const { dataSource } = useUIStore();

    // Refs for optimization
    const isMountedRef = useRef<boolean>(true);
    const timeRangeRef = useRef<TimeRange>(timeRange);
    const isLoadingRef = useRef<boolean>(false);
    const isAutoRefreshRef = useRef<boolean>(false);

    // Load data function
    const loadData = useCallback(async (): Promise<void> => {
        uiLogger.debug('PostDynamics: loadData called', { isLoading: isLoadingRef.current });

        if (isLoadingRef.current) {
            uiLogger.debug('PostDynamics: Already loading, skipping');
            return;
        }

        const channelId = (dataSource === 'demo' || dataSource === 'mock')
            ? DEFAULT_DEMO_CHANNEL_ID
            : (selectedChannel?.id?.toString() || null);

        uiLogger.debug('PostDynamics: Channel determination', { dataSource, selectedChannel: selectedChannel?.id, channelId });

        if (!channelId) {
            uiLogger.info('No channel selected - select a channel to view post dynamics');
            setError('info:Please select a channel to view post dynamics');
            setData([]);
            isLoadingRef.current = false;
            return;
        }

        isLoadingRef.current = true;
        setError(null);

        try {
            const currentTimeRange = timeRangeRef.current;

            const customTimeRange = drillDownHour ? {
                start_time: drillDownHour,
                end_time: new Date(new Date(drillDownHour).getTime() + 60 * 60 * 1000 - 1000).toISOString()
            } : undefined;

            const customDateRange = drillDownDate && !drillDownHour ? {
                start_date: drillDownDate,
                end_date: drillDownDate
            } : undefined;

            // Cast TimeRange to TimePeriod - the store supports a subset of TimeRange values
            const storeTimeRange = currentTimeRange as TimePeriod;
            await fetchPostDynamicsFromStore(channelId, storeTimeRange, customDateRange, customTimeRange, isAutoRefreshRef.current);

            const latestPostDynamics = useAnalyticsStore.getState().postDynamics;

            let dataArray: DataPoint[] = [];
            if (Array.isArray(latestPostDynamics)) {
                dataArray = latestPostDynamics;
            } else if (latestPostDynamics && typeof latestPostDynamics === 'object') {
                if ('dataPoints' in latestPostDynamics) {
                    dataArray = (latestPostDynamics as any).dataPoints || [];
                } else if ('data' in latestPostDynamics) {
                    dataArray = (latestPostDynamics as any).data || [];
                }
            }

            setData(dataArray);
        } catch (err) {
            uiLogger.error('PostViewDynamicsChart: Error loading data', { error: err });
            if (isMountedRef.current) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics data';
                setError(errorMessage);
            }
        } finally {
            isLoadingRef.current = false;
        }
    }, [selectedChannel, dataSource, drillDownDate, drillDownHour, fetchPostDynamicsFromStore]);

    // Event handlers
    const handleTimeRangeChange = useCallback((value: TimeRange): void => {
        const newTimeRange = value;
        timeRangeRef.current = newTimeRange;
        setTimeRange(newTimeRange);
        isLoadingRef.current = false;

        setTimeout(() => {
            if (timeRangeRef.current === newTimeRange) {
                loadData();
            }
        }, 300);
    }, [loadData]);

    const handleRefreshIntervalChange = useCallback((value: RefreshInterval): void => {
        setRefreshInterval(value);
    }, []);

    const handleMetricFilterChange = useCallback((value: MetricFilter): void => {
        setMetricFilter(value);
    }, []);

    const handleChartClick = useCallback((clickData: any) => {
        if (!clickData || !clickData.activeLabel) return;

        const clickedTimestamp = clickData.activeLabel;
        const clickedDate = new Date(clickedTimestamp);

        if (drillDownHour) {
            return; // Already at deepest level
        } else if (drillDownDate) {
            setDrillDownHour(clickedDate.toISOString());
        } else if (timeRange !== '1h' && timeRange !== '6h' && timeRange !== '12h' && timeRange !== '24h') {
            setDrillDownDate(clickedDate.toISOString().split('T')[0]);
        }
    }, [timeRange, drillDownDate, drillDownHour]);

    const handleBackClick = useCallback(() => {
        if (drillDownHour) {
            setDrillDownHour(null);
        } else {
            setDrillDownDate(null);
        }
    }, [drillDownHour]);

    // Initial load effect
    useEffect(() => {
        const shouldLoad = (dataSource === 'demo' || dataSource === 'mock')
            || (dataSource === 'api' && selectedChannel?.id);

        if (shouldLoad) {
            loadData();
        }
    }, [selectedChannel, dataSource, loadData]);

    // Cleanup effect
    useEffect(() => {
        return () => {
            isMountedRef.current = false;
        };
    }, []);

    return {
        data,
        timeRange,
        refreshInterval,
        metricFilter,
        drillDownDate,
        drillDownHour,
        error,
        isLoading: isLoadingPostDynamics,
        handleTimeRangeChange,
        handleRefreshIntervalChange,
        handleMetricFilterChange,
        handleChartClick,
        handleBackClick,
        loadData
    };
}
