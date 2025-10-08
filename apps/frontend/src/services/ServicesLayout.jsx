import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
    Box,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Typography,
    Chip
} from '@mui/material';
import {
    AutoFixHigh as ContentIcon,
    TrendingUp as PredictiveIcon,
    PersonRemove as ChurnIcon,
    Security as SecurityIcon,
    Dashboard as OverviewIcon
} from '@mui/icons-material';

const DRAWER_WIDTH = 280;

/**
 * Professional Services Layout
 * Provides navigation sidebar and content area for AI services
 */
const ServicesLayout = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const services = [
        {
            id: 'overview',
            name: 'Services Overview',
            path: '/services/overview',
            icon: OverviewIcon,
            status: 'active',
            description: 'All services dashboard'
        },
        {
            id: 'content-optimizer',
            name: 'Content Optimizer',
            path: '/services/content-optimizer',
            icon: ContentIcon,
            status: 'active',
            description: 'AI-powered content enhancement'
        },
        {
            id: 'predictive-analytics',
            name: 'Predictive Analytics',
            path: '/services/predictive-analytics',
            icon: PredictiveIcon,
            status: 'active',
            description: 'Future trend predictions'
        },
        {
            id: 'churn-predictor',
            name: 'Churn Predictor',
            path: '/services/churn-predictor',
            icon: ChurnIcon,
            status: 'beta',
            description: 'Customer retention insights'
        },
        {
            id: 'security-monitoring',
            name: 'Security Monitoring',
            path: '/services/security-monitoring',
            icon: SecurityIcon,
            status: 'active',
            description: 'Real-time security analysis'
        }
    ];

    const currentService = services.find(service =>
        location.pathname.includes(service.id)
    );

    const getStatusColor = (status) => {
        switch (status) {
            case 'active': return 'success';
            case 'beta': return 'warning';
            case 'maintenance': return 'error';
            default: return 'default';
        }
    };

    return (
        <Box variant="mainLayout">
            {/* Services Navigation Drawer */}
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
                        position: 'relative', // Changed from fixed to relative
                        height: 'calc(100vh - 64px)', // Account for NavigationBar height
                        overflow: 'auto'
                    }
                }}
            >
                <Box variant="drawerContent">
                    <Typography
                        variant="h6"
                        sx={{ mb: 2, fontWeight: 600, color: 'text.secondary' }}
                    >
                        AI Services
                    </Typography>

                    <List disablePadding>
                        {services.map((service) => {
                            const IconComponent = service.icon;
                            const isActive = location.pathname === service.path;

                            return (
                                <ListItem
                                    key={service.id}
                                    disablePadding
                                    variant="navigation"
                                >
                                    <ListItemButton
                                        onClick={() => navigate(service.path)}
                                        selected={isActive}
                                        variant="navigation"
                                        sx={{
                                            '&:hover': {
                                                backgroundColor: isActive ? 'primary.dark' : 'action.hover'
                                            }
                                        }}
                                    >
                                        <ListItemIcon variant="compact">
                                            <IconComponent />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={service.name}
                                            secondary={service.description}
                                            primaryTypographyProps={{
                                                fontWeight: isActive ? 600 : 400,
                                                fontSize: '0.95rem'
                                            }}
                                            secondaryTypographyProps={{
                                                fontSize: '0.8rem',
                                                sx: {
                                                    color: isActive ? 'inherit' : 'text.secondary',
                                                    opacity: isActive ? 0.8 : 1
                                                }
                                            }}
                                        />
                                        <Chip
                                            label={service.status}
                                            size="small"
                                            color={getStatusColor(service.status)}
                                            variant={isActive ? 'filled' : 'outlined'}
                                            sx={{ fontSize: '0.7rem', height: 20, '& .MuiChip-label': { px: 1 } }}
                                        />
                                    </ListItemButton>
                                </ListItem>
                            );
                        })}
                    </List>
                </Box>
            </Drawer>

            {/* Main Content Area */}
            <Box
                component="main"
                variant="mainContent"
            >
                <Outlet />
            </Box>
        </Box>
    );
};

export default ServicesLayout;
