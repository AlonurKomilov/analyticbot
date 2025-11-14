import React from 'react';
import {
    Box,
    Typography,
    Container,
    Paper,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Divider,
    Card,
    CardContent
} from '@mui/material';
import {
    PhoneAndroid as PhoneIcon,
    AccountCircle as AccountIcon,
    Notifications as NotificationsIcon,
    Security as SecurityIcon,
    Palette as ThemeIcon,
    Language as LanguageIcon,
    SmartToy as BotIcon,
    Timeline as MonitoringIcon,
    CloudQueue as StorageIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

/**
 * Settings Page Component
 * User preferences and account configuration
 */
const SettingsPage: React.FC = () => {
    const navigate = useNavigate();

    const settingsSections = [
        {
            title: 'Bot Setup',
            description: 'Configure your Telegram bot credentials and settings',
            icon: <BotIcon />,
            path: '/bot/setup',
            available: true
        },
        {
            title: 'Storage Channels',
            description: 'Manage Telegram channels for zero-cost file storage',
            icon: <StorageIcon />,
            path: '/settings/storage-channels',
            available: true
        },
        {
            title: 'MTProto Setup',
            description: 'Configure Telegram MTProto client for advanced features',
            icon: <PhoneIcon />,
            path: '/settings/mtproto-setup',
            available: true
        },
        {
            title: 'MTProto Monitoring',
            description: 'Monitor your MTProto session health and data collection progress',
            icon: <MonitoringIcon />,
            path: '/settings/mtproto-monitoring',
            available: true
        },
        {
            title: 'Account Settings',
            description: 'Manage your account information and preferences',
            icon: <AccountIcon />,
            path: '/profile',
            available: true
        },
        {
            title: 'Notifications',
            description: 'Configure notification preferences',
            icon: <NotificationsIcon />,
            available: false
        },
        {
            title: 'Security & Privacy',
            description: 'Manage security settings and privacy options',
            icon: <SecurityIcon />,
            available: false
        },
        {
            title: 'Theme & Appearance',
            description: 'Customize the look and feel',
            icon: <ThemeIcon />,
            available: false
        },
        {
            title: 'Language & Region',
            description: 'Set language and regional preferences',
            icon: <LanguageIcon />,
            available: false
        }
    ];

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Settings
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Configure your preferences and account settings
                </Typography>
            </Box>

            <Card>
                <CardContent>
                    <List>
                        {settingsSections.map((section, index) => (
                            <React.Fragment key={section.title}>
                                {index > 0 && <Divider />}
                                <ListItem disablePadding>
                                    <ListItemButton
                                        onClick={() => section.available && section.path && navigate(section.path)}
                                        disabled={!section.available}
                                    >
                                        <ListItemIcon>
                                            {section.icon}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Typography variant="subtitle1">
                                                        {section.title}
                                                    </Typography>
                                                    {!section.available && (
                                                        <Typography
                                                            variant="caption"
                                                            sx={{
                                                                px: 1,
                                                                py: 0.25,
                                                                bgcolor: 'action.disabledBackground',
                                                                borderRadius: 1,
                                                                fontStyle: 'italic'
                                                            }}
                                                        >
                                                            Coming Soon
                                                        </Typography>
                                                    )}
                                                </Box>
                                            }
                                            secondary={section.description}
                                        />
                                    </ListItemButton>
                                </ListItem>
                            </React.Fragment>
                        ))}
                    </List>
                </CardContent>
            </Card>

            {/* Help Text */}
            <Paper sx={{ p: 2, mt: 3, bgcolor: 'info.lighter' }}>
                <Typography variant="body2" color="text.secondary">
                    💡 <strong>Quick Start:</strong> Set up your bot credentials first in <strong>Bot Setup</strong>,
                    then optionally configure <strong>MTProto Setup</strong> for advanced features like reading
                    channel history and analyzing posts.
                </Typography>
            </Paper>
        </Container>
    );
};

export default SettingsPage;
