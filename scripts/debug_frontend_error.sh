#!/bin/bash

echo "🔍 DEBUGGING FRONTEND REACT ERROR"
echo "================================="
echo

echo "1. 🧪 Testing Component Isolation:"
echo "----------------------------------"

# Create a backup of the current AnalyticsDashboard
cp apps/frontend/src/components/AnalyticsDashboard.jsx apps/frontend/src/components/AnalyticsDashboard.jsx.backup

echo "✅ Backup created"

# Create a simplified version without advanced analytics
cat > apps/frontend/src/components/AnalyticsDashboard.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Grid,
    Paper,
    Tabs,
    Tab,
    Card,
    CardContent,
    Chip,
    Alert
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Schedule as ScheduleIcon,
    TrendingUp as TrendingIcon
} from '@mui/icons-material';

// Simple Tab Panel Component
const TabPanel = ({ children, value, index, ...other }) => (
    <section
        role="tabpanel"
        hidden={value !== index}
        id={`analytics-tabpanel-${index}`}
        aria-labelledby={`analytics-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </section>
);

const AnalyticsDashboard = () => {
    const [activeTab, setActiveTab] = useState(0);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    📊 Analytics Dashboard - Test Mode
                </Typography>
                <Typography variant="subtitle1" align="center" color="text.secondary">
                    Testing component isolation
                </Typography>
            </Box>

            <Paper sx={{ width: '100%', mb: 3 }}>
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    aria-label="analytics dashboard tabs"
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
                        icon={<DashboardIcon />}
                        label="Overview"
                        id="analytics-tab-0"
                        aria-controls="analytics-tabpanel-0"
                    />
                    <Tab
                        icon={<TrendingIcon />}
                        label="Analytics"
                        id="analytics-tab-1"
                        aria-controls="analytics-tabpanel-1"
                    />
                    <Tab
                        icon={<ScheduleIcon />}
                        label="Recommendations"
                        id="analytics-tab-2"
                        aria-controls="analytics-tabpanel-2"
                    />
                </Tabs>
            </Paper>

            <TabPanel value={activeTab} index={0}>
                <Alert severity="success" sx={{ mb: 3 }}>
                    ✅ Basic React components are working!
                </Alert>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Component Test
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    If you can see this, the basic React app is loading correctly.
                                </Typography>
                                <Chip label="Test Mode" color="primary" sx={{ mt: 2 }} />
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Status Check
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Basic Material-UI components are rendering properly.
                                </Typography>
                                <Chip label="Working" color="success" sx={{ mt: 2 }} />
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
                <Alert severity="info">
                    Analytics components temporarily disabled for testing.
                </Alert>
            </TabPanel>

            <TabPanel value={activeTab} index={2}>
                <Alert severity="info">
                    Recommendations temporarily disabled for testing.
                </Alert>
            </TabPanel>
        </Container>
    );
};

export default AnalyticsDashboard;
EOF

echo "✅ Created simplified test component"
echo
echo "2. 🏗️ Rebuilding frontend with test component:"
echo "----------------------------------------------"
