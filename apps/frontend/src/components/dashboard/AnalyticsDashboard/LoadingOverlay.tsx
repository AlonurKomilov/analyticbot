import React from 'react';
import {
    Box,
    Card,
    Typography
} from '@mui/material';
import {
    Refresh as RefreshIcon
} from '@mui/icons-material';

interface LoadingOverlayProps {
    isVisible: boolean;
    message?: string;
}

/**
 * LoadingOverlay Component
 *
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Displays loading state with full-screen overlay and animation
 *
 * Responsibilities:
 * - Full-screen loading overlay with backdrop
 * - Animated loading icon (spinning refresh icon)
 * - Accessible loading message
 * - Proper ARIA live region for screen readers
 * - Centered loading card with professional styling
 */
const LoadingOverlay: React.FC<LoadingOverlayProps> = React.memo(({
    isVisible,
    message = "Loading analytics data..."
}) => {
    if (!isVisible) return null;

    return (
        <>
            <Box
                data-testid="loading-overlay"
                sx={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    bgcolor: 'rgba(0,0,0,0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 9999
                }}
                role="status"
                aria-live="polite"
            >
                <Card sx={{ p: 3, textAlign: 'center' }}>
                    <RefreshIcon
                        sx={{
                            fontSize: 48,
                            color: 'primary.main',
                            mb: 2,
                            animation: 'spin 1s linear infinite'
                        }}
                    />
                    <Typography variant="h6">
                        {message}
                    </Typography>
                </Card>
            </Box>

            {/* Custom CSS for animations */}
            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </>
    );
});

LoadingOverlay.displayName = 'LoadingOverlay';

export default LoadingOverlay;
