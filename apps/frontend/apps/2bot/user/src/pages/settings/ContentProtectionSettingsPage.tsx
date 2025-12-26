/**
 * Content Protection Settings Page
 * Configure watermarking and theft detection for your content
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
import ContentProtectionDashboard from '@features/posts/components/ContentProtectionDashboard';
import { useChannelStore } from '@store';

const ContentProtectionSettingsPage: React.FC = () => {
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
                        <Typography color="text.primary">Content Protection</Typography>
                    </Breadcrumbs>
                    <Typography variant="h4" component="h1">
                        Content Protection
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Protect your digital content with watermarks and theft detection
                    </Typography>
                </Box>
            </Box>

            {/* Content Protection Dashboard */}
            <ContentProtectionDashboard channelId={channelId} lastUpdated={new Date()} />

            {/* Help Text */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="body2" color="text.secondary">
                    💡 <strong>About Content Protection:</strong> Add custom watermarks to your images and
                    scan the web for unauthorized usage of your content using advanced hash-based detection
                    across multiple platforms. This is a premium feature.
                </Typography>
            </Box>
        </Container>
    );
};

export default ContentProtectionSettingsPage;
