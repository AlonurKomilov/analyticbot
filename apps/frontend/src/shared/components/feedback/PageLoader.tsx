/**
 * PageLoader Component
 *
 * Professional loading indicator for lazy-loaded pages
 * Provides smooth loading experience with skeleton UI
 */

import React from 'react';
import { Box, CircularProgress, LinearProgress, Typography, Skeleton, Stack } from '@mui/material';

export interface PageLoaderProps {
  /** Show minimal loader (just spinner) */
  minimal?: boolean;
  /** Custom loading message */
  message?: string;
  /** Show skeleton UI instead of spinner */
  skeleton?: boolean;
  /** Skeleton variant type */
  skeletonType?: 'dashboard' | 'form' | 'list' | 'content';
}

/**
 * Skeleton UI for dashboard pages
 */
const DashboardSkeleton: React.FC = () => (
  <Box sx={{ p: 3 }}>
    <Skeleton variant="rectangular" width="100%" height={60} sx={{ mb: 3, borderRadius: 1 }} />
    <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
      <Skeleton variant="rectangular" width="25%" height={120} sx={{ borderRadius: 1 }} />
      <Skeleton variant="rectangular" width="25%" height={120} sx={{ borderRadius: 1 }} />
      <Skeleton variant="rectangular" width="25%" height={120} sx={{ borderRadius: 1 }} />
      <Skeleton variant="rectangular" width="25%" height={120} sx={{ borderRadius: 1 }} />
    </Stack>
    <Skeleton variant="rectangular" width="100%" height={300} sx={{ mb: 2, borderRadius: 1 }} />
    <Skeleton variant="rectangular" width="100%" height={200} sx={{ borderRadius: 1 }} />
  </Box>
);

/**
 * Skeleton UI for form pages
 */
const FormSkeleton: React.FC = () => (
  <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
    <Skeleton variant="text" width="60%" height={40} sx={{ mb: 3 }} />
    <Stack spacing={2}>
      <Skeleton variant="rectangular" width="100%" height={56} sx={{ borderRadius: 1 }} />
      <Skeleton variant="rectangular" width="100%" height={56} sx={{ borderRadius: 1 }} />
      <Skeleton variant="rectangular" width="100%" height={120} sx={{ borderRadius: 1 }} />
      <Skeleton variant="rectangular" width="100%" height={56} sx={{ borderRadius: 1 }} />
      <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
        <Skeleton variant="rectangular" width="48%" height={42} sx={{ borderRadius: 1 }} />
        <Skeleton variant="rectangular" width="48%" height={42} sx={{ borderRadius: 1 }} />
      </Stack>
    </Stack>
  </Box>
);

/**
 * Skeleton UI for list pages
 */
const ListSkeleton: React.FC = () => (
  <Box sx={{ p: 3 }}>
    <Skeleton variant="text" width="40%" height={40} sx={{ mb: 3 }} />
    <Stack spacing={2}>
      {[...Array(5)].map((_, i) => (
        <Skeleton key={i} variant="rectangular" width="100%" height={80} sx={{ borderRadius: 1 }} />
      ))}
    </Stack>
  </Box>
);

/**
 * Skeleton UI for content pages
 */
const ContentSkeleton: React.FC = () => (
  <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
    <Skeleton variant="text" width="70%" height={48} sx={{ mb: 2 }} />
    <Skeleton variant="text" width="40%" height={24} sx={{ mb: 3 }} />
    <Skeleton variant="rectangular" width="100%" height={200} sx={{ mb: 3, borderRadius: 1 }} />
    <Skeleton variant="text" width="100%" height={20} sx={{ mb: 1 }} />
    <Skeleton variant="text" width="100%" height={20} sx={{ mb: 1 }} />
    <Skeleton variant="text" width="95%" height={20} sx={{ mb: 1 }} />
    <Skeleton variant="text" width="98%" height={20} sx={{ mb: 3 }} />
    <Skeleton variant="rectangular" width="100%" height={300} sx={{ borderRadius: 1 }} />
  </Box>
);

/**
 * Get skeleton component based on type
 */
const getSkeletonComponent = (type: PageLoaderProps['skeletonType']) => {
  switch (type) {
    case 'dashboard':
      return <DashboardSkeleton />;
    case 'form':
      return <FormSkeleton />;
    case 'list':
      return <ListSkeleton />;
    case 'content':
      return <ContentSkeleton />;
    default:
      return <DashboardSkeleton />;
  }
};

/**
 * PageLoader Component
 */
export const PageLoader: React.FC<PageLoaderProps> = ({
  minimal = false,
  message = 'Loading...',
  skeleton = false,
  skeletonType = 'dashboard',
}) => {
  // Show skeleton UI if requested
  if (skeleton) {
    return getSkeletonComponent(skeletonType);
  }

  // Minimal loader (just spinner)
  if (minimal) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '200px',
        }}
      >
        <CircularProgress size={40} />
      </Box>
    );
  }

  // Full-featured loader
  return (
    <Box
      sx={{
        minHeight: '400px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 2,
        p: 3,
      }}
    >
      <CircularProgress
        size={48}
        thickness={4}
        sx={{
          color: 'primary.main',
        }}
      />

      <LinearProgress
        sx={{
          width: '240px',
          borderRadius: 1,
          height: 4,
        }}
        variant="indeterminate"
      />

      <Typography
        variant="body2"
        color="text.secondary"
        sx={{
          fontWeight: 500,
          mt: 1,
        }}
      >
        {message}
      </Typography>

      <Typography
        variant="caption"
        color="text.disabled"
        sx={{
          mt: 1,
        }}
      >
        Optimizing your experience...
      </Typography>
    </Box>
  );
};

/**
 * Compact loader for inline use
 */
export const CompactLoader: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => (
  <Box
    sx={{
      display: 'flex',
      alignItems: 'center',
      gap: 1.5,
      p: 2,
    }}
  >
    <CircularProgress size={20} thickness={4} />
    <Typography variant="body2" color="text.secondary">
      {message}
    </Typography>
  </Box>
);

/**
 * Full-screen loader for initial app load
 */
export const FullScreenLoader: React.FC<{ message?: string }> = ({
  message = 'Loading application...'
}) => (
  <Box
    sx={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      gap: 2,
      bgcolor: 'background.default',
      zIndex: 9999,
    }}
  >
    <CircularProgress size={56} thickness={4} />
    <Typography variant="h6" color="text.primary" sx={{ fontWeight: 500 }}>
      {message}
    </Typography>
    <LinearProgress sx={{ width: '300px', mt: 2 }} />
  </Box>
);

export default PageLoader;
