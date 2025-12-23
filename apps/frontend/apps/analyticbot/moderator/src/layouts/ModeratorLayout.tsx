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
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  LibraryBooks as CatalogIcon,
  Category as CategoryIcon,
  Star as FeaturedIcon,
  Report as ReportsIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { ROUTES } from '@config/routes';

const DRAWER_WIDTH = 260;

interface NavItem {
  title: string;
  path: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { title: 'Dashboard', path: ROUTES.DASHBOARD, icon: <DashboardIcon /> },
  { title: 'Channel Catalog', path: ROUTES.CATALOG, icon: <CatalogIcon /> },
  { title: 'Categories', path: ROUTES.CATEGORIES, icon: <CategoryIcon /> },
  { title: 'Featured Channels', path: ROUTES.FEATURED, icon: <FeaturedIcon /> },
  { title: 'Reports', path: ROUTES.REPORTS, icon: <ReportsIcon /> },
];

interface ModeratorLayoutProps {
  children: React.ReactNode;
}

const ModeratorLayout: React.FC<ModeratorLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

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
        <ShieldIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h6" fontWeight={700} color="primary.main">
            Moderator
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Catalog Management
          </Typography>
        </Box>
      </Box>

      {/* Navigation */}
      <List sx={{ flex: 1, py: 2 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ px: 1.5, mb: 0.5 }}>
              <ListItemButton
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  borderRadius: 2,
                  backgroundColor: isActive
                    ? alpha(theme.palette.primary.main, 0.1)
                    : 'transparent',
                  '&:hover': {
                    backgroundColor: isActive
                      ? alpha(theme.palette.primary.main, 0.15)
                      : alpha(theme.palette.primary.main, 0.05),
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive ? 'primary.main' : 'text.secondary',
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
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
            {user?.username?.[0]?.toUpperCase() || 'M'}
          </Avatar>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            <Typography variant="body2" fontWeight={600} noWrap>
              {user?.username || 'Moderator'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.role || 'moderator'}
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
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
          bgcolor: 'background.paper',
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' }, color: 'text.primary' }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ flexGrow: 1, color: 'text.primary' }}
          >
            {navItems.find((item) => item.path === location.pathname)?.title || 'Moderator Panel'}
          </Typography>
          <IconButton onClick={handleMenuOpen}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
              {user?.username?.[0]?.toUpperCase() || 'M'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
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
        sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
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
          bgcolor: 'background.default',
          minHeight: '100vh',
          pt: 8,
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default ModeratorLayout;
