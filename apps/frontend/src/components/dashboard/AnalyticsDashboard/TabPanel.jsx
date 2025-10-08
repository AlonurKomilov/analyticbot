import React from 'react';
import { Box } from '@mui/material';

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
 */
const TabPanel = React.memo(({ children, value, index, ...other }) => (
    <section
        role="tabpanel"
        hidden={value !== index}
        id={`analytics-tabpanel-${index}`}
        aria-labelledby={`analytics-tab-${index}`}
        aria-hidden={value !== index}
        tabIndex={value === index ? 0 : -1}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </section>
));

TabPanel.displayName = 'TabPanel';

export default TabPanel;
