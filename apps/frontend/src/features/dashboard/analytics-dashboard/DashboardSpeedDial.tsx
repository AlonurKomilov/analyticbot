import React from 'react';
import {
    SpeedDial,
    SpeedDialIcon,
    SpeedDialAction,
    Snackbar,
    Alert
} from '@mui/material';
import {
    Refresh as RefreshIcon,
    Download as DownloadIcon,
    Share as ShareIcon,
    Print as PrintIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

interface DashboardSpeedDialProps {
    onRefresh: () => void;
    onExport?: () => void;
    onShare?: () => void;
    onPrint?: () => void;
    onSettings: () => void;
}

interface SpeedDialActionItem {
    icon: React.ReactElement;
    name: string;
    action: () => void;
}

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
const DashboardSpeedDial: React.FC<DashboardSpeedDialProps> = React.memo(({
    onRefresh,
    onExport,
    onShare,
    onPrint,
    onSettings
}) => {
    const [showComingSoon, setShowComingSoon] = React.useState(false);
    const [featureName, setFeatureName] = React.useState('');

    const handleComingSoon = (feature: string) => {
        setFeatureName(feature);
        setShowComingSoon(true);
    };

    const handleExport = () => {
        if (onExport) {
            onExport();
        } else {
            handleComingSoon('Export');
        }
    };

    const handleShare = () => {
        if (onShare) {
            onShare();
        } else {
            handleComingSoon('Share');
        }
    };

    const handlePrint = () => {
        if (onPrint) {
            onPrint();
        } else {
            // Basic print implementation
            window.print();
        }
    };

    const speedDialActions: SpeedDialActionItem[] = [
        { icon: <RefreshIcon />, name: 'Refresh', action: onRefresh },
        { icon: <DownloadIcon />, name: 'Export', action: handleExport },
        { icon: <ShareIcon />, name: 'Share', action: handleShare },
        { icon: <PrintIcon />, name: 'Print', action: handlePrint },
        { icon: <SettingsIcon />, name: 'Settings', action: onSettings }
    ];

    return (
        <>
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

            <Snackbar
                open={showComingSoon}
                autoHideDuration={3000}
                onClose={() => setShowComingSoon(false)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert severity="info" onClose={() => setShowComingSoon(false)}>
                    {featureName} feature coming soon!
                </Alert>
            </Snackbar>
        </>
    );
});

DashboardSpeedDial.displayName = 'DashboardSpeedDial';

export default DashboardSpeedDial;
