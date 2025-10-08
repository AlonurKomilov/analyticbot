import React from 'react';
import { Box } from '@mui/material';
import { StatusChip } from '../../common';

const ChartDataInsights = React.memo(({ data }) => {
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
                variant="primary"
            />
            <StatusChip
                label={`Peak: ${peakViews.toLocaleString()} views`}
                size="small"
                variant="success"
            />
            <StatusChip
                label={`Avg engagement: ${avgEngagement}`}
                size="small"
                variant="info"
            />
        </Box>
    );
});

ChartDataInsights.displayName = 'ChartDataInsights';

export default ChartDataInsights;
