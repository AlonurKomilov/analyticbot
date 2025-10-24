import React, { useState } from 'react';
import {
    Box,
    Container,
    Typography,
    Tabs,
    Tab,
    Paper,
    Chip,
    Alert,
    Grid,
    Card,
    CardContent
} from '@mui/material';
import {
    Image as ImageIcon,
    Search as SearchIcon,
    Shield as ShieldIcon,
    Star as StarIcon
} from '@mui/icons-material';

import WatermarkTool from './WatermarkTool';
import ContentProtectionPanel from '../protection/ContentProtectionPanel';

// Tab Panel Component
interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`content-protection-tabpanel-${index}`}
        aria-labelledby={`content-protection-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

const ContentProtectionDashboard: React.FC = () => {
    const [activeTab, setActiveTab] = useState<number>(0);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
        setActiveTab(newValue);
    };

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    🛡️ Content Protection Suite
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Protect your digital content with watermarks and theft detection
                </Typography>

                {/* Feature Badges */}
                <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
                    <Chip icon={<ShieldIcon />} label="Premium Security" color="primary" />
                    <Chip icon={<ImageIcon />} label="Image Watermarks" color="secondary" />
                    <Chip icon={<SearchIcon />} label="Theft Detection" color="info" />
                    <Chip icon={<StarIcon />} label="Enterprise Grade" color="warning" />
                </Box>
            </Box>

            {/* Feature Overview Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6}>
                    <Card sx={{ height: '100%', bgcolor: 'primary.50' }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <ImageIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                            <Typography variant="h6" gutterBottom>
                                Image Watermarking
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Add custom watermarks to your images with full control over text, position,
                                opacity, and styling to protect your visual content.
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Card sx={{ height: '100%', bgcolor: 'secondary.50' }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <SearchIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
                            <Typography variant="h6" gutterBottom>
                                Theft Detection
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Scan the web for unauthorized usage of your content using advanced
                                hash-based detection across multiple platforms.
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Premium Notice */}
            <Alert
                severity="info"
                icon={<StarIcon />}
                sx={{ mb: 3 }}
            >
                <Typography variant="body2">
                    <strong>Premium Feature:</strong> Content Protection tools are available to premium subscribers.
                    Upgrade your plan to access watermarking and theft detection capabilities.
                </Typography>
            </Alert>

            {/* Navigation Tabs */}
            <Paper sx={{ width: '100%' }}>
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    aria-label="content protection tabs"
                    variant="fullWidth"
                    sx={{
                        borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
                        '& .MuiTab-root': {
                            minHeight: 64,
                            fontSize: '1rem',
                            fontWeight: 500
                        }
                    }}
                >
                    <Tab
                        icon={<ImageIcon />}
                        label="Image Watermark"
                        id="content-protection-tab-0"
                        aria-controls="content-protection-tabpanel-0"
                    />
                    <Tab
                        icon={<SearchIcon />}
                        label="Theft Detection"
                        id="content-protection-tab-1"
                        aria-controls="content-protection-tabpanel-1"
                    />
                </Tabs>
            </Paper>

            {/* Tab Content */}
            <TabPanel value={activeTab} index={0}>
                <WatermarkTool />
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
                <ContentProtectionPanel />
            </TabPanel>

            {/* Footer Info */}
            <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                    Content Protection Suite - Secure your digital assets with enterprise-grade tools
                </Typography>
            </Box>
        </Container>
    );
};

export default ContentProtectionDashboard;
