import React from 'react';
import {
    Box,
    Tabs,
    Tab
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    People as PeopleIcon,
    Security as SecurityIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

/**
 * Props for AdminTabNavigation component
 */
interface AdminTabNavigationProps {
    /** Currently active tab index */
    activeTab: number;
    /** Callback when tab changes */
    onTabChange: (newValue: number) => void;
}

/**
 * AdminTabNavigation Component
 * Navigation tabs for admin dashboard sections
 */
const AdminTabNavigation: React.FC<AdminTabNavigationProps> = ({ activeTab, onTabChange }) => {
    return (
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={(_e, newValue) => onTabChange(newValue)}>
                <Tab
                    icon={<DashboardIcon />}
                    label="Overview"
                    iconPosition="start"
                />
                <Tab
                    icon={<PeopleIcon />}
                    label="User Management"
                    iconPosition="start"
                />
                <Tab
                    icon={<SecurityIcon />}
                    label="Audit Logs"
                    iconPosition="start"
                />
                <Tab
                    icon={<SettingsIcon />}
                    label="System Config"
                    iconPosition="start"
                />
            </Tabs>
        </Box>
    );
};

export default AdminTabNavigation;
