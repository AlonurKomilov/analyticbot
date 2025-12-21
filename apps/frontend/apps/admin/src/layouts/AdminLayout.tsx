import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  useTheme,
  alpha,
  Collapse,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  LiveTv as ChannelsIcon,
  SmartToy as BotsIcon,
  Telegram as TelegramIcon,
  MonitorHeart as HealthIcon,
  History as AuditIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  AdminPanelSettings as AdminIcon,
  Speed as SpeedIcon,
  Psychology as AIIcon,
  ExpandLess,
  ExpandMore,
  AutoAwesome as AIDecisionsIcon,
  Memory as AIWorkersIcon,
  Tune as AIConfigIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { ROUTES } from '@config/routes';

const DRAWER_WIDTH = 260;

interface NavItem {
  title: string;
  path: string;
  icon: React.ReactNode;
  children?: NavItem[];
}

const navItems: NavItem[] = [
  { title: 'Dashboard', path: ROUTES.DASHBOARD, icon: <DashboardIcon /> },
  { title: 'Users', path: ROUTES.USERS, icon: <PeopleIcon /> },
  { title: 'Channels', path: ROUTES.CHANNELS, icon: <ChannelsIcon /> },
  { title: 'Bots', path: ROUTES.BOTS, icon: <BotsIcon /> },
  { title: 'MTProto', path: ROUTES.MTPROTO, icon: <TelegramIcon /> },
  { title: 'Plans', path: ROUTES.PLANS, icon: <SpeedIcon /> },
  
  // System AI Section
  { 
    title: 'System AI', 
    path: ROUTES.AI_DASHBOARD, 
    icon: <AIIcon />,
    children: [
      { title: 'Dashboard', path: ROUTES.AI_DASHBOARD, icon: <DashboardIcon /> },
      { title: 'Workers', path: ROUTES.AI_WORKERS, icon: <AIWorkersIcon /> },
      { title: 'Decisions', path: ROUTES.AI_DECISIONS, icon: <AIDecisionsIcon /> },
      { title: 'Configuration', path: ROUTES.AI_CONFIG, icon: <AIConfigIcon /> },
    ]
  },

  { title: 'System Health', path: ROUTES.SYSTEM_HEALTH, icon: <HealthIcon /> },
  { title: 'Rate Limits', path: ROUTES.SYSTEM_RATE_LIMITS, icon: <SpeedIcon /> },
  { title: 'Audit Log', path: ROUTES.SYSTEM_AUDIT, icon: <AuditIcon /> },
  { title: 'Settings', path: ROUTES.SETTINGS, icon: <SettingsIcon /> },
];

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [aiMenuOpen, setAiMenuOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
  };

  const isAIRoute = location.pathname.startsWith('/ai');

  // Auto-expand AI menu when on AI routes
  React.useEffect(() => {
    if (isAIRoute) {
      setAiMenuOpen(true);
    }
  }, [isAIRoute]);

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          p: 2,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <AdminIcon sx={{ fontSize: 32, color: theme.palette.primary.main }} />
        <Box>
          <Typography variant="h6" fontWeight={700}>
            AnalyticBot
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Admin Panel
          </Typography>
        </Box>
      </Box>

      {/* Navigation */}
      <List sx={{ flex: 1, px: 1, py: 2 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || 
            (item.children && item.children.some(child => location.pathname === child.path));
          
          // Handle items with children (like System AI)
          if (item.children) {
            return (
              <React.Fragment key={item.path}>
                <ListItem disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    onClick={() => setAiMenuOpen(!aiMenuOpen)}
                    sx={{
                      borderRadius: 2,
                      backgroundColor: isActive
                        ? alpha(theme.palette.primary.main, 0.15)
                        : 'transparent',
                      '&:hover': {
                        backgroundColor: isActive
                          ? alpha(theme.palette.primary.main, 0.2)
                          : alpha(theme.palette.primary.main, 0.08),
                      },
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        color: isActive
                          ? theme.palette.primary.main
                          : theme.palette.text.secondary,
                        minWidth: 40,
                      }}
                    >
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={item.title}
                      primaryTypographyProps={{
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? 'primary.main' : 'text.primary',
                      }}
                    />
                    {aiMenuOpen ? <ExpandLess /> : <ExpandMore />}
                  </ListItemButton>
                </ListItem>
                <Collapse in={aiMenuOpen} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {item.children.map((child) => {
                      const isChildActive = location.pathname === child.path;
                      return (
                        <ListItem key={child.path} disablePadding sx={{ mb: 0.5 }}>
                          <ListItemButton
                            onClick={() => navigate(child.path)}
                            sx={{
                              pl: 4,
                              borderRadius: 2,
                              backgroundColor: isChildActive
                                ? alpha(theme.palette.primary.main, 0.15)
                                : 'transparent',
                              '&:hover': {
                                backgroundColor: isChildActive
                                  ? alpha(theme.palette.primary.main, 0.2)
                                  : alpha(theme.palette.primary.main, 0.08),
                              },
                            }}
                          >
                            <ListItemIcon
                              sx={{
                                color: isChildActive
                                  ? theme.palette.primary.main
                                  : theme.palette.text.secondary,
                                minWidth: 40,
                              }}
                            >
                              {child.icon}
                            </ListItemIcon>
                            <ListItemText
                              primary={child.title}
                              primaryTypographyProps={{
                                fontWeight: isChildActive ? 600 : 400,
                                color: isChildActive ? 'primary.main' : 'text.primary',
                                fontSize: '0.875rem',
                              }}
                            />
                          </ListItemButton>
                        </ListItem>
                      );
                    })}
                  </List>
                </Collapse>
              </React.Fragment>
            );
          }
          
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  backgroundColor: isActive
                    ? alpha(theme.palette.primary.main, 0.15)
                    : 'transparent',
                  '&:hover': {
                    backgroundColor: isActive
                      ? alpha(theme.palette.primary.main, 0.2)
                      : alpha(theme.palette.primary.main, 0.08),
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive
                      ? theme.palette.primary.main
                      : theme.palette.text.secondary,
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.title}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? 'primary.main' : 'text.primary',
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* User Info */}
      <Box
        sx={{
          p: 2,
          borderTop: `1px solid ${theme.palette.divider}`,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
        }}
      >
        <Avatar sx={{ bgcolor: theme.palette.primary.main, width: 36, height: 36 }}>
          {user?.username?.charAt(0).toUpperCase() || 'A'}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="body2" fontWeight={600} noWrap>
            {user?.username || 'Admin'}
          </Typography>
          <Typography variant="caption" color="text.secondary" noWrap>
            {user?.email}
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
          bgcolor: 'background.paper',
          borderBottom: `1px solid ${theme.palette.divider}`,
          boxShadow: 'none',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Box sx={{ flex: 1 }} />

          <IconButton onClick={handleMenuOpen}>
            <Avatar sx={{ bgcolor: theme.palette.primary.main, width: 36, height: 36 }}>
              {user?.username?.charAt(0).toUpperCase() || 'A'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem disabled>
              <Typography variant="body2">{user?.email}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              bgcolor: 'background.paper',
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              bgcolor: 'background.paper',
              borderRight: `1px solid ${theme.palette.divider}`,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
          bgcolor: 'background.default',
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default AdminLayout;
