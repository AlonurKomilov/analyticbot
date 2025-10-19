import React, { useMemo, useCallback } from 'react';
import { Container, Box, Typography, Skeleton, Stack, Alert } from '@mui/material';
import { useChannelStore, usePostStore, useUIStore } from './stores';
import { ErrorBoundary } from './utils/errors';
import { ErrorFallback } from './components/common/ErrorFallback';
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
    const { channels, loadChannels } = useChannelStore();
    const { scheduledPosts } = usePostStore();
    const { globalLoading } = useUIStore();

    // Memoize computed values
    const globalError = useMemo(() => globalLoading.error, [globalLoading.error]);
    const hasData = useMemo(() => channels.length > 0 || scheduledPosts.length > 0, [channels, scheduledPosts]);
    const isLoading = useMemo(() => globalLoading.isLoading, [globalLoading.isLoading]);

    // Memoize callbacks
    const handleRetry = useCallback(() => {
        loadChannels();
    }, [loadChannels]);

    // Load data on mount
    React.useEffect(() => {
        if (!hasData && !isLoading && !globalError) {
            loadChannels();
        }
    }, [hasData, isLoading, globalError, loadChannels]);

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

// Wrap App with ErrorBoundary
const AppWithErrorBoundary = () => (
    <ErrorBoundary fallback={(error, reset) => <ErrorFallback error={error} reset={reset} />}>
        <App />
    </ErrorBoundary>
);

export default AppWithErrorBoundary;
