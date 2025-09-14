import React, { useState } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Avatar,
    Tooltip,
    Divider
} from '@mui/material';
import {
    Person as PersonIcon,
    Settings as SettingsIcon,
    Help as HelpIcon,
    Logout as LogoutIcon,
    Brightness4 as DarkModeIcon,
    Brightness7 as LightModeIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useNavigation } from '../../../../components/common/NavigationProvider';

/**
 * ProfileMenu Component
 * 
 * Handles user profile dropdown menu including:
 * - User avatar display
 * - Profile navigation
 * - Settings access
 * - Theme toggle
 * - Help & support
 * - Logout functionality
 */
const ProfileMenu = ({ className, ...props }) => {
    const navigate = useNavigate();
    const { isDarkMode, toggleTheme } = useNavigation();
    
    // Menu anchor state
    const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);
    
    // Menu open/close handlers
    const handleMenuOpen = (event) => {
        setProfileMenuAnchor(event.currentTarget);
    };
    
    const handleMenuClose = () => {
        setProfileMenuAnchor(null);
    };
    
    // Navigation handlers
    const handleProfileClick = () => {
        navigate('/profile');
        handleMenuClose();
    };
    
    const handleSettingsClick = () => {
        navigate('/settings');
        handleMenuClose();
    };
    
    const handleHelpClick = () => {
        navigate('/help');
        handleMenuClose();
    };
    
    const handleThemeToggle = () => {
        toggleTheme();
        // Keep menu open for theme toggle
    };
    
    const handleLogout = () => {
        // TODO: Implement actual logout logic
        // Clear user session, redirect to login, etc.
        handleMenuClose();
    };

    return (
        <>
            {/* Profile Avatar Button */}
            <Tooltip title="Profile & Settings" placement="bottom">
                <IconButton
                    onClick={handleMenuOpen}
                    className={className}
                    sx={{ ml: 1 }}
                    aria-label="Profile menu"
                    {...props}
                >
                    <Avatar sx={{ width: 32, height: 32 }}>
                        <PersonIcon />
                    </Avatar>
                </IconButton>
            </Tooltip>

            {/* Profile Menu */}
            <Menu
                anchorEl={profileMenuAnchor}
                open={Boolean(profileMenuAnchor)}
                onClose={handleMenuClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                PaperProps={{
                    sx: {
                        minWidth: 200,
                        mt: 1
                    }
                }}
            >
                {/* Profile */}
                <MenuItem onClick={handleProfileClick}>
                    <ListItemIcon>
                        <PersonIcon />
                    </ListItemIcon>
                    <ListItemText>Profile</ListItemText>
                </MenuItem>

                {/* Settings */}
                <MenuItem onClick={handleSettingsClick}>
                    <ListItemIcon>
                        <SettingsIcon />
                    </ListItemIcon>
                    <ListItemText>Settings</ListItemText>
                </MenuItem>

                {/* Theme Toggle */}
                <MenuItem onClick={handleThemeToggle}>
                    <ListItemIcon>
                        {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
                    </ListItemIcon>
                    <ListItemText>
                        {isDarkMode ? 'Light Mode' : 'Dark Mode'}
                    </ListItemText>
                </MenuItem>

                {/* Help & Support */}
                <MenuItem onClick={handleHelpClick}>
                    <ListItemIcon>
                        <HelpIcon />
                    </ListItemIcon>
                    <ListItemText>Help & Support</ListItemText>
                </MenuItem>

                <Divider />

                {/* Logout */}
                <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                        <LogoutIcon />
                    </ListItemIcon>
                    <ListItemText>Logout</ListItemText>
                </MenuItem>
            </Menu>
        </>
    );
};

export default ProfileMenu;