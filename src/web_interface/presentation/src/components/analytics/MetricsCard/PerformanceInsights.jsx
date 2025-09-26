import React from 'react';
import {
    Box,
    Typography,
    Chip
} from '@mui/material';

const PerformanceInsights = React.memo(({ metrics }) => {
    const {
        totalViews = 0,
        growthRate = 0,
        engagementRate = 0,
        performanceScore = 0
    } = metrics;

    const insights = [];

    // Generate insights based on thresholds
    if (growthRate > 10) {
        insights.push({
            label: "🚀 High Growth",
            color: 'rgba(76, 175, 80, 0.8)'
        });
    }

    if (engagementRate > 5) {
        insights.push({
            label: "💡 Great Engagement", 
            color: 'rgba(33, 150, 243, 0.8)'
        });
    }

    if (performanceScore > 80) {
        insights.push({
            label: "⭐ Excellent Performance",
            color: 'rgba(255, 193, 7, 0.8)'
        });
    }

    if (totalViews > 10000) {
        insights.push({
            label: "👥 Popular Content",
            color: 'rgba(156, 39, 176, 0.8)'
        });
    }

    // Add warning insights
    if (growthRate < -5) {
        insights.push({
            label: "📉 Declining Growth",
            color: 'rgba(244, 67, 54, 0.8)'
        });
    }

    if (engagementRate < 2) {
        insights.push({
            label: "⚠️ Low Engagement",
            color: 'rgba(255, 152, 0, 0.8)'
        });
    }

    if (insights.length === 0) {
        return null;
    }

    return (
        <Box sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                Quick Insights:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {insights.map((insight, index) => (
                    <Chip 
                        key={index}
                        label={insight.label} 
                        size="small" 
                        sx={{ bgcolor: insight.color, color: 'white' }} 
                    />
                ))}
            </Box>
        </Box>
    );
});

PerformanceInsights.displayName = 'PerformanceInsights';

export default PerformanceInsights;