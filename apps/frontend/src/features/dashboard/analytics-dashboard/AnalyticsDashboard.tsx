import React, { useState, useEffect, SyntheticEvent } from 'react';
import {
    Box,
    Container,
    Paper
} from '@mui/material';

// Import refactored components
import DashboardTabs from './DashboardTabs';
import LoadingOverlay from './LoadingOverlay';
import DashboardSpeedDial from './DashboardSpeedDial';
import TabPanel from './TabPanel';

// Import Quick Win components
import DataSourceBanner from './DataSourceBanner';

// Import existing components
import PostViewDynamicsChart from '@shared/components/charts/PostViewDynamics';
import { EnhancedTopPostsTable } from '@features/posts';
import { SpecialTimesRecommender } from '@features/analytics';
import { AdvancedAnalyticsDashboard } from '@features/analytics';
import SmartAlertsPanel from '@features/analytics/advanced-dashboard/SmartAlertsPanel';
import ContentProtectionDashboard from '@features/posts/components/ContentProtectionDashboard';
import ApiFailureDialog from '@shared/components/dialogs/ApiFailureDialog';
import { useChannelStore, useUIStore, useAnalyticsStore } from '@store';
import { useApiFailureDialog } from '@shared/hooks';

/**
 * AnalyticsDashboard - Refactored Orchestrator Component
 *
 * Phase 3.1 Refactoring - Reduced from 539 lines to ~150 lines
 *
 * This is the main orchestrator component that coordinates all extracted
 * dashboard sub-components while maintaining existing functionality.
 *
 * Extracted Components:
 * - DashboardHeader: Header, breadcrumbs, settings
 * - SummaryStatsGrid: Statistics cards
 * - DashboardTabs: Tab navigation
 * - LoadingOverlay: Loading states
 * - DashboardSpeedDial: Quick actions
 * - TabPanel: Accessible tab content
 *
 * Benefits:
 * - 72% reduction in component size (539 → ~150 lines)
 * - Independent component memoization
 * - Better maintainability and testability
 * - Preserved all existing functionality
 */
const AnalyticsDashboard: React.FC = React.memo(() => {
    const [activeTab, setActiveTab] = useState<number>(0);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
    const [isLoading, setIsLoading] = useState<boolean>(false);

    // Store integration
    const { setDataSource, dataSource } = useUIStore();
    const { loadChannels, selectedChannel } = useChannelStore() as any;
    const { clearAnalytics } = useAnalyticsStore();

    // Determine channel ID based on data source mode
    // 'api' = Real API with real channel, 'demo'/'mock' = Demo mode with demo channel
    const channelId = (dataSource === 'demo' || dataSource === 'mock')
        ? 'demo_channel'
        : (selectedChannel?.id?.toString() || null);

    // API failure dialog management
    const {
        isDialogOpen: isApiFailureDialogOpen,
        currentError: apiError,
        isRetrying,
        handleRetryConnection,
        handleSwitchToMock,
        handleCloseDialog: closeApiFailureDialog
    } = useApiFailureDialog();

    // Auto-refresh functionality
    useEffect(() => {
        const interval = setInterval(() => {
            setLastUpdated(new Date());
        }, 60000); // Update every minute

        return () => clearInterval(interval);
    }, []);

    // Handle data source change
    const handleDataSourceChange = async (newSource: string): Promise<void> => {
        setDataSource(newSource as any);
        setIsLoading(true);

        try {
            await loadChannels();
            clearAnalytics();
            setLastUpdated(new Date());

            // Force refresh of analytics data with new source
            setTimeout(() => {
                window.dispatchEvent(new CustomEvent('dataSourceChanged', {
                    detail: { source: newSource }
                }));
            }, 100);
        } catch (error) {
            console.error('Error switching data source:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTabChange = (_event: SyntheticEvent, newValue: number): void => {
        setActiveTab(newValue);
    };

    const handleRefresh = async (): Promise<void> => {
        // Silent background refresh - no loading spinner
        // Just update the timestamp and let components fetch new data
        setTimeout(() => {
            setLastUpdated(new Date());
            // Components watching lastUpdated will refresh their data automatically
        }, 100);
    };

    const handleSwitchToRealData = async (): Promise<void> => {
        await handleDataSourceChange('api');
    };

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Data Source Banner - Quick Win #3 */}
            <DataSourceBanner onSwitchToRealData={handleSwitchToRealData} />

            {/* Navigation Tabs */}
            <DashboardTabs
                activeTab={activeTab}
                onTabChange={handleTabChange}
                isLoading={isLoading}
                lastUpdated={lastUpdated}
                onChannelChange={(channel) => {
                    const { selectChannel } = useChannelStore.getState();
                    selectChannel(channel);
                }}
            />

            {/* Tab Content */}
            <main role="main">
                <TabPanel value={activeTab} index={0}>
                    {/* Chart Component with integrated summary stats */}
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <PostViewDynamicsChart />
                    </Paper>
                </TabPanel>

                <TabPanel value={activeTab} index={1}>
                    <EnhancedTopPostsTable lastUpdated={lastUpdated} />
                </TabPanel>

                <TabPanel value={activeTab} index={2}>
                    <SpecialTimesRecommender lastUpdated={lastUpdated} />
                </TabPanel>

                <TabPanel value={activeTab} index={3}>
                    {/* Smart Alerts & Analytics Overview */}
                    <SmartAlertsPanel channelId={channelId} />
                    <Box sx={{ mt: 3 }}>
                        <AdvancedAnalyticsDashboard channelId={channelId} lastUpdated={lastUpdated} />
                    </Box>
                </TabPanel>

                <TabPanel value={activeTab} index={4}>
                    {/* Week 5-6 Content Protection */}
                    <ContentProtectionDashboard channelId={channelId} lastUpdated={lastUpdated} />
                </TabPanel>
            </main>

            {/* Quick Actions Speed Dial */}
            <DashboardSpeedDial
                onRefresh={handleRefresh}
                onSettings={() => {}}
            />

            {/* Loading State */}
            <LoadingOverlay isVisible={isLoading} />

            {/* API Failure Dialog */}
            <ApiFailureDialog
                open={isApiFailureDialogOpen}
                onClose={closeApiFailureDialog}
                onRetry={handleRetryConnection}
                onSwitchToMock={handleSwitchToMock}
                error={apiError as any}
                isRetrying={isRetrying}
            />
        </Container>
    );
});

AnalyticsDashboard.displayName = 'AnalyticsDashboard';

export default AnalyticsDashboard;
