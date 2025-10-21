import React from 'react';
import { Box } from '@mui/material';

/**
 * Props for the TabPanel component
 */
interface TabPanelProps {
    /** Child content to render when tab is active */
    children?: React.ReactNode;
    /** Current active tab value */
    value: number;
    /** This panel's index */
    index: number;
}

/**
 * TabPanel Component
 *
 * Extracted from AnalyticsDashboard.jsx (Phase 3.1)
 * Provides accessible tab panel container for dashboard content
 *
 * Responsibilities:
 * - ARIA-compliant tab panel implementation
 * - Proper hiding/showing of content based on active tab
 * - Keyboard navigation support
 * - Screen reader accessibility
 * - Consistent padding for all tab content
 *
 * Note: Uses `inert` attribute instead of `aria-hidden` to prevent
 * focus issues when tab panels contain interactive elements
 */
const TabPanel: React.FC<TabPanelProps> = React.memo(({ children, value, index, ...other }) => {
    const isActive = value === index;
    
    return (
        <section
            role="tabpanel"
            hidden={!isActive}
            id={`analytics-tabpanel-${index}`}
            aria-labelledby={`analytics-tab-${index}`}
            {...(isActive ? {} : { inert: '' as any })} // Use inert instead of aria-hidden
            tabIndex={isActive ? 0 : -1}
            style={{
                display: isActive ? 'block' : 'none' // Ensure hidden panels are not rendered
            }}
            {...other}
        >
            {isActive && <Box sx={{ py: 3 }}>{children}</Box>}
        </section>
    );
});

TabPanel.displayName = 'TabPanel';

export default TabPanel;
