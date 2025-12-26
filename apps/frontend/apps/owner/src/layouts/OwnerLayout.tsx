import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Collapse,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  People,
  FolderSpecial,
  Computer,
  Storage,
  History,
  Settings,
  Logout,
  Cloud,
  ExpandLess,
  ExpandMore,
  Dns,
  ViewInAr,
  Inventory,
  NetworkCheck,
  Language,
  Security,
  MonitorHeart,
} from '@mui/icons-material';
import { useAuth } from '@contexts/AuthContext';
import { ROUTES } from '@config/routes';

const DRAWER_WIDTH = 280;

interface NavItem {
  label: string;
  icon: React.ReactElement;
  path: string;
  children?: NavItem[];
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: <Dashboard />, path: ROUTES.DASHBOARD },
  { label: 'Users', icon: <People />, path: ROUTES.USERS },
  { label: 'Projects', icon: <FolderSpecial />, path: ROUTES.PROJECTS },
  { label: 'System', icon: <Computer />, path: ROUTES.SYSTEM },
  { label: 'System Health', icon: <MonitorHeart />, path: ROUTES.SYSTEM_HEALTH },
  { label: 'Database', icon: <Storage />, path: ROUTES.DATABASE },
  { label: 'Audit Log', icon: <History />, path: ROUTES.AUDIT },
  {
    label: 'Infrastructure',
    icon: <Cloud />,
    path: ROUTES.INFRASTRUCTURE,
    children: [
      { label: 'Overview', icon: <Cloud />, path: ROUTES.INFRASTRUCTURE },
      { label: 'Clusters', icon: <Dns />, path: ROUTES.CLUSTERS },
      { label: 'Nodes', icon: <ViewInAr />, path: ROUTES.NODES },
      { label: 'Deployments', icon: <Inventory />, path: ROUTES.DEPLOYMENTS },
      { label: 'Pods', icon: <ViewInAr />, path: ROUTES.PODS },
      { label: 'Services', icon: <NetworkCheck />, path: ROUTES.SERVICES },
      { label: 'Ingress', icon: <Language />, path: ROUTES.INGRESS },
    ],
  },
  { label: 'Settings', icon: <Settings />, path: ROUTES.SETTINGS },
];

interface OwnerLayoutProps {
  children: React.ReactNode;
}

const OwnerLayout: React.FC<OwnerLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [infraOpen, setInfraOpen] = useState(
    location.pathname.startsWith('/infrastructure')
  );

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    navigate(ROUTES.LOGIN);
  };

  const handleNavClick = (item: NavItem) => {
    if (item.children) {
      setInfraOpen(!infraOpen);
    } else {
      navigate(item.path);
      setDrawerOpen(false); // Close drawer after navigation
    }
  };

  const isActive = (path: string) => {
    if (path === ROUTES.DASHBOARD) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Security sx={{ fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h6" fontWeight={700} color="primary.main">
            Owner Panel
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Platform Control Center
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: alpha(theme.palette.primary.main, 0.2) }} />

      {/* Navigation */}
      <List sx={{ flex: 1, px: 2, py: 1 }}>
        {navItems.map((item) => (
          <React.Fragment key={item.label}>
            <ListItem disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavClick(item)}
                selected={isActive(item.path) && !item.children}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    bgcolor: alpha(theme.palette.primary.main, 0.15),
                    '&:hover': {
                      bgcolor: alpha(theme.palette.primary.main, 0.25),
                    },
                  },
                  '&:hover': {
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: isActive(item.path) ? 600 : 400,
                    color: isActive(item.path) ? 'primary.main' : 'text.primary',
                  }}
                />
                {item.children && (infraOpen ? <ExpandLess /> : <ExpandMore />)}
              </ListItemButton>
            </ListItem>
            
            {/* Infrastructure submenu */}
            {item.children && (
              <Collapse in={infraOpen} timeout="auto" unmountOnExit>
                <List component="div" disablePadding sx={{ pl: 2 }}>
                  {item.children.map((child) => (
                    <ListItem key={child.label} disablePadding sx={{ mb: 0.5 }}>
                      <ListItemButton
                        onClick={() => {
                          navigate(child.path);
                          setDrawerOpen(false);
                        }}
                        selected={location.pathname === child.path}
                        sx={{
                          borderRadius: 2,
                          py: 0.75,
                          '&.Mui-selected': {
                            bgcolor: alpha(theme.palette.primary.main, 0.15),
                          },
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            color: location.pathname === child.path
                              ? 'primary.main'
                              : 'text.secondary',
                            minWidth: 36,
                          }}
                        >
                          {child.icon}
                        </ListItemIcon>
                        <ListItemText
                          primary={child.label}
                          primaryTypographyProps={{
                            fontSize: '0.875rem',
                            fontWeight: location.pathname === child.path ? 600 : 400,
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Collapse>
            )}
          </React.Fragment>
        ))}
      </List>

      {/* User Info */}
      <Box sx={{ p: 2 }}>
        <Divider sx={{ mb: 2, borderColor: alpha(theme.palette.primary.main, 0.2) }} />
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 1.5,
            borderRadius: 2,
            bgcolor: alpha(theme.palette.primary.main, 0.1),
          }}
        >
          <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
            {user?.username?.[0]?.toUpperCase() || 'O'}
          </Avatar>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            <Typography variant="body2" fontWeight={600} noWrap>
              {user?.username || 'Owner'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              Platform Owner
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        elevation={0}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            AnalyticBot Owner Panel
          </Typography>

          <IconButton onClick={handleMenuOpen} sx={{ p: 0.5 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
              {user?.username?.[0]?.toUpperCase() || 'O'}
            </Avatar>
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => { handleMenuClose(); navigate(ROUTES.SETTINGS); }}>
              <ListItemIcon><Settings fontSize="small" /></ListItemIcon>
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer - Works on all screen sizes */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH },
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%',
          maxWidth: '100%',
          minHeight: '100vh',
          bgcolor: 'background.default',
          overflow: 'hidden',
        }}
      >
        <Toolbar />
        <Box sx={{ p: { xs: 2, sm: 3 }, overflow: 'auto', maxWidth: '100%' }}>{children}</Box>
      </Box>
    </Box>
  );
};

export default OwnerLayout;
