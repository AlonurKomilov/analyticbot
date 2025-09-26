import React from 'react';
import {
    Box,
    Typography,
    Breadcrumbs,
    Link,
    Collapse,
    Alert
} from '@mui/material';
import {
    Home as HomeIcon,
    Analytics as AnalyticsIcon,
    NavigateNext as NavigateNextIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Security as SecurityIcon
} from '@mui/icons-material';
import DataSourceSettings from '../../DataSourceSettings';

/**
 * DashboardHeader Component
 * 
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Handles header, breadcrumbs, data source controls, and status alerts
 * 
 * Responsibilities:
 * - Breadcrumb navigation
 * - Collapsible data source settings
 * - Status alert messages
 */
const DashboardHeader = React.memo(({
    showSettings,
    onToggleSettings,
    onDataSourceChange
}) => {
    return (
        <>
            {/* Breadcrumbs */}
            <nav aria-label="Breadcrumb navigation">
                <Breadcrumbs 
                    separator={<NavigateNextIcon fontSize="small" aria-hidden="true" />} 
                    sx={{ mb: 2 }}
                >
                    <Link 
                        underline="hover" 
                        color="inherit" 
                        href="/"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                        aria-label="Go to homepage"
                    >
                        <HomeIcon fontSize="small" aria-hidden="true" />
                        Home
                    </Link>
                    <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <AnalyticsIcon fontSize="small" aria-hidden="true" />
                        Analytics Dashboard
                    </Typography>
                </Breadcrumbs>
            </nav>

            {/* Live region for announcements */}
            <div aria-live="polite" aria-atomic="true" className="sr-only">
                Analytics dashboard loaded
            </div>

            {/* Data Source Settings - Collapsible */}
            <Collapse in={showSettings}>
                <div id="data-source-settings">
                    <DataSourceSettings onDataSourceChange={onDataSourceChange} />
                </div>
            </Collapse>

            {/* Alert for Current Status */}
            <Alert 
                severity="success" 
                sx={{ mb: 3 }}
                icon={<SecurityIcon />}
                role="status"
            >
                <strong>🛡️ NEW: Week 5-6 Content Protection Available!</strong> Click the "Content Protection" tab below to access watermarking and theft detection tools. 
                Premium features include image watermarking, content scanning, and security tools.
            </Alert>
        </>
    );
});

DashboardHeader.displayName = 'DashboardHeader';

export default DashboardHeader;