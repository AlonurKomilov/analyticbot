import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import {
    AppBar,
    Toolbar,
    Typography,
    Box,
    IconButton,
    TextField,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Avatar,
    Badge,
    Tooltip,
    Breadcrumbs,
    Link,
    Chip,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    Divider,
    InputAdornment,
    Dialog,
    DialogTitle,
    DialogContent,
    Fab,
    SpeedDial,
    SpeedDialAction,
    SpeedDialIcon,
    Autocomplete,
    Paper,
    useMediaQuery,
    useTheme,
    Collapse
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useNavigation } from './NavigationProvider';
import GlobalSearchDialog from './GlobalSearchDialog';
import ExportButton from './ExportButton';
import ShareButton from './ShareButton';
import {
    Search as SearchIcon,
    Menu as MenuIcon,
    Notifications as NotificationsIcon,
    Settings as SettingsIcon,
    Person as PersonIcon,
    Home as HomeIcon,
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Build as ServicesIcon,
    TableChart as TablesIcon,
    NavigateNext as NavigateNextIcon,
    Logout as LogoutIcon,
    Help as HelpIcon,
    Brightness4 as DarkModeIcon,
    Brightness7 as LightModeIcon,
    Add as AddIcon,
    Edit as EditIcon,
    Share as ShareIcon,
    Download as DownloadIcon,
    Close as CloseIcon,
    KeyboardCommandKey as CommandIcon,
    History as RecentIcon,
    Bookmark as BookmarkIcon,
    ExpandLess,
    ExpandMore,
    Launch as LaunchIcon
} from '@mui/icons-material';
import { Icon } from './IconSystem';

/**
 * Advanced Navigation System
 * 
 * Enterprise-grade navigation with:
 * - Global search with command palette
 * - Intelligent breadcrumb system
 * - Responsive mobile navigation
 * - Quick actions and shortcuts
 * - User context management
 * - Navigation analytics
 * - Theme and settings integration
 */

// Navigation configuration
const NAVIGATION_CONFIG = {
    routes: [
        {
            id: 'dashboard',
            label: 'Dashboard',
            path: '/',
            icon: DashboardIcon,
            description: 'Main analytics dashboard',
            keywords: ['home', 'main', 'overview', 'dashboard'],
            category: 'Core'
        },
        {
            id: 'analytics',
            label: 'Analytics',
            path: '/analytics',
            icon: AnalyticsIcon,
            description: 'Detailed analytics and reports',
            keywords: ['analytics', 'reports', 'data', 'metrics'],
            category: 'Analytics'
        },
        {
            id: 'services',
            label: 'AI Services',
            path: '/services',
            icon: ServicesIcon,
            description: 'AI-powered automation services',
            keywords: ['ai', 'services', 'automation', 'ml'],
            category: 'AI',
            children: [
                {
                    id: 'content-optimizer',
                    label: 'Content Optimizer',
                    path: '/services/content-optimizer',
                    description: 'AI content enhancement',
                    keywords: ['content', 'optimize', 'ai', 'enhance']
                },
                {
                    id: 'predictive-analytics',
                    label: 'Predictive Analytics',
                    path: '/services/predictive-analytics',
                    description: 'Future predictions and trends',
                    keywords: ['predict', 'forecast', 'trends', 'future']
                },
                {
                    id: 'churn-predictor',
                    label: 'Churn Predictor',
                    path: '/services/churn-predictor',
                    description: 'Customer retention insights',
                    keywords: ['churn', 'retention', 'customers', 'risk']
                },
                {
                    id: 'security-monitoring',
                    label: 'Security Monitoring',
                    path: '/services/security-monitoring',
                    description: 'Security analysis and monitoring',
                    keywords: ['security', 'monitor', 'threats', 'analysis']
                }
            ]
        },
        {
            id: 'tables',
            label: 'Data Tables',
            path: '/tables',
            icon: TablesIcon,
            description: 'Enhanced data table showcase',
            keywords: ['tables', 'data', 'grid', 'export'],
            category: 'Tools'
        }
    ],
    quickActions: [
        {
            id: 'create-post',
            label: 'Create Post',
            icon: AddIcon,
            action: 'navigate',
            target: '/?tab=1',
            shortcut: 'Ctrl+N'
        },
        {
            id: 'export-data',
            label: 'Export Data',
            icon: DownloadIcon,
            action: 'function',
            shortcut: 'Ctrl+E'
        },
        {
            id: 'share-dashboard',
            label: 'Share Dashboard',
            icon: ShareIcon,
            action: 'function',
            shortcut: 'Ctrl+S'
        },
        {
            id: 'help-support',
            label: 'Help & Support',
            icon: HelpIcon,
            action: 'navigate',
            target: '/help'
        }
    ]
};

