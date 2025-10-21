import React from 'react';
import { Box } from '@mui/material';

interface TabPanelProps {
  /** Content to display in the tab panel */
  children?: React.ReactNode;
  /** Current active tab value */
  value: number;
  /** Index of this tab panel */
  index: number;
  /** Additional props to spread on the root element */
  [key: string]: any;
}

/**
 * TabPanel Component
 * Utility component for rendering tab content with proper ARIA attributes
 *
 * @component
 * @example
 * ```tsx
 * <TabPanel value={activeTab} index={0}>
 *   <Typography>Tab 1 content</Typography>
 * </TabPanel>
 * ```
 */
const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`admin-tabpanel-${index}`}
        aria-labelledby={`admin-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
);

export default TabPanel;
