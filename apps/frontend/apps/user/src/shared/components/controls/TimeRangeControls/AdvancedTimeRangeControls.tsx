/**
 * AdvancedTimeRangeControls - Feature-rich time range controls
 *
 * Used for analytics dashboards requiring:
 * - Time period selection
 * - Refresh interval control
 * - Metric filtering
 *
 * @example
 * ```tsx
 * <AdvancedTimeRangeControls
 *   timeRange="24h"
 *   onTimeRangeChange={(range) => setTimeRange(range)}
 *   hideRefreshControl
 * />
 * ```
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    SelectChangeEvent
} from '@mui/material';
import type { AdvancedTimeRangeControlsProps, TimeRange, RefreshInterval, MetricFilter } from './types';

const AdvancedTimeRangeControls: React.FC<AdvancedTimeRangeControlsProps> = React.memo(({
    timeRange = '24h',
    refreshInterval = '1m',
    metricFilter = 'all',
    onTimeRangeChange,
    onRefreshIntervalChange,
    onMetricFilterChange,
    hideRefreshControl = false,
    hideMetricFilter = false
}) => {
    const { t } = useTranslation(['filters', 'common']);
    
    const handleTimeRangeChange = (e: SelectChangeEvent<string>) => {
        onTimeRangeChange(e.target.value as TimeRange);
    };

    const handleRefreshIntervalChange = (e: SelectChangeEvent<string>) => {
        onRefreshIntervalChange?.(e.target.value as RefreshInterval);
    };

    const handleMetricFilterChange = (e: SelectChangeEvent<string>) => {
        onMetricFilterChange?.(e.target.value as MetricFilter);
    };

    return (
        <Box sx={{ display: 'flex', gap: 2 }}>
            {/* Time Period Selector */}
            <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="time-range-label" size="small">
                    {t('filters:timePeriod')}
                </InputLabel>
                <Select
                    labelId="time-range-label"
                    id="time-range-select"
                    value={timeRange}
                    label={t('filters:timePeriod')}
                    size="small"
                    onChange={handleTimeRangeChange}
                >
                    <MenuItem value="1h">{t('filters:lastHour')}</MenuItem>
                    <MenuItem value="6h">{t('filters:last6Hours')}</MenuItem>
                    <MenuItem value="24h">{t('filters:last24Hours')}</MenuItem>
                    <MenuItem value="7d">{t('filters:last7Days')}</MenuItem>
                    <MenuItem value="14d">{t('filters:last14Days')}</MenuItem>
                    <MenuItem value="30d">{t('filters:last30Days')}</MenuItem>
                    <MenuItem value="90d">{t('filters:last90Days')}</MenuItem>
                    <MenuItem value="all">{t('filters:allTime')}</MenuItem>
                </Select>
            </FormControl>

            {/* Metric Filter Selector */}
            {!hideMetricFilter && onMetricFilterChange && (
                <FormControl variant="outlined" size="small" sx={{ minWidth: 140 }}>
                    <InputLabel id="metric-filter-label" size="small">
                        {t('filters:showMetric')}
                    </InputLabel>
                    <Select
                        labelId="metric-filter-label"
                        id="metric-filter-select"
                        value={metricFilter}
                        label={t('filters:showMetric')}
                        size="small"
                        onChange={handleMetricFilterChange}
                    >
                        <MenuItem value="all">{t('filters:allMetrics')}</MenuItem>
                        <MenuItem value="views">{t('common:views')}</MenuItem>
                        <MenuItem value="reactions">{t('common:reactions')}</MenuItem>
                        <MenuItem value="forwards">{t('common:forwards')}</MenuItem>
                        <MenuItem value="comments">{t('common:comments')}</MenuItem>
                    </Select>
                </FormControl>
            )}

            {/* Refresh Interval Selector */}
            {!hideRefreshControl && onRefreshIntervalChange && (
                <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                    <InputLabel id="refresh-interval-label" size="small">
                        {t('filters:refresh')}
                    </InputLabel>
                    <Select
                        labelId="refresh-interval-label"
                        id="refresh-interval-select"
                        value={refreshInterval}
                        label={t('filters:refresh')}
                        size="small"
                        onChange={handleRefreshIntervalChange}
                    >
                        <MenuItem value="30s">{t('filters:30seconds')}</MenuItem>
                        <MenuItem value="1m">{t('filters:1minute')}</MenuItem>
                        <MenuItem value="5m">{t('filters:5minutes')}</MenuItem>
                        <MenuItem value="10m">{t('filters:10minutes')}</MenuItem>
                    </Select>
                </FormControl>
            )}
        </Box>
    );
});

AdvancedTimeRangeControls.displayName = 'AdvancedTimeRangeControls';

export default AdvancedTimeRangeControls;
