import React from 'react';
import {
    SpeedDial,
    SpeedDialIcon,
    SpeedDialAction
} from '@mui/material';
import {
    Refresh as RefreshIcon,
    Download as DownloadIcon,
    Share as ShareIcon,
    Print as PrintIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

/**
 * DashboardSpeedDial Component
 * 
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Provides floating action button with quick access to common actions
 * 
 * Responsibilities:
 * - Floating action button positioned at bottom-right
 * - Quick access to refresh, export, share, print, and settings
 * - Proper ARIA labeling for accessibility
 * - Hover tooltips for each action
 * - Customizable action handlers
 */
const DashboardSpeedDial = React.memo(({ 
    onRefresh,
    onExport = () => {}, // TODO: Implement export functionality
    onShare = () => {}, // TODO: Implement share functionality
    onPrint = () => {}, // TODO: Implement print functionality
    onSettings
}) => {
    const speedDialActions = [
        { icon: <RefreshIcon />, name: 'Refresh', action: onRefresh },
        { icon: <DownloadIcon />, name: 'Export', action: onExport },
        { icon: <ShareIcon />, name: 'Share', action: onShare },
        { icon: <PrintIcon />, name: 'Print', action: onPrint },
        { icon: <SettingsIcon />, name: 'Settings', action: onSettings }
    ];

    return (
        <SpeedDial
            ariaLabel="Analytics Actions"
            sx={{ position: 'fixed', bottom: 16, right: 16 }}
            icon={<SpeedDialIcon />}
            open={false}
        >
            {speedDialActions.map((action) => (
                <SpeedDialAction
                    key={action.name}
                    icon={action.icon}
                    tooltipTitle={action.name}
                    onClick={action.action}
                />
            ))}
        </SpeedDial>
    );
});

DashboardSpeedDial.displayName = 'DashboardSpeedDial';

export default DashboardSpeedDial;