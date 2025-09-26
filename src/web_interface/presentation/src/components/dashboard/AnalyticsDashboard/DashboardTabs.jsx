import React from 'react';
import {
    Paper,
    Tabs,
    Tab
} from '@mui/material';
import {
    TrendingUp as TrendingIcon,
    Dashboard as DashboardIcon,
    Schedule as ScheduleIcon,
    Analytics as AnalyticsIcon,
    Security as SecurityIcon
} from '@mui/icons-material';

/**
 * DashboardTabs Component
 * 
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Handles tab navigation system with accessibility features
 * 
 * Responsibilities:
 * - Tab navigation between dashboard sections
 * - ARIA compliance for screen readers
 * - Proper tab styling and focus management
 * - Full-width responsive layout
 * - Icon and text labels for each tab
 */
const DashboardTabs = React.memo(({ 
    activeTab, 
    onTabChange 
}) => {
    const tabConfig = [
        {
            icon: <TrendingIcon />,
            label: "Post Dynamics",
            id: "analytics-tab-0",
            controls: "analytics-tabpanel-0"
        },
        {
            icon: <DashboardIcon />,
            label: "Top Posts",
            id: "analytics-tab-1",
            controls: "analytics-tabpanel-1"
        },
        {
            icon: <ScheduleIcon />,
            label: "AI Time Recommendations",
            id: "analytics-tab-2",
            controls: "analytics-tabpanel-2"
        },
        {
            icon: <AnalyticsIcon />,
            label: "Advanced Analytics",
            id: "analytics-tab-3",
            controls: "analytics-tabpanel-3"
        },
        {
            icon: <SecurityIcon />,
            label: "🛡️ Content Protection",
            id: "analytics-tab-4",
            controls: "analytics-tabpanel-4",
            specialColor: 'primary.main'
        }
    ];

    return (
        <nav aria-label="Analytics navigation">
            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={activeTab}
                    onChange={onTabChange}
                    sx={{ 
                        borderBottom: 1, 
                        borderColor: 'divider',
                        '& .MuiTab-root': { 
                            minHeight: 64,
                            '&:focus-visible': {
                                outline: '2px solid #2196F3',
                                outlineOffset: '2px'
                            }
                        }
                    }}
                    variant="fullWidth"
                    aria-label="Analytics sections"
                >
                    {tabConfig.map((tab, index) => (
                        <Tab
                            key={index}
                            icon={tab.icon}
                            label={tab.label}
                            sx={{ 
                                fontSize: '0.9rem', 
                                fontWeight: 'bold',
                                ...(tab.specialColor && { color: tab.specialColor })
                            }}
                            id={tab.id}
                            aria-controls={tab.controls}
                        />
                    ))}
                </Tabs>
            </Paper>
        </nav>
    );
});

DashboardTabs.displayName = 'DashboardTabs';

export default DashboardTabs;