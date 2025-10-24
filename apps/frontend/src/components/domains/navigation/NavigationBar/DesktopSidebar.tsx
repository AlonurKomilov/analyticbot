import React from 'react';
import {
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Box,
    Typography,
    Divider,
    Toolbar
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { NAVIGATION_CONFIG, type NavigationRoute } from './navigationConfig';
import { Icon } from '@components/common/IconSystem';

const DRAWER_WIDTH = 260;

/**
 * DesktopSidebar Component
 *
 * Permanent sidebar for desktop screens showing navigation menu
 * with icons, labels, and active state indicators
 */
const DesktopSidebar: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const handleNavigation = (path: string) => {
        navigate(path);
    };

    const isActiveRoute = (path: string): boolean => {
        return location.pathname === path || location.pathname.startsWith(`${path}/`);
    };

    // Group routes by category
    const coreRoutes = NAVIGATION_CONFIG.routes.filter(
        (route) => route.category === 'Core'
    );
    const contentRoutes = NAVIGATION_CONFIG.routes.filter(
        (route) => route.category === 'Content'
    );
    const analyticsRoutes = NAVIGATION_CONFIG.routes.filter(
        (route) => route.category === 'Analytics'
    );
    const systemRoutes = NAVIGATION_CONFIG.routes.filter(
        (route) => route.category === 'System'
    );

    const renderRouteItem = (route: NavigationRoute) => {
        const isActive = isActiveRoute(route.path);

        return (
            <ListItem key={route.id} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                    onClick={() => handleNavigation(route.path)}
                    sx={{
                        borderRadius: 1,
                        mx: 1,
                        '&:hover': {
                            backgroundColor: 'action.hover',
                        },
                        ...(isActive && {
                            backgroundColor: 'primary.main',
                            color: 'primary.contrastText',
                            '&:hover': {
                                backgroundColor: 'primary.dark',
                            },
                            '& .MuiListItemIcon-root': {
                                color: 'primary.contrastText',
                            },
                        }),
                    }}
                >
                    <ListItemIcon
                        sx={{
                            minWidth: 40,
                            color: isActive ? 'inherit' : 'text.secondary',
                        }}
                    >
                        {route.icon ? (
                            <route.icon />
                        ) : (
                            <Icon name="dashboard" size="sm" />
                        )}
                    </ListItemIcon>
                    <ListItemText
                        primary={route.label}
                        primaryTypographyProps={{
                            fontSize: '0.9rem',
                            fontWeight: isActive ? 600 : 400,
                        }}
                    />
                </ListItemButton>
            </ListItem>
        );
    };

    const renderCategory = (title: string, routes: NavigationRoute[]) => {
        if (routes.length === 0) return null;

        return (
            <Box sx={{ mb: 2 }}>
                <Typography
                    variant="caption"
                    sx={{
                        px: 3,
                        py: 1,
                        display: 'block',
                        color: 'text.secondary',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        letterSpacing: 1,
                    }}
                >
                    {title}
                </Typography>
                <List disablePadding>
                    {routes.map(renderRouteItem)}
                </List>
            </Box>
        );
    };

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: DRAWER_WIDTH,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: DRAWER_WIDTH,
                    boxSizing: 'border-box',
                    borderRight: '1px solid',
                    borderColor: 'divider',
                    backgroundColor: 'background.paper',
                },
            }}
        >
            {/* Toolbar spacer to push content below AppBar */}
            <Toolbar />

            <Box
                sx={{
                    overflow: 'auto',
                    py: 2,
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                }}
            >
                {/* Core navigation */}
                {renderCategory('Core', coreRoutes)}

                {/* Content management */}
                {contentRoutes.length > 0 && (
                    <>
                        <Divider sx={{ mx: 2, my: 1 }} />
                        {renderCategory('Content', contentRoutes)}
                    </>
                )}

                {/* Analytics */}
                {analyticsRoutes.length > 0 && (
                    <>
                        <Divider sx={{ mx: 2, my: 1 }} />
                        {renderCategory('Analytics', analyticsRoutes)}
                    </>
                )}

                {/* System routes */}
                {systemRoutes.length > 0 && (
                    <>
                        <Divider sx={{ mx: 2, my: 1 }} />
                        {renderCategory('System', systemRoutes)}
                    </>
                )}

                {/* Spacer to push footer to bottom */}
                <Box sx={{ flexGrow: 1 }} />

                {/* Footer info */}
                <Box sx={{ px: 3, py: 2, mt: 2 }}>
                    <Typography
                        variant="caption"
                        sx={{
                            color: 'text.disabled',
                            display: 'block',
                            textAlign: 'center',
                        }}
                    >
                        AnalyticBot v1.0
                    </Typography>
                </Box>
            </Box>
        </Drawer>
    );
};

export default DesktopSidebar;
export { DRAWER_WIDTH };
