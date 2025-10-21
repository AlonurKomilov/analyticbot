/**
 * ShowcaseNavigation Component
 *
 * Extracted from DataTablesShowcase - handles tab navigation
 * and tab panel rendering with proper accessibility
 */

import React, { ReactNode } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import {
    Analytics as AnalyticsIcon,
    People as PeopleIcon,
    TableChart as TableIcon
} from '@mui/icons-material';

interface TabPanelProps {
    children: ReactNode;
    value: number;
    index: number;
}

// Accessible TabPanel component
export const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`showcase-tabpanel-${index}`}
        aria-labelledby={`showcase-tab-${index}`}
        {...other}
    >
        {value === index && (
            <Box sx={{ py: 3 }}>
                {children}
            </Box>
        )}
    </div>
);

interface TabConfigItem {
    label: string;
    icon: React.ReactElement;
    ariaLabel: string;
}

// Tab navigation configuration
const tabConfig: TabConfigItem[] = [
    {
        label: 'Top Posts Analytics',
        icon: <AnalyticsIcon />,
        ariaLabel: 'Top posts analytics table showcase'
    },
    {
        label: 'User Management',
        icon: <PeopleIcon />,
        ariaLabel: 'User management table showcase'
    },
    {
        label: 'Generic Data Table',
        icon: <TableIcon />,
        ariaLabel: 'Generic data table showcase'
    }
];

interface ShowcaseNavigationProps {
    activeTab: number;
    onTabChange: (event: React.SyntheticEvent, newValue: number) => void;
}

const ShowcaseNavigation: React.FC<ShowcaseNavigationProps> = ({ activeTab, onTabChange }) => {
    return (
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs
                value={activeTab}
                onChange={onTabChange}
                variant="fullWidth"
                aria-label="Data tables showcase navigation"
                sx={{
                    '& .MuiTab-root': {
                        minHeight: 64,
                        textTransform: 'none',
                        fontSize: '1rem',
                        fontWeight: 500
                    }
                }}
            >
                {tabConfig.map((tab, index) => (
                    <Tab
                        key={index}
                        icon={tab.icon}
                        label={tab.label}
                        id={`showcase-tab-${index}`}
                        aria-controls={`showcase-tabpanel-${index}`}
                        aria-label={tab.ariaLabel}
                        iconPosition="start"
                        sx={{
                            '& .MuiTab-iconWrapper': {
                                marginBottom: 0,
                                marginRight: 1
                            }
                        }}
                    />
                ))}
            </Tabs>
        </Box>
    );
};

export default ShowcaseNavigation;
