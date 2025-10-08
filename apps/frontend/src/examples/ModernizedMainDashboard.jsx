/**
 * Example: Modernized MainDashboard with Standardized Spacing
 *
 * This demonstrates how to apply the new spacing system to replace
 * hardcoded values with semantic spacing tokens.
 */
import React, { useState, useEffect, useMemo } from 'react';
import {
    Container,
    Grid,
    Box,
    Tab,
    Tabs,
    Stack,
    Chip,
    Paper,
    Card,
    CardContent,
    Typography,
    Button,
    IconButton
} from '@mui/material';
import { Icon } from './components/common/IconSystem';
import { spacingUtils, SEMANTIC_SPACING, SPACING_SCALE } from './theme/spacingSystem';
import ModernCard, { ModernCardHeader } from './components/common/ModernCard.jsx';

// Component with standardized spacing
const ModernizedMainDashboard = () => {
    const [selectedTab, setSelectedTab] = useState(0);

    return (
        <Container
            maxWidth="xl"
            sx={{
                // Use semantic spacing for container
                ...spacingUtils.patterns.containerSpacing(),
                py: SEMANTIC_SPACING.layout.containerPadding
            }}
        >
            {/* AI Services Section with standardized spacing */}
            <ModernCard
                variant="gradient"
                sx={{
                    mb: SPACING_SCALE.xl,  // 24px standardized margin
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
            >
                <ModernCardHeader
                    title="AI-Powered Analytics Suite"
                    subtitle="Intelligent content analysis and optimization"
                    action={
                        <Chip
                            label="All Systems Active"
                            color="success"
                            size="small"
                            variant="outlined"
                            sx={{ bgcolor: 'rgba(255,255,255,0.1)' }}
                        />
                    }
                />

                <Grid container spacing={SPACING_SCALE.xl}> {/* 24px grid spacing */}
                    {/* Service Cards with consistent internal spacing */}
                    <Grid item xs={12} md={4}>
                        <ModernCard
                            variant="clean"
                            sx={{
                                height: '100%',
                                ...spacingUtils.patterns.cardPadding() // Semantic card padding
                            }}
                        >
                            <Box sx={spacingUtils.patterns.stack('md')}> {/* 12px vertical stack */}
                                <Icon name="analytics" size="large" color="primary" />
                                <Typography variant="h6">Content Intelligence</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Advanced AI analysis of post performance
                                </Typography>
                                <Button
                                    variant="outlined"
                                    size="small"
                                    sx={{ mt: SPACING_SCALE.sm }} // 8px top margin
                                >
                                    Configure
                                </Button>
                            </Box>
                        </ModernCard>
                    </Grid>

                    <Grid item xs={12} md={4}>
                        <ModernCard variant="clean" sx={{ height: '100%' }}>
                            <Box sx={spacingUtils.patterns.stack('md')}>
                                <Icon name="auto_awesome" size="large" color="secondary" />
                                <Typography variant="h6">Smart Scheduling</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    ML-powered optimal posting times
                                </Typography>
                                <Button
                                    variant="outlined"
                                    size="small"
                                    sx={{ mt: SPACING_SCALE.sm }}
                                >
                                    Setup
                                </Button>
                            </Box>
                        </ModernCard>
                    </Grid>

                    <Grid item xs={12} md={4}>
                        <ModernCard variant="clean" sx={{ height: '100%' }}>
                            <Box sx={spacingUtils.patterns.stack('md')}>
                                <Icon name="psychology" size="large" color="success" />
                                <Typography variant="h6">Audience Insights</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Deep learning audience behavior analysis
                                </Typography>
                                <Button
                                    variant="outlined"
                                    size="small"
                                    sx={{ mt: SPACING_SCALE.sm }}
                                >
                                    Explore
                                </Button>
                            </Box>
                        </ModernCard>
                    </Grid>
                </Grid>
            </ModernCard>

            {/* System Status with semantic spacing */}
            <ModernCard
                variant="elevated"
                sx={{ mb: SPACING_SCALE.xxl }} // 32px section gap
            >
                <ModernCardHeader
                    title="System Status"
                    action={
                        <Box sx={spacingUtils.patterns.row('sm')}> {/* 8px gap horizontal row */}
                            <Chip
                                label="API: Online"
                                color="success"
                                size="small"
                                variant="outlined"
                            />
                            <Chip
                                label="Database: Optimal"
                                color="success"
                                size="small"
                                variant="outlined"
                            />
                            <Chip
                                label="Analytics: Processing"
                                color="warning"
                                size="small"
                                variant="outlined"
                            />
                        </Box>
                    }
                />

                <Grid container spacing={SPACING_SCALE.lg}> {/* 16px grid spacing */}
                    <Grid item xs={12} md={6}>
                        <ModernCard
                            variant="outlined"
                            sx={{
                                height: '100%',
                                p: SEMANTIC_SPACING.ui.cardPadding // Semantic padding
                            }}
                        >
                            <Box sx={spacingUtils.patterns.stack('sm')}> {/* 8px stack */}
                                <Typography variant="subtitle1" fontWeight="medium">
                                    Performance Metrics
                                </Typography>
                                <Box sx={spacingUtils.patterns.row('lg')}> {/* 16px gap row */}
                                    <Box>
                                        <Typography variant="h4">98.5%</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Uptime
                                        </Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="h4">1,247</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Posts Analyzed
                                        </Typography>
                                    </Box>
                                </Box>
                            </Box>
                        </ModernCard>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <ModernCard
                            variant="outlined"
                            sx={{
                                height: '100%',
                                p: SEMANTIC_SPACING.ui.cardPadding
                            }}
                        >
                            <Box sx={spacingUtils.patterns.stack('sm')}>
                                <Typography variant="subtitle1" fontWeight="medium">
                                    Activity Summary
                                </Typography>
                                <Box sx={spacingUtils.patterns.row('lg')}>
                                    <Box>
                                        <Typography variant="h4">32</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Active Channels
                                        </Typography>
                                    </Box>
                                    <Box>
                                        <Typography variant="h4">156K</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Total Reach
                                        </Typography>
                                    </Box>
                                </Box>
                            </Box>
                        </ModernCard>
                    </Grid>
                </Grid>
            </ModernCard>

            {/* Tabbed Content with consistent spacing */}
            <ModernCard variant="clean" style={{ height: '100%' }}>
                <ModernCardHeader
                    title="Control Center"
                    action={
                        <Chip
                            label={`${selectedTab === 0 ? 'Dashboard' : selectedTab === 1 ? 'Create Post' : 'Analytics'} Active`}
                            color="primary"
                            size="small"
                            variant="outlined"
                        />
                    }
                />
                <Tabs
                    value={selectedTab}
                    onChange={(_, newValue) => setSelectedTab(newValue)}
                    variant="fullWidth"
                    sx={{
                        borderBottom: 1,
                        borderColor: 'divider',
                        mb: SPACING_SCALE.xl // 24px bottom margin
                    }}
                >
                    <Tab
                        label="Dashboard"
                        icon={<Icon name="dashboard" />}
                    />
                    <Tab
                        label="Create Post"
                        icon={<Icon name="create" />}
                    />
                    <Tab
                        label="Analytics"
                        icon={<Icon name="analytics" />}
                    />
                </Tabs>

                <Box variant="tabContent">
                    {selectedTab === 0 && (
                        <Box
                            variant="responsiveGrid"
                            sx={{
                                display: 'grid',
                                gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
                                gap: SPACING_SCALE.xl // 24px grid gap
                            }}
                        >
                            <Box>
                                {/* AnalyticsDashboard would be loaded here */}
                                <Typography variant="h6">Analytics Dashboard Content</Typography>
                            </Box>

                            <Stack spacing={SPACING_SCALE.xl}> {/* 24px stack spacing */}
                                <Paper
                                    sx={{
                                        p: SEMANTIC_SPACING.ui.cardPadding,
                                        borderRadius: 2
                                    }}
                                >
                                    <Typography variant="h6" sx={{ mb: SPACING_SCALE.lg }}>
                                        Scheduled Posts
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        No scheduled posts available
                                    </Typography>
                                </Paper>

                                <Paper
                                    sx={{
                                        p: SEMANTIC_SPACING.ui.cardPadding,
                                        borderRadius: 2
                                    }}
                                >
                                    <Typography variant="h6" sx={{ mb: SPACING_SCALE.lg }}>
                                        Channel Management
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Manage your connected channels
                                    </Typography>
                                </Paper>
                            </Stack>
                        </Box>
                    )}

                    {selectedTab === 1 && (
                        <Box
                            variant="responsiveGridLg"
                            sx={{
                                display: 'grid',
                                gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
                                gap: SPACING_SCALE.xxl // 32px larger gap for content creation
                            }}
                        >
                            <Box>
                                <Typography variant="h6">Post Creator</Typography>
                            </Box>
                            <Box>
                                <Stack spacing={SPACING_SCALE.xl}>
                                    <Typography variant="h6">Media & Tools</Typography>
                                </Stack>
                            </Box>
                        </Box>
                    )}

                    {selectedTab === 2 && (
                        <Box sx={{ p: SEMANTIC_SPACING.ui.cardPadding }}>
                            <Typography variant="h6">Advanced Analytics</Typography>
                        </Box>
                    )}
                </Box>
            </ModernCard>
        </Container>
    );
};

export default ModernizedMainDashboard;
