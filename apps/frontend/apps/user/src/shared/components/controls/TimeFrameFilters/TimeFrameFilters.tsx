/**
 * TimeFrameFilters Component
 * Unified filter controls for AI posting time recommendations
 *
 * Supports:
 * - Time frame selection with standard periods
 * - Optional total posts analyzed display
 * - Optional content type breakdown
 * - Optional title with icon
 *
 * @example
 * ```tsx
 * <TimeFrameFilters
 *   timeFrame="30d"
 *   setTimeFrame={setTimeFrame}
 *   totalPostsAnalyzed={1234}
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
    Typography,
    SelectChangeEvent,
    Chip
} from '@mui/material';
import { Psychology as AIIcon } from '@mui/icons-material';
import type { TimeFrameFiltersProps, TimeFrame } from './types';

const TimeFrameFilters: React.FC<TimeFrameFiltersProps> = ({
    timeFrame,
    setTimeFrame,
    totalPostsAnalyzed,
    contentTypeBreakdown,
    title,
    showIcon = false
}) => {
    const { t } = useTranslation('filters');
    const handleTimeFrameChange = (event: SelectChangeEvent) => {
        setTimeFrame(event.target.value as TimeFrame);
    };

    // Get contextual chip for time frame
    const getTimeFrameChip = () => {
        if (totalPostsAnalyzed !== undefined && totalPostsAnalyzed > 0) {
            const breakdownText = contentTypeBreakdown
                ? ` (Text: ${contentTypeBreakdown.text || 0}, Video: ${contentTypeBreakdown.video || 0}, Image: ${contentTypeBreakdown.image || 0}, Link: ${contentTypeBreakdown.link || 0})`
                : '';
            return (
                <Chip
                    label={`${totalPostsAnalyzed.toLocaleString()} posts analyzed${breakdownText}`}
                    color="primary"
                    size="small"
                    sx={{ fontWeight: 500 }}
                />
            );
        }

        if (timeFrame === 'all') {
            return (
                <Chip
                    label="Analyzing complete history (up to 10k posts)"
                    color="primary"
                    size="small"
                    sx={{ fontWeight: 500 }}
                />
            );
        }

        if (timeFrame === '1y') {
            return (
                <Chip
                    label="Last 365 days"
                    color="info"
                    size="small"
                />
            );
        }

        return null;
    };

    return (
        <Box sx={{ mb: 3 }}>
            {/* Optional title with icon */}
            {title && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    {showIcon && <AIIcon color="primary" />}
                    <Typography variant="h5" component="h1">
                        {title}
                    </Typography>
                </Box>
            )}

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                <FormControl size="small" sx={{ minWidth: 200 }}>
                    <InputLabel id="timeframe-label">{t('filters.analysisPeriod')}</InputLabel>
                    <Select
                        labelId="timeframe-label"
                        value={timeFrame}
                        label={t('filters.analysisPeriod')}
                        onChange={handleTimeFrameChange}
                    >
                        <MenuItem value="1h">{t('timePeriods.lastHour')}</MenuItem>
                        <MenuItem value="6h">{t('timePeriods.last6Hours')}</MenuItem>
                        <MenuItem value="24h">{t('timePeriods.last24Hours')}</MenuItem>
                        <MenuItem value="7d">{t('timePeriods.last7Days')}</MenuItem>
                        <MenuItem value="30d">{t('timePeriods.last30Days')}</MenuItem>
                        <MenuItem value="90d">{t('timePeriods.last90Days')}</MenuItem>
                        <MenuItem value="180d">{t('common.last180Days')}</MenuItem>
                        <MenuItem value="1y">{t('common.lastYear')}</MenuItem>
                        <MenuItem value="all">{t('timePeriods.allTime')}</MenuItem>
                    </Select>
                </FormControl>

                {getTimeFrameChip()}
            </Box>
        </Box>
    );
};

export default TimeFrameFilters;
