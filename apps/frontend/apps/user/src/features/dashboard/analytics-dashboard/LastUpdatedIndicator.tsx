/**
 * LastUpdatedIndicator Component
 *
 * Compact status dot indicator - matches MTProto Monitoring page style.
 * Shows next to page title with minimal UI.
 *
 * States:
 * - 🔵 Blue pulsing = Currently refreshing/updating
 * - 🟢 Green = Live and connected
 */

import React from 'react';
import {
    Box,
    Typography
} from '@mui/material';

interface LastUpdatedIndicatorProps {
    lastUpdated: Date;
    isLoading?: boolean;
}

const LastUpdatedIndicator: React.FC<LastUpdatedIndicatorProps> = ({
    lastUpdated,
    isLoading = false
}) => {
    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Compact Pulsing Dot - Blue when loading, Green when idle */}
            <Box
                sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: isLoading ? 'primary.main' : 'success.main',
                    animation: isLoading ? 'pulse 1s ease-in-out infinite' : 'none',
                    boxShadow: isLoading
                        ? '0 0 8px rgba(25, 118, 210, 0.6)'
                        : '0 0 6px rgba(46, 125, 50, 0.4)',
                    '@keyframes pulse': {
                        '0%, 100%': {
                            opacity: 1,
                            transform: 'scale(1)',
                        },
                        '50%': {
                            opacity: 0.6,
                            transform: 'scale(1.2)',
                        },
                    },
                }}
                title={isLoading ? 'Updating data...' : 'Live - Connected'}
            />
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                Last updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
        </Box>
    );
};

export default LastUpdatedIndicator;
