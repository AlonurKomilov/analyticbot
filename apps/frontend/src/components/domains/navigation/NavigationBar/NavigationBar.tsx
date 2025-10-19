import React, { useState } from 'react';
import {
    AppBar,
    Toolbar,
    Typography,
    Box,
    IconButton,
    useMediaQuery,
    useTheme,
    SxProps,
    Theme
} from '@mui/material';
import {
    Menu as MenuIcon,
    Brightness4 as DarkModeIcon,
    Brightness7 as LightModeIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useNavigation } from '@components/common/NavigationProvider';
import { Icon } from '@components/common/IconSystem';

// Import extracted components
import GlobalSearchBar from './GlobalSearchBar';
import ProfileMenu from './ProfileMenu';
import NotificationMenu from './NotificationMenu';
import SmartBreadcrumbs from './SmartBreadcrumbs';
import MobileNavigationDrawer from './MobileNavigationDrawer';
import GlobalDataSourceSwitch from '@components/common/GlobalDataSourceSwitch';

/**
 * Simplified NavigationBar Component
 *
 * Orchestrates navigation sub-components:
 * - GlobalSearchBar: Search functionality and dialog
 * - ProfileMenu: User profile and settings dropdown
 * - NotificationMenu: Notifications badge and dropdown
 * - SmartBreadcrumbs: Dynamic breadcrumb navigation
 * - MobileNavigationDrawer: Mobile-specific navigation
 *
 * Reduced from 833 lines to ~200 lines while maintaining full functionality
 */
const NavigationBar: React.FC = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const navigate = useNavigate();

    // Navigation context
    const { isDarkMode, toggleTheme } = useNavigation();

    // Mobile drawer state
    const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

    const handleMobileMenuToggle = (): void => {
        setMobileMenuOpen(true);
    };

    const handleMobileMenuClose = (): void => {
        setMobileMenuOpen(false);
    };

    const handleLogoClick = (): void => {
        navigate('/');
    };

    return (
        <>
            {/* Main AppBar */}
            <AppBar
                position="fixed"
                elevation={1}
                sx={{
                    zIndex: (theme: Theme) => theme.zIndex.drawer + 1,
                    backgroundColor: 'background.paper',
                    color: 'text.primary',
                    borderBottom: '1px solid',
                    borderColor: 'divider'
                }}
            >
                <Toolbar sx={{ minHeight: { xs: 64, sm: 70 } }}>
                    {/* Mobile menu button */}
                    {isMobile && (
                        <IconButton
                            edge="start"
                            onClick={handleMobileMenuToggle}
                            sx={{ mr: 2 }}
                            aria-label="Open navigation menu"
                        >
                            <MenuIcon />
                        </IconButton>
                    )}

                    {/* Logo and title */}
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            cursor: 'pointer',
                            mr: 3
                        }}
                        onClick={handleLogoClick}
                    >
                        <Icon
                            name="analytics"
                            size="lg"
                            sx={{ mr: 1, color: 'primary.main' } as SxProps<Theme>}
                        />
                        <Typography
                            variant="h6"
                            component="h1"
                            sx={{
                                fontWeight: 600,
                                display: { xs: 'none', sm: 'block' }
                            }}
                        >
                            AnalyticBot
                        </Typography>
                    </Box>

                    {/* Desktop breadcrumbs */}
                    {!isMobile && (
                        <SmartBreadcrumbs
                            className=""
                            maxItems={3}
                        />
                    )}

                    {/* Right side actions */}
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        ml: 'auto'
                    }}>
                        {/* Global Search */}
                        <GlobalSearchBar {...({className: ""} as any)} />

                        {/* Data Source Switch */}
                        <GlobalDataSourceSwitch showLabel={!isMobile} {...({className: ""} as any)} />

                        {/* Theme toggle */}
                        <IconButton
                            onClick={toggleTheme}
                            aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
                            sx={{
                                '&:hover': {
                                    backgroundColor: 'action.hover'
                                }
                            }}
                        >
                            {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
                        </IconButton>

                        {/* Notifications */}
                        <NotificationMenu {...({className: ""} as any)} />

                        {/* Profile menu */}
                        <ProfileMenu {...({className: ""} as any)} />
                    </Box>
                </Toolbar>
            </AppBar>

            {/* Mobile Navigation Drawer */}
            <MobileNavigationDrawer
                open={mobileMenuOpen}
                onClose={handleMobileMenuClose}
                {...({className: ""} as any)}
            />
        </>
    );
};

export default NavigationBar;
