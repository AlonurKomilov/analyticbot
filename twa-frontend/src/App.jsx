import React, { useState } from 'react';
import { Container, Box, Typography, Skeleton, Stack, Tabs, Tab, Paper } from '@mui/material';
import PostCreator from './components/PostCreator';
import ScheduledPostsList from './components/ScheduledPostsList';
import MediaPreview from './components/MediaPreview';
import AddChannel from './components/AddChannel';
import EnhancedMediaUploader from './components/EnhancedMediaUploader.jsx'; // NEW for Phase 2.1
import StorageFileBrowser from './components/StorageFileBrowser.jsx'; // NEW for Phase 2.1
import AnalyticsDashboard from './components/AnalyticsDashboard.jsx'; // NEW Week 2 Analytics
import { useAppStore } from './store/appStore.js';

const AppSkeleton = () => (
    <Stack spacing={3} sx={{ mt: 2 }}>
        <Skeleton variant="rounded" width="100%" height={110} />
        <Skeleton variant="rounded" width="100%" height={280} />
        <Skeleton variant="rounded" width="100%" height={200} />
    </Stack>
);

// Tab Panel Component
const TabPanel = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`main-tabpanel-${index}`}
        aria-labelledby={`main-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

function App() {
    const { isLoading } = useAppStore();
    const [activeTab, setActiveTab] = useState(0);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <Container maxWidth="xl">
            <Box sx={{ my: 2, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Bot Dashboard - Phase 2.1
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Enhanced TWA with Analytics & AI Recommendations
                </Typography>
            </Box>

            {isLoading ? (
                <AppSkeleton />
            ) : (
                <Box>
                    {/* Main Navigation Tabs */}
                    <Paper sx={{ mb: 3 }}>
                        <Tabs
                            value={activeTab}
                            onChange={handleTabChange}
                            sx={{ borderBottom: 1, borderColor: 'divider' }}
                            variant="fullWidth"
                        >
                            <Tab label="📝 Post Management" />
                            <Tab label="📊 Analytics Dashboard" />
                        </Tabs>
                    </Paper>

                    {/* Post Management Tab */}
                    <TabPanel value={activeTab} index={0}>
                        <Container maxWidth="sm">
                            <AddChannel />
                            <EnhancedMediaUploader /> {/* NEW Enhanced uploader */}
                            <MediaPreview /> {/* Keep existing for compatibility */}
                            <PostCreator />
                            <ScheduledPostsList />
                            <StorageFileBrowser /> {/* NEW File browser */}
                        </Container>
                    </TabPanel>

                    {/* Analytics Dashboard Tab */}
                    <TabPanel value={activeTab} index={1}>
                        <AnalyticsDashboard /> {/* NEW Week 2 Analytics Dashboard */}
                    </TabPanel>
                </Box>
            )}
        </Container>
    );
}

export default App;
