import React from 'react';
import { Box, Chip } from '@mui/material';

const ChartDataInsights = React.memo(({ data }) => {
    if (!data || data.length === 0) {
        return null;
    }

    const dataPointsCount = data.length;
    const peakViews = Math.max(...data.map(d => d.views));
    const avgEngagement = (data.reduce((acc, d) => acc + d.engagement, 0) / data.length).toFixed(0);

    return (
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Chip 
                label={`${dataPointsCount} data points`} 
                size="small" 
                color="primary" 
                variant="outlined" 
            />
            <Chip 
                label={`Peak: ${peakViews.toLocaleString()} views`} 
                size="small" 
                color="success" 
                variant="outlined" 
            />
            <Chip 
                label={`Avg engagement: ${avgEngagement}`} 
                size="small" 
                color="info" 
                variant="outlined" 
            />
        </Box>
    );
});

ChartDataInsights.displayName = 'ChartDataInsights';

export default ChartDataInsights;