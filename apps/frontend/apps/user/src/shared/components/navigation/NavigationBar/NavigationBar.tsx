/**
 * 🧭 Navigation Bar Component
 *
 * Top navigation bar for authenticated users, includes sidebar for desktop.
 * Profile menu is in top-right corner like modern platforms.
 *
 * @component
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    AppBar,
    Avatar,
    Box,
    Chip,
    Divider,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Menu,
    MenuItem,
    Toolbar,
    Tooltip,
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
    Psychology as AIIcon,
    Payment as PaymentIcon,
    Person as PersonIcon,
    Tv as ChannelIcon,
    SmartToy as BotIcon,
    Logout as LogoutIcon,
    MonetizationOn as CreditsIcon,
    EmojiEvents as TrophyIcon,
    Store as StoreIcon,
    Memory as MTProtoIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { ROUTES } from '@config/routes';
import { useAuth } from '@/contexts/AuthContext';
import { LanguageSwitcher } from '@shared/components/LanguageSwitcher';

const DRAWER_WIDTH = 260;

interface NavItem {
    labelKey: string;
    path: string;
    icon: React.ReactElement;
    dividerBefore?: boolean;  // Show divider before this item
    sectionLabel?: string;    // Section header label
}

// Navigation items with translation keys
const NAV_ITEMS: NavItem[] = [
    { labelKey: 'sidebar.dashboard', path: ROUTES.DASHBOARD, icon: <DashboardIcon /> },
    { labelKey: 'sidebar.analytics', path: ROUTES.ANALYTICS, icon: <AnalyticsIcon /> },
    { labelKey: 'sidebar.channels', path: ROUTES.CHANNELS, icon: <ChannelIcon /> },
    { labelKey: 'sidebar.posts', path: ROUTES.POSTS, icon: <ArticleIcon /> },
    { labelKey: 'aiServices', path: ROUTES.AI_SERVICES, icon: <AIIcon /> },
    // Workers Section
    { labelKey: 'workers.bot', path: ROUTES.WORKERS_BOT, icon: <BotIcon />, dividerBefore: true, sectionLabel: 'Workers' },
    { labelKey: 'workers.mtproto', path: ROUTES.WORKERS_MTPROTO, icon: <MTProtoIcon /> },
    // Credits & Payments Section
    { labelKey: 'credits', path: ROUTES.CREDITS, icon: <CreditsIcon />, dividerBefore: true },
    { labelKey: 'rewards', path: ROUTES.REWARDS, icon: <TrophyIcon /> },
    { labelKey: 'marketplace', path: ROUTES.MARKETPLACE, icon: <StoreIcon /> },
    { labelKey: 'payment', path: ROUTES.PAYMENT, icon: <PaymentIcon /> },
    // Settings
    { labelKey: 'sidebar.settings', path: ROUTES.SETTINGS, icon: <SettingsIcon />, dividerBefore: true },
];

const NavigationBar: React.FC = () => {
    const { t } = useTranslation('navigation');
    const { t: tCommon } = useTranslation('common');
    const theme = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const [mobileOpen, setMobileOpen] = useState(false);

    // Profile menu state
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const profileMenuOpen = Boolean(anchorEl);

    // Get user and logout from auth context (same as Security page uses)
    const { user, logout } = useAuth();

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const handleNavigation = (path: string) => {
        navigate(path);
        if (isMobile) {
            setMobileOpen(false);
        }
    };

    const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleProfileClose = () => {
        setAnchorEl(null);
    };

    const handleProfileNavigate = (path: string) => {
        navigate(path);
        handleProfileClose();
    };

    const handleLogout = async () => {
        handleProfileClose();
        await logout();  // This calls API and redirects to /login
    };

    // Get user initials for avatar
    const getUserInitials = () => {
        if (!user) return '?';

        // Try full_name first (from API)
        if (user.full_name) {
            const parts = user.full_name.trim().split(' ');
            if (parts.length >= 2) {
                return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
            }
            return user.full_name[0].toUpperCase();
        }

        // Try firstName/lastName
        if (user.firstName && user.lastName) {
            return `${user.firstName[0]}${user.lastName[0]}`.toUpperCase();
        }
        if (user.firstName) {
            return user.firstName[0].toUpperCase();
        }

        // Fallback to email
        if (user.email) {
            return user.email[0].toUpperCase();
        }
        return '?';
    };

    // Get display name
    const getDisplayName = () => {
        if (!user) return 'User';

        // Try full_name first (from API)
        if (user.full_name) {
            return user.full_name;
        }

        // Try firstName/lastName
        if (user.firstName && user.lastName) {
            return `${user.firstName} ${user.lastName}`;
        }
        if (user.firstName) {
            return user.firstName;
        }

        // Fallback to username or email
        return user.username || user.email || 'User';
    };

    const drawerContent = (
        <Box>
            <Toolbar>
                <Typography variant="h6" noWrap component="div">
                    {tCommon('appName')}
                </Typography>
            </Toolbar>
            <List>
                {NAV_ITEMS.map((item, index) => (
                    <React.Fragment key={item.path}>
                        {/* Show divider before this item if specified */}
                        {item.dividerBefore && index > 0 && <Divider sx={{ my: 1 }} />}
                        
                        {/* Show section label if specified */}
                        {item.sectionLabel && (
                            <Typography
                                variant="overline"
                                sx={{
                                    px: 2,
                                    py: 0.5,
                                    color: 'text.secondary',
                                    fontWeight: 600,
                                    fontSize: '0.7rem',
                                }}
                            >
                                {item.sectionLabel}
                            </Typography>
                        )}
                        
                        <ListItem disablePadding>
                            <ListItemButton
                                selected={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
                                onClick={() => handleNavigation(item.path)}
                            >
                                <ListItemIcon>{item.icon}</ListItemIcon>
                                <ListItemText primary={t(item.labelKey as any)} />
                            </ListItemButton>
                        </ListItem>
                    </React.Fragment>
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
                    <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                        {tCommon('appName')}
                    </Typography>

                    {/* Language Switcher */}
                    <LanguageSwitcher size="small" color="inherit" />

                    {/* Credit Balance Display */}
                    {user && (
                        <Tooltip title={t('userMenu.credits', 'Your credit balance')} arrow>
                            <Chip
                                icon={<CreditsIcon sx={{ fontSize: '1rem' }} />}
                                label={`${(user.credit_balance ?? 0).toLocaleString()} ${tCommon('credits', 'credits')}`}
                                size="small"
                                onClick={() => navigate(ROUTES.CREDITS)}
                                sx={{
                                    mr: 2,
                                    cursor: 'pointer',
                                    bgcolor: theme.palette.mode === 'dark'
                                        ? 'rgba(255, 215, 0, 0.15)'
                                        : 'rgba(255, 193, 7, 0.15)',
                                    color: theme.palette.mode === 'dark'
                                        ? '#FFD700'
                                        : '#F9A825',
                                    fontWeight: 600,
                                    '&:hover': {
                                        bgcolor: theme.palette.mode === 'dark'
                                            ? 'rgba(255, 215, 0, 0.25)'
                                            : 'rgba(255, 193, 7, 0.25)',
                                    },
                                    '& .MuiChip-icon': {
                                        color: 'inherit',
                                    },
                                }}
                            />
                        </Tooltip>
                    )}

                    {/* Profile Avatar Button */}
                    <IconButton
                        onClick={handleProfileClick}
                        size="small"
                        sx={{ ml: 2 }}
                        aria-controls={profileMenuOpen ? 'profile-menu' : undefined}
                        aria-haspopup="true"
                        aria-expanded={profileMenuOpen ? 'true' : undefined}
                    >
                        <Avatar
                            sx={{
                                width: 36,
                                height: 36,
                                bgcolor: theme.palette.primary.light,
                                fontSize: '0.9rem',
                                fontWeight: 600,
                            }}
                        >
                            {getUserInitials()}
                        </Avatar>
                    </IconButton>

                    {/* Profile Dropdown Menu */}
                    <Menu
                        id="profile-menu"
                        anchorEl={anchorEl}
                        open={profileMenuOpen}
                        onClose={handleProfileClose}
                        onClick={handleProfileClose}
                        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                        PaperProps={{
                            elevation: 3,
                            sx: {
                                mt: 1,
                                minWidth: 200,
                                '& .MuiMenuItem-root': {
                                    py: 1.5,
                                },
                            },
                        }}
                    >
                        {/* User Info Header */}
                        <Box sx={{ px: 2, py: 1.5 }}>
                            <Typography variant="subtitle1" fontWeight={600}>
                                {getDisplayName()}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {user?.email}
                            </Typography>
                        </Box>
                        <Divider />

                        {/* Menu Items */}
                        <MenuItem onClick={() => handleProfileNavigate(ROUTES.PROFILE)}>
                            <ListItemIcon>
                                <PersonIcon fontSize="small" />
                            </ListItemIcon>
                            {t('userMenu.profile')}
                        </MenuItem>
                        <MenuItem onClick={() => handleProfileNavigate(ROUTES.CREDITS)}>
                            <ListItemIcon>
                                <CreditsIcon fontSize="small" sx={{ color: '#FFD700' }} />
                            </ListItemIcon>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                                <span>{t('userMenu.credits', 'Credits')}</span>
                                <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                                    {(user?.credit_balance ?? 0).toLocaleString()}
                                </Typography>
                            </Box>
                        </MenuItem>
                        <MenuItem onClick={() => handleProfileNavigate(ROUTES.SETTINGS)}>
                            <ListItemIcon>
                                <SettingsIcon fontSize="small" />
                            </ListItemIcon>
                            {t('userMenu.settings')}
                        </MenuItem>
                        <Divider />
                        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                            <ListItemIcon>
                                <LogoutIcon fontSize="small" sx={{ color: 'error.main' }} />
                            </ListItemIcon>
                            {t('userMenu.logout')}
                        </MenuItem>
                    </Menu>
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
