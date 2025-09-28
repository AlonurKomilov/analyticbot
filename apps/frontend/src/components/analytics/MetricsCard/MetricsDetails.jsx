import React from 'react';
import {
    Grid,
    Box,
    Avatar,
    Typography,
    Divider,
    Collapse
} from '@mui/material';
import {
    Speed as SpeedIcon
} from '@mui/icons-material';
import { formatMetricValue } from './metricsUtils.jsx';

const MetricsDetails = React.memo(({ metrics, expanded }) => {
    const {
        reachScore = 0,
        activeUsers = 0,
        performanceScore = 0
    } = metrics;

    return (
        <Collapse in={expanded}>
            <Divider sx={{ my: 2, bgcolor: 'rgba(255,255,255,0.2)' }} />
            
            <Grid container spacing={2}>
                <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                        <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1, width: 32, height: 32 }}>
                            <SpeedIcon fontSize="small" />
                        </Avatar>
                        <Typography variant="h6" fontWeight="bold">
                            {formatMetricValue(reachScore, 'score')}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.9 }}>
                            Reach Score
                        </Typography>
                    </Box>
                </Grid>
                
                <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                        <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1, width: 32, height: 32 }}>
                            <Typography variant="body2" fontWeight="bold">
                                {Math.floor(activeUsers / 1000)}K
                            </Typography>
                        </Avatar>
                        <Typography variant="h6" fontWeight="bold">
                            {formatMetricValue(activeUsers, 'compact')}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.9 }}>
                            Active Users
                        </Typography>
                    </Box>
                </Grid>
            </Grid>

            {/* Performance Progress */}
            <Box sx={{ mt: 3 }}>
                <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                    Overall Performance: {formatMetricValue(performanceScore, 'score')}/100
                </Typography>
                <Box 
                    sx={{ 
                        width: '100%', 
                        height: 8, 
                        borderRadius: 4, 
                        bgcolor: 'rgba(255,255,255,0.2)' 
                    }}
                >
                    <Box 
                        sx={{ 
                            width: `${Math.min(performanceScore, 100)}%`, 
                            height: '100%', 
                            borderRadius: 4,
                            bgcolor: performanceScore >= 70 ? '#4caf50' : performanceScore >= 40 ? '#ff9800' : '#f44336'
                        }} 
                    />
                </Box>
            </Box>
        </Collapse>
    );
});

MetricsDetails.displayName = 'MetricsDetails';

export default MetricsDetails;