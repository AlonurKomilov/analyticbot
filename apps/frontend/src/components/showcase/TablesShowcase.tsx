/**
 * TablesShowcase Component - Refactored Orchestrator
 *
 * Reduced from 437 lines to ~80 lines by extracting components:
 * - ShowcaseNavigation: Tab management and navigation
 * - ShowcaseLayout: Shared layout and feature summary
 * - PostsTableDemo: Top Posts table demonstration
 * - UsersTableDemo: User Management table demonstration
 * - GenericTableDemo: Generic data table demonstration
 *
 * Benefits:
 * - 82% reduction in component size (437 → ~80 lines)
 * - Better separation of concerns
 * - Improved maintainability and testability
 * - Individual component reusability
 */

import React, { useState } from 'react';
import { Alert } from '@mui/material';
import ShowcaseLayout from './ShowcaseLayout.jsx';
import ShowcaseNavigation, { TabPanel } from './ShowcaseNavigation.jsx';
// Import demo components with mock data from __mocks__
import PostsTableDemo from '../../__mocks__/components/showcase/tables/PostsTableDemo';
import UsersTableDemo from '../../__mocks__/components/showcase/tables/UsersTableDemo';
import GenericTableDemo from '../../__mocks__/components/showcase/tables/GenericTableDemo';

/**
 * Main Tables Showcase Orchestrator
 *
 * Coordinates the showcase components while maintaining all original functionality.
 * Now focused purely on state management and component coordination.
 */
const TablesShowcase: React.FC = () => {
    const [activeTab, setActiveTab] = useState<number>(0);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
        setActiveTab(newValue);
    };

    return (
        <ShowcaseLayout>
            {/* Showcase Alert */}
            <Alert severity="info" sx={{ mb: 3 }}>
                <strong>Enhanced Data Tables Showcase:</strong> Explore three different implementations
                of our enterprise-grade data table system with advanced features like sorting,
                filtering, bulk operations, and export capabilities.
            </Alert>

            {/* Navigation Tabs */}
            <ShowcaseNavigation
                activeTab={activeTab}
                onTabChange={handleTabChange}
            />

            {/* Tab Content */}
            <TabPanel value={activeTab} index={0}>
                <PostsTableDemo />
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
                <UsersTableDemo />
            </TabPanel>

            <TabPanel value={activeTab} index={2}>
                <GenericTableDemo />
            </TabPanel>
        </ShowcaseLayout>
    );
};

export default TablesShowcase;
