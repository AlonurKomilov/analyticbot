/**
 * Tab Panel Component
 * Reusable tab panel wrapper
 */

import React from 'react';
import { Box } from '@mui/material';
import type { TabPanelProps } from './types';

export const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`profile-tabpanel-${index}`}
        aria-labelledby={`profile-tab-${index}`}
    >
        {value === index && (
            <Box sx={{ pt: 3 }}>
                {children}
            </Box>
        )}
    </div>
);
