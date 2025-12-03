import React from 'react';
import { Box } from '@mui/material';
import { StatusChip } from '@shared/components';

/**
 * Props for the ChartDataInsights component
 */
interface ChartDataInsightsProps {
    /** Chart data array */
    data?: Array<{
        views: number;
        engagement: number;
    }>;
}

const ChartDataInsights: React.FC<ChartDataInsightsProps> = React.memo(({ data }) => {
    if (!data || data.length === 0) {
        return null;
    }

    const dataPointsCount = data.length;
    const peakViews = Math.max(...data.map(d => d.views));
    const avgEngagement = (data.reduce((acc, d) => acc + d.engagement, 0) / data.length).toFixed(0);

    return (
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <StatusChip
                label={`${dataPointsCount} data points`}
                size="small"
                status="info"
            />
            <StatusChip
                label={`Peak: ${peakViews.toLocaleString()} views`}
                size="small"
                status="success"
            />
            <StatusChip
                label={`Avg engagement: ${avgEngagement}`}
                size="small"
                status="info"
            />
        </Box>
    );
});

ChartDataInsights.displayName = 'ChartDataInsights';

export default ChartDataInsights;
