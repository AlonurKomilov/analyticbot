/**
 * LastUpdatedIndicator Component
 *
 * Shows timestamp of last data refresh with auto-update capability.
 * Provides visual feedback on data freshness.
 *
 * Quick Win #4: Real-Time Update Indicator
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Chip,
    Tooltip
} from '@mui/material';
import {
    AccessTime as ClockIcon,
    FiberManualRecord as DotIcon
} from '@mui/icons-material';

interface LastUpdatedIndicatorProps {
    lastUpdated: Date;
    autoRefreshInterval?: number; // in seconds
    onRefresh?: () => void;
}

const LastUpdatedIndicator: React.FC<LastUpdatedIndicatorProps> = ({
    lastUpdated,
    autoRefreshInterval,
    onRefresh
}) => {
    const [timeAgo, setTimeAgo] = useState<string>('');
    const [freshness, setFreshness] = useState<'fresh' | 'recent' | 'stale'>('fresh');

    useEffect(() => {
        const updateTimeAgo = () => {
            const now = new Date();
            const diffInSeconds = Math.floor((now.getTime() - lastUpdated.getTime()) / 1000);

            let displayText = '';
            let freshnessLevel: 'fresh' | 'recent' | 'stale' = 'fresh';

            if (diffInSeconds < 60) {
                displayText = 'Just now';
                freshnessLevel = 'fresh';
            } else if (diffInSeconds < 3600) {
                const minutes = Math.floor(diffInSeconds / 60);
                displayText = `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
                freshnessLevel = diffInSeconds < 300 ? 'fresh' : 'recent'; // 5 minutes threshold
            } else if (diffInSeconds < 86400) {
                const hours = Math.floor(diffInSeconds / 3600);
                displayText = `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
                freshnessLevel = 'stale';
            } else {
                const days = Math.floor(diffInSeconds / 86400);
                displayText = `${days} ${days === 1 ? 'day' : 'days'} ago`;
                freshnessLevel = 'stale';
            }

            setTimeAgo(displayText);
            setFreshness(freshnessLevel);
        };

        updateTimeAgo();
        const interval = setInterval(updateTimeAgo, 1000); // Update every second

        return () => clearInterval(interval);
    }, [lastUpdated]);

    // Auto-refresh functionality
    useEffect(() => {
        if (!autoRefreshInterval || !onRefresh) return;

        const interval = setInterval(() => {
            onRefresh();
        }, autoRefreshInterval * 1000);

        return () => clearInterval(interval);
    }, [autoRefreshInterval, onRefresh]);

    const getColor = () => {
        switch (freshness) {
            case 'fresh':
                return 'success';
            case 'recent':
                return 'warning';
            case 'stale':
                return 'default';
        }
    };

    const getDotColor = () => {
        switch (freshness) {
            case 'fresh':
                return '#4caf50';
            case 'recent':
                return '#ff9800';
            case 'stale':
                return '#9e9e9e';
        }
    };

    return (
        <Tooltip
            title={
                <Box>
                    <div>Last updated: {lastUpdated.toLocaleString()}</div>
                    {autoRefreshInterval && (
                        <div style={{ marginTop: 4, fontSize: '0.85em', opacity: 0.9 }}>
                            Auto-refresh: Every {autoRefreshInterval}s
                        </div>
                    )}
                </Box>
            }
            arrow
        >
            <Chip
                icon={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <DotIcon
                            sx={{
                                fontSize: 12,
                                color: getDotColor(),
                                animation: freshness === 'fresh' ? 'pulse 2s infinite' : 'none',
                                '@keyframes pulse': {
                                    '0%, 100%': {
                                        opacity: 1
                                    },
                                    '50%': {
                                        opacity: 0.5
                                    }
                                }
                            }}
                        />
                        <ClockIcon sx={{ fontSize: 16 }} />
                    </Box>
                }
                label={`Updated ${timeAgo}`}
                size="small"
                color={getColor()}
                variant="outlined"
                sx={{
                    fontWeight: 500,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                        transform: 'scale(1.05)'
                    }
                }}
            />
        </Tooltip>
    );
};

export default LastUpdatedIndicator;
