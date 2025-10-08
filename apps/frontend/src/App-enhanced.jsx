import React, { useMemo, useCallback } from 'react';
import { Container, Box, Typography, Skeleton, Stack, Alert } from '@mui/material';
import { useAppStore } from './store/appStore.js';
import { withErrorBoundary } from './utils/errorHandler.js';
import PostCreator from './components/PostCreator';
import ScheduledPostsList from './components/ScheduledPostsList';
import MediaPreview from './components/MediaPreview';
import AddChannel from './components/AddChannel';

const AppSkeleton = React.memo(() => (
    <Stack spacing={3} sx={{ mt: 2 }}>
        <Skeleton variant="rounded" width="100%" height={110} />
        <Skeleton variant="rounded" width="100%" height={280} />
        <Skeleton variant="rounded" width="100%" height={200} />
    </Stack>
));

AppSkeleton.displayName = 'AppSkeleton';

const ErrorAlert = React.memo(({ error, onRetry }) => (
    <Alert
        severity="error"
        sx={{ mb: 2 }}
        action={
            onRetry && (
                <button onClick={onRetry} style={{
                    background: 'none',
                    border: 'none',
                    color: 'inherit',
                    cursor: 'pointer',
                    textDecoration: 'underline'
                }}>
                    Retry
                </button>
            )
        }
    >
        {error}
    </Alert>
));

ErrorAlert.displayName = 'ErrorAlert';

function App() {
    const {
        isGlobalLoading,
        getError,
        fetchData,
        channels,
        scheduledPosts
    } = useAppStore();

    // Memoize computed values
    const globalError = useMemo(() => getError('fetchData'), [getError]);
    const hasData = useMemo(() => channels.length > 0 || scheduledPosts.length > 0, [channels, scheduledPosts]);
    const isLoading = useMemo(() => isGlobalLoading(), [isGlobalLoading]);

    // Memoize callbacks
    const handleRetry = useCallback(() => {
        fetchData();
    }, [fetchData]);

    // Load data on mount
    React.useEffect(() => {
        if (!hasData && !isLoading && !globalError) {
            fetchData();
        }
    }, [hasData, isLoading, globalError, fetchData]);

    return (
        <Container maxWidth="sm">
            <Box sx={{ my: 2, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Bot Dashboard
                </Typography>
            </Box>

            {globalError && (
                <ErrorAlert error={globalError} onRetry={handleRetry} />
            )}

            {isLoading ? (
                <AppSkeleton />
            ) : (
                <Box>
                    <AddChannel />
                    <MediaPreview />
                    <PostCreator />
                    <ScheduledPostsList />
                </Box>
            )}
        </Container>
    );
}

export default withErrorBoundary(App);
