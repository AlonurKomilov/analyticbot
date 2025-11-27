import React from 'react';
import {
    Paper,
    Tabs,
    Tab,
    Box,
    Typography
} from '@mui/material';
import {
    TrendingUp as TrendingIcon,
    Dashboard as DashboardIcon,
    Schedule as ScheduleIcon,
    Analytics as AnalyticsIcon,
    Security as SecurityIcon
} from '@mui/icons-material';
import ChannelSelector from '@shared/components/ui/ChannelSelector';

interface TabConfigItem {
    icon: React.ReactElement;
    label: string;
    id: string;
    controls: string;
    specialColor?: string;
}

interface DashboardTabsProps {
    activeTab: number;
    onTabChange: (event: React.SyntheticEvent, newValue: number) => void;
    isLoading?: boolean;
    lastUpdated?: Date;
    onChannelChange?: (channel: any) => void;
}

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
const DashboardTabs: React.FC<DashboardTabsProps> = React.memo(({
    activeTab,
    onTabChange,
    isLoading = false,
    lastUpdated,
    onChannelChange
}) => {
    const tabConfig: TabConfigItem[] = [
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
            label: "Special Time Recommendations",
            id: "analytics-tab-2",
            controls: "analytics-tabpanel-2"
        },
        {
            icon: <AnalyticsIcon />,
            label: "Analytics Overview",
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

    // Format timestamp
    const formatTime = (date: Date | undefined) => {
        if (!date) return '';
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
    };

    return (
        <nav aria-label="Analytics navigation">
            {/* Status Header - Analytics Overview style */}
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 3 }}>
                <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                            Analytics Overview
                        </Typography>
                        {/* Status dot indicator */}
                        <Box
                            sx={{
                                width: 12,
                                height: 12,
                                borderRadius: '50%',
                                backgroundColor: isLoading ? '#2196F3' : '#4caf50',
                                animation: isLoading ? 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' : 'none',
                                '@keyframes pulse': {
                                    '0%, 100%': {
                                        opacity: 1,
                                    },
                                    '50%': {
                                        opacity: 0.5,
                                    },
                                }
                            }}
                            aria-label={isLoading ? 'Refreshing data' : 'Data is current'}
                        />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                        Real-time performance metrics for your content
                    </Typography>
                    {lastUpdated && (
                        <Typography variant="caption" color="text.secondary">
                            Last updated: {formatTime(lastUpdated)}
                        </Typography>
                    )}
                </Box>

                {/* Channel Selector */}
                <Box sx={{ minWidth: 300 }}>
                    <ChannelSelector
                        onChannelChange={onChannelChange}
                        showCreateButton={false}
                        showRefreshButton={true}
                        size="small"
                        fullWidth={true}
                    />
                </Box>
            </Box>

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
