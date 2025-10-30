/**
 * 🧭 Navigation Bar Component
 *
 * Top navigation bar for authenticated users, includes sidebar for desktop.
 *
 * @component
 */

import React, { useState } from 'react';
import {
    AppBar,
    Box,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
    useMediaQuery,
    useTheme,
} from '@mui/material';
import {
    Menu as MenuIcon,
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Article as ArticleIcon,
    Settings as SettingsIcon,
    AdminPanelSettings as AdminIcon,
    Psychology as AIIcon,
    Payment as PaymentIcon,
    Person as PersonIcon,
    Tv as ChannelIcon,
    SmartToy as BotIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { ROUTES } from '@config/routes';

const DRAWER_WIDTH = 260;

interface NavItem {
    label: string;
    path: string;
    icon: React.ReactElement;
}

const NAV_ITEMS: NavItem[] = [
    { label: 'Dashboard', path: ROUTES.DASHBOARD, icon: <DashboardIcon /> },
    { label: 'Analytics', path: ROUTES.ANALYTICS, icon: <AnalyticsIcon /> },
    { label: 'Channels', path: ROUTES.CHANNELS, icon: <ChannelIcon /> },
    { label: 'Posts', path: ROUTES.POSTS, icon: <ArticleIcon /> },
    { label: 'AI Services', path: ROUTES.AI_SERVICES, icon: <AIIcon /> },
    { label: 'My Bot', path: '/bot/dashboard', icon: <BotIcon /> },
    { label: 'Payment', path: ROUTES.PAYMENT, icon: <PaymentIcon /> },
    { label: 'Profile', path: ROUTES.PROFILE, icon: <PersonIcon /> },
    { label: 'Settings', path: ROUTES.SETTINGS, icon: <SettingsIcon /> },
    { label: 'Admin', path: ROUTES.ADMIN, icon: <AdminIcon /> },
    { label: 'Admin Bots', path: '/admin/bots', icon: <AdminIcon /> },
];

const NavigationBar: React.FC = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const [mobileOpen, setMobileOpen] = useState(false);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const handleNavigation = (path: string) => {
        navigate(path);
        if (isMobile) {
            setMobileOpen(false);
        }
    };

    const drawerContent = (
        <Box>
            <Toolbar>
                <Typography variant="h6" noWrap component="div">
                    AnalyticBot
                </Typography>
            </Toolbar>
            <List>
                {NAV_ITEMS.map((item) => (
                    <ListItem key={item.path} disablePadding>
                        <ListItemButton
                            selected={location.pathname === item.path}
                            onClick={() => handleNavigation(item.path)}
                        >
                            <ListItemIcon>{item.icon}</ListItemIcon>
                            <ListItemText primary={item.label} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </Box>
    );

    return (
        <>
            {/* Top AppBar */}
            <AppBar
                position="fixed"
                sx={{
                    zIndex: theme.zIndex.drawer + 1,
                }}
            >
                <Toolbar>
                    {isMobile && (
                        <IconButton
                            color="inherit"
                            edge="start"
                            onClick={handleDrawerToggle}
                            sx={{ mr: 2 }}
                        >
                            <MenuIcon />
                        </IconButton>
                    )}
                    <Typography variant="h6" noWrap component="div">
                        AnalyticBot
                    </Typography>
                </Toolbar>
            </AppBar>

            {/* Desktop Sidebar */}
            {!isMobile && (
                <Drawer
                    variant="permanent"
                    sx={{
                        width: DRAWER_WIDTH,
                        flexShrink: 0,
                        '& .MuiDrawer-paper': {
                            width: DRAWER_WIDTH,
                            boxSizing: 'border-box',
                        },
                    }}
                >
                    {drawerContent}
                </Drawer>
            )}

            {/* Mobile Drawer */}
            {isMobile && (
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    ModalProps={{
                        keepMounted: true, // Better mobile performance
                    }}
                    sx={{
                        '& .MuiDrawer-paper': {
                            width: DRAWER_WIDTH,
                            boxSizing: 'border-box',
                        },
                    }}
                >
                    {drawerContent}
                </Drawer>
            )}
        </>
    );
};

export default NavigationBar;
