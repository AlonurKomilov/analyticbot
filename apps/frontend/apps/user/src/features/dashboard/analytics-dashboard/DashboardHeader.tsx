import React from 'react';
import {
    Collapse,
    Box
} from '@mui/material';
import DataSourceSettings from '@shared/components/ui/DataSourceSettings';
import ChannelSelector from '@shared/components/ui/ChannelSelector';
import { useChannelStore } from '@store';

interface DashboardHeaderProps {
    showSettings: boolean;
    onToggleSettings?: () => void;
    onDataSourceChange: (source: string) => void;
}

/**
 * DashboardHeader Component
 *
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Handles channel selector and data source controls
 *
 * Responsibilities:
 * - Channel selection
 * - Collapsible data source settings
 */
const DashboardHeader: React.FC<DashboardHeaderProps> = React.memo(({
    showSettings,
    onDataSourceChange
}) => {
    // Get channel store to sync selected channel
    const { selectChannel } = useChannelStore();

    // Handle channel selection - sync with global store
    const handleChannelChange = (channel: any) => {
        console.log('🔄 DashboardHeader: Channel changed:', channel);
        selectChannel(channel);
    };

    return (
        <>
            {/* Channel Selector - Primary Action */}
            <Box sx={{ mb: 3 }}>
                <ChannelSelector
                    onChannelChange={handleChannelChange}
                    showCreateButton={false}
                    showRefreshButton={true}
                    size="medium"
                    fullWidth={true}
                />
            </Box>

            {/* Data Source Settings - Collapsible */}
            <Collapse in={showSettings}>
                <div id="data-source-settings">
                    <DataSourceSettings onDataSourceChange={onDataSourceChange} />
                </div>
            </Collapse>
        </>
    );
});

DashboardHeader.displayName = 'DashboardHeader';

export default DashboardHeader;
