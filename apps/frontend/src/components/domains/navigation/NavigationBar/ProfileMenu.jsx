import React, { useState } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Avatar,
    Tooltip,
    Divider,
    Typography,
    Box,
    Chip
} from '@mui/material';
import {
    Person as PersonIcon,
    Settings as SettingsIcon,
    Help as HelpIcon,
    Logout as LogoutIcon,
    Brightness4 as DarkModeIcon,
    Brightness7 as LightModeIcon,
    AccountCircle as AccountIcon,
    AdminPanelSettings as AdminIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useNavigation } from '../../../../components/common/NavigationProvider';
import { useAuth } from '../../../../contexts/AuthContext';
import { AdminOnly } from '../../../auth/RoleGuard';

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
    const { user, logout, isAuthenticated } = useAuth();

    // Menu anchor state
    const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);

    // Don't render if not authenticated
    if (!isAuthenticated) {
        return null;
    }

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

    const handleAdminClick = () => {
        navigate('/admin');
        handleMenuClose();
    };

    const handleThemeToggle = () => {
        toggleTheme();
        // Keep menu open for theme toggle
    };

    const handleLogout = async () => {
        try {
            await logout();
            // AuthContext will handle redirect to login
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            handleMenuClose();
        }
    };

    return (
        <>
            {/* Profile Avatar Button */}
            <Tooltip title={`${user?.username || 'User'} - Profile & Settings`} placement="bottom">
                <IconButton
                    onClick={handleMenuOpen}
                    className={className}
                    sx={{ ml: 1 }}
                    aria-label="Profile menu"
                    {...props}
                >
                    <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                        {user?.username ? user.username.charAt(0).toUpperCase() : <AccountIcon />}
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
                        minWidth: 250,
                        mt: 1
                    }
                }}
            >
                {/* User Info Header */}
                <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
                    <Typography variant="subtitle2" fontWeight="bold">
                        {user?.full_name || user?.username || 'User'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {user?.email}
                    </Typography>
                    <Chip
                        label={user?.role || 'User'}
                        size="small"
                        color="primary"
                        variant="outlined"
                    />
                </Box>

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

                {/* Admin Dashboard - Only for admin users */}
                <AdminOnly>
                    <MenuItem onClick={handleAdminClick}>
                        <ListItemIcon>
                            <AdminIcon />
                        </ListItemIcon>
                        <ListItemText>Admin Dashboard</ListItemText>
                    </MenuItem>
                </AdminOnly>

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
