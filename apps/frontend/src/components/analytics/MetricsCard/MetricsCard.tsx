import React, { useState } from 'react';

interface Metrics {
    totalViews?: number;
    growthRate?: number;
    engagementRate?: number;
    reachScore?: number;
}

interface MetricsCardProps {
    metrics?: Metrics | null;
    loading?: boolean;
    onRefresh?: () => void;
    showDetails?: boolean;
}
import {
    Card,
    CardContent,
    Typography,
    Box,
    IconButton,
    Tooltip,
    LinearProgress
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Refresh as RefreshIcon,
    Analytics as AnalyticsIcon
} from '@mui/icons-material';

// Import extracted components (JSX - not yet migrated)
import MetricsGrid from './MetricsGrid';
import MetricsDetails from './MetricsDetails';
import PerformanceInsights from './PerformanceInsights';

// Type assertions for JSX components
const TypedMetricsGrid = MetricsGrid as any;
const TypedMetricsDetails = MetricsDetails as any;
const TypedPerformanceInsights = PerformanceInsights as any;

const MetricsCard: React.FC<MetricsCardProps> = React.memo(({
    metrics,
    loading = false,
    onRefresh,
    showDetails = true
}) => {
    const [expanded, setExpanded] = useState(false);

    if (loading) {
        return (
            <Card sx={{ minHeight: 200 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Loading Metrics...
                    </Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                </CardContent>
            </Card>
        );
    }

    if (!metrics) {
        return (
            <Card sx={{ minHeight: 200 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        No Metrics Available
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Metrics data is not available at the moment.
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card sx={{
            height: '100%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'visible'
        }}>
            <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AnalyticsIcon />
                        Performance Metrics
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        {onRefresh && (
                            <Tooltip title="Refresh metrics">
                                <IconButton size="small" onClick={onRefresh} sx={{ color: 'white' }}>
                                    <RefreshIcon />
                                </IconButton>
                            </Tooltip>
                        )}
                        {showDetails && (
                            <Tooltip title={expanded ? "Show less" : "Show more"}>
                                <IconButton
                                    size="small"
                                    onClick={() => setExpanded(!expanded)}
                                    sx={{ color: 'white' }}
                                >
                                    {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                </IconButton>
                            </Tooltip>
                        )}
                    </Box>
                </Box>

                {/* Main Metrics Grid */}
                <TypedMetricsGrid metrics={metrics} />

                {/* Expanded Details */}
                {showDetails && (
                    <TypedMetricsDetails
                        metrics={metrics}
                        expanded={expanded}
                    />
                )}

                {/* Performance Insights */}
                {expanded && (
                    <TypedPerformanceInsights metrics={metrics} />
                )}
            </CardContent>
        </Card>
    );
});

MetricsCard.displayName = 'MetricsCard';

export default MetricsCard;
