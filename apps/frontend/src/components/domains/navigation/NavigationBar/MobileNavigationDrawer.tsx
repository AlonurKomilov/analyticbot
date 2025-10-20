import React from 'react';
import {
    Drawer,
    Box,
    Toolbar,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Divider,
    Typography,
    DrawerProps
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { NAVIGATION_CONFIG } from './navigationConfig';
import SmartBreadcrumbs from './SmartBreadcrumbs';

interface MobileNavigationDrawerProps extends Omit<DrawerProps, 'open'> {
    open: boolean;
    onClose: () => void;
    className?: string;
}

/**
 * MobileNavigationDrawer Component
 *
 * Handles mobile navigation drawer including:
 * - Slide-out navigation menu
 * - Complete route listing with icons
 * - Mobile-optimized breadcrumbs
 * - Active route highlighting
 * - Auto-close on navigation
 */
const MobileNavigationDrawer: React.FC<MobileNavigationDrawerProps> = ({
    open,
    onClose,
    className,
    ...props
}) => {
    const navigate = useNavigate();
    const location = useLocation();

    const handleNavigate = (path: string): void => {
        navigate(path);
        onClose(); // Close drawer after navigation
    };

    return (
        <Drawer
            anchor="left"
            open={open}
            onClose={onClose}
            className={className}
            PaperProps={{
                sx: {
                    width: 280,
                    backgroundColor: 'background.paper'
                }
            }}
            {...props}
        >
            {/* Account for AppBar height */}
            <Toolbar />

            <Box sx={{ p: 2 }}>
                {/* Mobile breadcrumbs */}
                <Box sx={{ mb: 2 }}>
                    <SmartBreadcrumbs
                        showOnMobile={true}
                        maxItems={4}
                    />
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* App Title */}
                <Typography
                    variant="h6"
                    sx={{
                        mb: 2,
                        fontWeight: 600,
                        color: 'primary.main',
                        textAlign: 'center'
                    }}
                >
                    AnalyticBot
                </Typography>

                {/* Navigation links */}
                <List disablePadding>
                    {NAVIGATION_CONFIG.routes.map((route) => {
                        const IconComponent = route.icon;
                        const isActive = location.pathname === route.path;

                        return (
                            <React.Fragment key={route.id}>
                                <ListItem disablePadding sx={{ mb: 1 }}>
                                    <ListItemButton
                                        onClick={() => handleNavigate(route.path)}
                                        selected={isActive}
                                        sx={{
                                            borderRadius: 2,
                                            minHeight: 56,
                                            '&.Mui-selected': {
                                                backgroundColor: 'primary.main',
                                                color: 'primary.contrastText',
                                                '& .MuiListItemIcon-root': {
                                                    color: 'inherit'
                                                },
                                                '&:hover': {
                                                    backgroundColor: 'primary.dark'
                                                }
                                            }
                                        }}
                                    >
                                        <ListItemIcon sx={{ minWidth: 48 }}>
                                            <IconComponent />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={
                                                <Typography
                                                    variant="body1"
                                                    sx={{ fontWeight: isActive ? 600 : 400 }}
                                                >
                                                    {route.label}
                                                </Typography>
                                            }
                                            secondary={
                                                <Typography
                                                    variant="caption"
                                                    sx={{
                                                        color: isActive ? 'inherit' : 'text.secondary',
                                                        opacity: isActive ? 0.8 : 1
                                                    }}
                                                >
                                                    {route.description}
                                                </Typography>
                                            }
                                        />
                                    </ListItemButton>
                                </ListItem>

                                {/* Show children for AI Services */}
                                {route.children && isActive && (
                                    <Box sx={{ pl: 2, mb: 1 }}>
                                        {route.children.map((child) => (
                                            <ListItem key={child.id} disablePadding sx={{ mb: 0.5 }}>
                                                <ListItemButton
                                                    onClick={() => handleNavigate(child.path)}
                                                    selected={location.pathname === child.path}
                                                    sx={{
                                                        borderRadius: 1,
                                                        minHeight: 40,
                                                        pl: 4
                                                    }}
                                                >
                                                    <ListItemText
                                                        primary={
                                                            <Typography variant="body2">
                                                                {child.label}
                                                            </Typography>
                                                        }
                                                        secondary={
                                                            <Typography
                                                                variant="caption"
                                                                color="text.secondary"
                                                            >
                                                                {child.description}
                                                            </Typography>
                                                        }
                                                    />
                                                </ListItemButton>
                                            </ListItem>
                                        ))}
                                    </Box>
                                )}
                            </React.Fragment>
                        );
                    })}
                </List>

                <Divider sx={{ my: 2 }} />

                {/* Quick Actions Section */}
                <Typography
                    variant="subtitle2"
                    color="text.secondary"
                    sx={{ mb: 1, px: 1 }}
                >
                    Quick Actions
                </Typography>
                <List dense>
                    {NAVIGATION_CONFIG.quickActions.map((action) => {
                        const IconComponent = action.icon;

                        return (
                            <ListItem key={action.id} disablePadding>
                                <ListItemButton
                                    onClick={() => {
                                        if (action.action === 'navigate' && action.target) {
                                            handleNavigate(action.target);
                                        } else {
                                            console.log(`Execute action: ${action.id}`);
                                            onClose();
                                        }
                                    }}
                                    sx={{
                                        borderRadius: 1,
                                        minHeight: 40
                                    }}
                                >
                                    <ListItemIcon sx={{ minWidth: 36 }}>
                                        <IconComponent fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={
                                            <Typography variant="body2">
                                                {action.label}
                                            </Typography>
                                        }
                                    />
                                    {action.shortcut && (
                                        <Typography
                                            variant="caption"
                                            color="text.disabled"
                                            sx={{ ml: 1 }}
                                        >
                                            {action.shortcut}
                                        </Typography>
                                    )}
                                </ListItemButton>
                            </ListItem>
                        );
                    })}
                </List>
            </Box>
        </Drawer>
    );
};

export default MobileNavigationDrawer;
