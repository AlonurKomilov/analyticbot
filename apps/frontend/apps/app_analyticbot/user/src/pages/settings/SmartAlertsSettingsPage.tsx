/**
 * Smart Alerts Settings Page
 * Configure and manage intelligent alerts for channel performance monitoring
 */

import React from 'react';
import {
    Box,
    Container,
    Typography,
    IconButton,
    Breadcrumbs,
    Link
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { SmartAlertsPanel } from '@features/alerts';
import { useChannelStore } from '@store';

const SmartAlertsSettingsPage: React.FC = () => {
    const navigate = useNavigate();
    const { selectedChannel } = useChannelStore();
    const channelId = selectedChannel?.id?.toString();

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Header with Back Button */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <IconButton
                    onClick={() => navigate('/settings')}
                    sx={{ mr: 2 }}
                    aria-label="Back to settings"
                >
                    <ArrowBackIcon />
                </IconButton>
                <Box>
                    <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 0.5 }}>
                        <Link
                            component={RouterLink}
                            to="/settings"
                            color="inherit"
                            underline="hover"
                        >
                            Settings
                        </Link>
                        <Typography color="text.primary">Smart Alerts</Typography>
                    </Breadcrumbs>
                    <Typography variant="h4" component="h1">
                        Smart Alerts
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Configure intelligent alerts for channel performance monitoring
                    </Typography>
                </Box>
            </Box>

            {/* Smart Alerts Panel */}
            <SmartAlertsPanel channelId={channelId} />

            {/* Help Text */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="body2" color="text.secondary">
                    💡 <strong>About Smart Alerts:</strong> Get notified about important changes in your channel's
                    performance such as unusual engagement drops, sudden growth spikes, or content quality issues.
                    Alerts are analyzed using AI to provide actionable insights.
                </Typography>
            </Box>
        </Container>
    );
};

export default SmartAlertsSettingsPage;