// Breadcrumb generation utilities
const generateBreadcrumbs = (pathname) => {
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs = [];
    
    // Always start with home
    breadcrumbs.push({
        label: 'Dashboard',
        path: '/',
        icon: DashboardIcon
    });
    
    // Build breadcrumbs from path segments
    let currentPath = '';
    segments.forEach((segment, index) => {
        currentPath += `/${segment}`;
        
        // Map segments to readable labels
        const labelMap = {
            'services': 'AI Services',
            'content-optimizer': 'Content Optimizer',
            'predictive-analytics': 'Predictive Analytics',
            'churn-predictor': 'Churn Predictor',
            'security-monitoring': 'Security Monitoring',
            'tables': 'Data Tables',
            'analytics': 'Analytics',
            'admin': 'Super Admin',
            'settings': 'Settings',
            'help': 'Help'
        };
        
        breadcrumbs.push({
            label: labelMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1),
            path: currentPath,
            icon: null
        });
    });
    
    return breadcrumbs;
};

// Breadcrumb generator
const useBreadcrumbs = () => {
    const location = useLocation();
    return useMemo(() => generateBreadcrumbs(location.pathname), [location.pathname]);
};

// Main navigation bar component
export const NavigationBar = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const navigate = useNavigate();
    const location = useLocation();
    const breadcrumbs = useBreadcrumbs();
    
    // Navigation context
    const {
        isDarkMode,
        toggleTheme,
        notifications,
        unreadCount,
        markAsRead,
        searchHistory,
        addSearchHistory
    } = useNavigation();
    
    // State management
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [searchDialogOpen, setSearchDialogOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);
    const [notificationsAnchor, setNotificationsAnchor] = useState(null);

    // Quick actions
    const [speedDialOpen, setSpeedDialOpen] = useState(false);
    const [exportDialogOpen, setExportDialogOpen] = useState(false);
    const [shareDialogOpen, setShareDialogOpen] = useState(false);
    
    // Derive recent searches from search history
    const recentSearches = useMemo(() => {
        if (!searchHistory || !Array.isArray(searchHistory)) return [];
        
        // Convert search history to search items format
        return searchHistory.slice(0, 5).map((historyItem, index) => ({
            id: `recent-${index}`,
            title: typeof historyItem === 'string' ? historyItem : historyItem.query || historyItem.title,
            path: typeof historyItem === 'string' ? `/search?q=${encodeURIComponent(historyItem)}` : historyItem.path || `/search?q=${encodeURIComponent(historyItem.query || historyItem.title)}`,
            type: 'search'
        }));
    }, [searchHistory]);
    
    // Placeholder for old search functionality (will be removed)
    const suggestions = [];

    // Handle search functionality
    const handleSearchOpen = useCallback(() => {
        setSearchDialogOpen(true);
    }, []);

    const handleSearchClose = useCallback(() => {
        setSearchDialogOpen(false);
    }, []);

    const handleSearchSelect = useCallback((item) => {
        if (item && item.path) {
            // Add to search history
            if (addSearchHistory) {
                addSearchHistory(item.title || item.path);
            }
            // Navigate to selected item
            navigate(item.path);
            // Close search dialog
            setSearchDialogOpen(false);
            setSearchQuery('');
        }
    }, [navigate, addSearchHistory]);

    // Quick action handlers
    const handleExportData = useCallback(() => {
        setExportDialogOpen(true);
    }, []);

    const handleShareDashboard = useCallback(() => {
        setShareDialogOpen(true);
    }, []);

    const handleQuickAction = useCallback((action) => {
        switch (action.id) {
            case 'export-data':
                handleExportData();
                break;
            case 'share-dashboard':
                handleShareDashboard();
                break;
            case 'create-post':
                if (action.target) {
                    navigate(action.target);
                }
                break;
            case 'help-support':
                if (action.target) {
                    navigate(action.target);
                }
                break;
            default:
                console.log(`Quick action ${action.id} not implemented`);
        }
        setSpeedDialOpen(false);
    }, [handleExportData, handleShareDashboard, navigate]);

    // Handle keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (event) => {
            // Global search shortcut (Ctrl+K or Cmd+K)
            if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                event.preventDefault();
                setSearchDialogOpen(true);
            }
            
            // Close dialogs on escape
            if (event.key === 'Escape') {
                setSearchDialogOpen(false);
                setMobileMenuOpen(false);
            }

            // Quick navigation shortcuts
            if ((event.ctrlKey || event.metaKey)) {
                switch(event.key) {
                    case '1':
                        event.preventDefault();
                        navigate('/');
                        break;
                    case '2':
                        event.preventDefault();
                        navigate('/services');
                        break;
                    case '3':
                        event.preventDefault();
                        navigate('/analytics');
                        break;
                    case '4':
                        event.preventDefault();
                        navigate('/tables');
                        break;
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [navigate]);

    return (
        <>
            <AppBar 
                position="fixed" 
                elevation={1}
                sx={{ 
                    zIndex: (theme) => theme.zIndex.drawer + 1,
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
                            onClick={() => setMobileMenuOpen(true)}
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
                        onClick={() => navigate('/')}
                    >
                        <Icon name="analytics" size="lg" sx={{ mr: 1, color: 'primary.main' }} />
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
                        <Breadcrumbs 
                            separator={<NavigateNextIcon fontSize="small" />}
                            sx={{ flexGrow: 1, ml: 2 }}
                            maxItems={3}
                        >
                            {breadcrumbs.map((crumb, index) => {
                                const isLast = index === breadcrumbs.length - 1;
                                const IconComponent = crumb.icon;
                                
                                return isLast ? (
                                    <Box 
                                        key={crumb.path}
                                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                                    >
                                        {IconComponent && <IconComponent fontSize="small" />}
                                        <Typography color="text.primary" variant="body2">
                                            {crumb.label}
                                        </Typography>
                                    </Box>
                                ) : (
                                    <Link
                                        key={crumb.path}
                                        component="button"
                                        variant="body2"
                                        onClick={() => navigate(crumb.path)}
                                        sx={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 0.5,
                                            color: 'text.secondary',
                                            textDecoration: 'none',
                                            '&:hover': { 
                                                textDecoration: 'underline',
                                                color: 'primary.main'
                                            }
                                        }}
                                    >
                                        {IconComponent && <IconComponent fontSize="small" />}
                                        {crumb.label}
                                    </Link>
                                );
                            })}
                        </Breadcrumbs>
                    )}

                    {/* Mobile title */}
                    {isMobile && (
                        <Typography variant="h6" sx={{ flexGrow: 1 }}>
                            {breadcrumbs[breadcrumbs.length - 1]?.label || 'Dashboard'}
                        </Typography>
                    )}

                    {/* Action buttons */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {/* Global search */}
                        {!isMobile && (
                            <Tooltip title="Search (Ctrl+K)">
                                <Box
                                    onClick={handleSearchOpen}
                                    sx={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 1,
                                        px: 2,
                                        py: 0.5,
                                        border: '1px solid',
                                        borderColor: 'divider',
                                        borderRadius: 1,
                                        cursor: 'pointer',
                                        minWidth: 200,
                                        '&:hover': {
                                            backgroundColor: 'action.hover'
                                        }
                                    }}
                                >
                                    <SearchIcon fontSize="small" color="action" />
                                    <Typography variant="body2" color="text.secondary">
                                        Search...
                                    </Typography>
                                    <Chip 
                                        label="⌘K" 
                                        size="small" 
                                        variant="outlined"
                                        sx={{ height: 20, fontSize: '0.7rem' }}
                                    />
                                </Box>
                            </Tooltip>
                        )}

                        {/* Mobile search */}
                        {isMobile && (
                            <IconButton
                                onClick={handleSearchOpen}
                                aria-label="Search"
                            >
                                <SearchIcon />
                            </IconButton>
                        )}

                        {/* Theme toggle */}
                        <Tooltip title={isDarkMode ? "Light Mode" : "Dark Mode"}>
                            <IconButton onClick={toggleTheme} aria-label="Toggle theme">
                                {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
                            </IconButton>
                        </Tooltip>

                        {/* Notifications */}
                        <Tooltip title="Notifications">
                            <IconButton
                                onClick={(e) => setNotificationsAnchor(e.currentTarget)}
                                aria-label={`${notifications.length} notifications`}
                            >
                                <Badge badgeContent={notifications.length} color="error">
                                    <NotificationsIcon />
                                </Badge>
                            </IconButton>
                        </Tooltip>

                        {/* Profile menu (generic avatar) */}
                        <Tooltip title="Profile & Settings">
                            <IconButton
                                onClick={(e) => setProfileMenuAnchor(e.currentTarget)}
                                sx={{ ml: 1 }}
                                aria-label="Profile menu"
                            >
                                <Avatar sx={{ width: 32, height: 32 }}>
                                    <PersonIcon />
                                </Avatar>
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Toolbar>
            </AppBar>

            {/* Mobile Navigation Drawer */}
            <Drawer
                anchor="left"
                open={mobileMenuOpen}
                onClose={() => setMobileMenuOpen(false)}
                PaperProps={{
                    sx: { width: 280 }
                }}
            >
                <Toolbar />
                <Box sx={{ p: 2 }}>
                    {/* Mobile breadcrumbs */}
                    <Breadcrumbs 
                        separator={<NavigateNextIcon fontSize="small" />}
                        sx={{ mb: 2 }}
                    >
                        {breadcrumbs.map((crumb, index) => {
                            const isLast = index === breadcrumbs.length - 1;
                            const IconComponent = crumb.icon;
                            
                            return (
                                <Box 
                                    key={crumb.path}
                                    sx={{ 
                                        display: 'flex', 
                                        alignItems: 'center', 
                                        gap: 0.5,
                                        color: isLast ? 'text.primary' : 'text.secondary'
                                    }}
                                >
                                    {IconComponent && <IconComponent fontSize="small" />}
                                    <Typography variant="body2">
                                        {crumb.label}
                                    </Typography>
                                </Box>
                            );
                        })}
                    </Breadcrumbs>

                    <Divider sx={{ my: 2 }} />

                    {/* Navigation links */}
                    <List>
                        {NAVIGATION_CONFIG.routes.map((route) => {
                            const IconComponent = route.icon;
                            const isActive = location.pathname === route.path;
                            
                            return (
                                <ListItem key={route.id} disablePadding sx={{ mb: 1 }}>
                                    <ListItemButton
                                        onClick={() => {
                                            navigate(route.path);
                                            setMobileMenuOpen(false);
                                        }}
                                        selected={isActive}
                                        sx={{ borderRadius: 1, minHeight: 48 }}
                                    >
                                        <ListItemIcon sx={{ minWidth: 40 }}>
                                            <IconComponent />
                                        </ListItemIcon>
                                        <ListItemText 
                                            primary={route.label}
                                            secondary={route.description}
                                        />
                                    </ListItemButton>
                                </ListItem>
                            );
                        })}
                    </List>
                </Box>
            </Drawer>

            {/* Search Dialog */}
            <Dialog
                open={false}
                onClose={() => {}}
                maxWidth="sm"
                fullWidth
                PaperProps={{
                    sx: { 
                        position: 'fixed',
                        top: 100,
                        m: 0,
                        borderRadius: 2
                    }
                }}
            >
                <DialogTitle sx={{ pb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <SearchIcon color="primary" />
                        <Typography variant="h6">Search & Navigation</Typography>
                        <Box sx={{ flexGrow: 1 }} />
                        <IconButton 
                            onClick={() => {}}
                            size="small"
                        >
                            <CloseIcon />
                        </IconButton>
                    </Box>
                </DialogTitle>
                <DialogContent sx={{ pt: 1 }}>
                    <Autocomplete
                        freeSolo
                        options={suggestions}
                        getOptionLabel={(option) => 
                            typeof option === 'string' ? option : option.fullPath || option.label
                        }
                        renderOption={(props, option) => (
                            <Box component="li" {...props}>
                                <ListItemIcon sx={{ minWidth: 40 }}>
                                    {option.icon ? <option.icon /> : <LaunchIcon />}
                                </ListItemIcon>
                                <ListItemText
                                    primary={option.label}
                                    secondary={option.description}
                                />
                            </Box>
                        )}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                placeholder="Search pages, actions, content..."
                                autoFocus
                                fullWidth
                                InputProps={{
                                    ...params.InputProps,
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            <SearchIcon />
                                        </InputAdornment>
                                    )
                                }}
                            />
                        )}
                        value={searchQuery}
                        onChange={(e, value) => {
                            if (typeof value === 'string') {
                                setSearchQuery(value);
                            } else if (value) {
                                handleSearchSelect(value);
                            }
                        }}
                        onInputChange={(e, value) => setSearchQuery(value)}
                    />

                    {/* Recent searches */}
                    {recentSearches.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                Recent
                            </Typography>
                            <List dense>
                                {recentSearches.map((item) => (
                                    <ListItem
                                        key={item.id}
                                        button
                                        onClick={() => handleSearchSelect(item)}
                                        sx={{ borderRadius: 1 }}
                                    >
                                        <ListItemIcon>
                                            <RecentIcon fontSize="small" />
                                        </ListItemIcon>
                                        <ListItemText primary={item.label} />
                                    </ListItem>
                                ))}
                            </List>
                        </Box>
                    )}

                    {/* Quick actions */}
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Quick Actions
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {NAVIGATION_CONFIG.quickActions.map((action) => (
                                <Chip
                                    key={action.id}
                                    icon={<action.icon />}
                                    label={action.label}
                                    onClick={() => {
                                        handleQuickAction(action);
                                        setSearchDialogOpen(false);
                                    }}
                                    variant="outlined"
                                    sx={{ mb: 1 }}
                                />
                            ))}
                        </Box>
                    </Box>
                </DialogContent>
            </Dialog>

            {/* Profile Menu */}
            <Menu
                anchorEl={profileMenuAnchor}
                open={Boolean(profileMenuAnchor)}
                onClose={() => setProfileMenuAnchor(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
                <MenuItem onClick={() => { navigate('/settings'); setProfileMenuAnchor(null); }}>
                    <ListItemIcon>
                        <PersonIcon />
                    </ListItemIcon>
                    <ListItemText>Profile</ListItemText>
                </MenuItem>
                <MenuItem onClick={() => { navigate('/settings'); setProfileMenuAnchor(null); }}>
                    <ListItemIcon>
                        <SettingsIcon />
                    </ListItemIcon>
                    <ListItemText>Settings</ListItemText>
                </MenuItem>
                <MenuItem onClick={() => { navigate('/help'); setProfileMenuAnchor(null); }}>
                    <ListItemIcon>
                        <HelpIcon />
                    </ListItemIcon>
                    <ListItemText>Help & Support</ListItemText>
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => { console.log('Logout clicked'); setProfileMenuAnchor(null); }}>
                    <ListItemIcon>
                        <LogoutIcon />
                    </ListItemIcon>
                    <ListItemText>Logout</ListItemText>
                </MenuItem>
            </Menu>

            {/* Notifications Menu */}
            <Menu
                anchorEl={notificationsAnchor}
                open={Boolean(notificationsAnchor)}
                onClose={() => setNotificationsAnchor(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                PaperProps={{ sx: { minWidth: 320, maxWidth: 400 } }}
            >
                {notifications.length === 0 ? (
                    <MenuItem disabled>
                        <ListItemText 
                            primary="No notifications"
                            secondary="You're all caught up!"
                        />
                    </MenuItem>
                ) : (
                    notifications.map((notification, index) => (
                        <MenuItem key={index}>
                            <ListItemIcon>
                                <Badge 
                                    variant="dot" 
                                    color={notification.priority || 'default'}
                                >
                                    <NotificationsIcon />
                                </Badge>
                            </ListItemIcon>
                            <ListItemText
                                primary={notification.title}
                                secondary={notification.message}
                            />
                        </MenuItem>
                    ))
                )}
            </Menu>

            {/* Quick Actions Speed Dial */}
            <SpeedDial
                ariaLabel="Quick Actions"
                sx={{ 
                    position: 'fixed', 
                    bottom: 24, 
                    right: 24,
                    display: { xs: 'flex', md: 'none' } // Mobile only
                }}
                icon={<SpeedDialIcon />}
                open={speedDialOpen}
                onOpen={() => setSpeedDialOpen(true)}
                onClose={() => setSpeedDialOpen(false)}
            >
                {NAVIGATION_CONFIG.quickActions.map((action) => (
                    <SpeedDialAction
                        key={action.id}
                        icon={<action.icon />}
                        tooltipTitle={action.label}
                        onClick={() => handleQuickAction(action)}
                    />
                ))}
            </SpeedDial>

            {/* Global Search Dialog */}
            <GlobalSearchDialog
                open={searchDialogOpen}
                onClose={handleSearchClose}
            />

            {/* Export Dialog */}
            <Dialog
                open={exportDialogOpen}
                onClose={() => setExportDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>Export Dashboard Data</DialogTitle>
                <DialogContent>
                    <Box sx={{ p: 2 }}>
                        <ExportButton 
                            channelId="dashboard"
                            dataType="analytics"
                            period="current"
                            size="large"
                            fullWidth
                            variant="contained"
                            onClose={() => setExportDialogOpen(false)}
                        />
                    </Box>
                </DialogContent>
            </Dialog>

            {/* Share Dialog */}
            <Dialog
                open={shareDialogOpen}
                onClose={() => setShareDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>Share Dashboard</DialogTitle>
                <DialogContent>
                    <Box sx={{ p: 2 }}>
                        <ShareButton 
                            channelId="dashboard"
                            dataType="analytics"
                            size="large"
                            fullWidth
                            variant="contained"
                            onClose={() => setShareDialogOpen(false)}
                        />
                    </Box>
                </DialogContent>
            </Dialog>
        </>
    );
};

export default NavigationBar;