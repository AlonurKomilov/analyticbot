import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';

export interface EmptyStateProps {
  /** Message to display in the empty state */
  message?: string;
  /** Optional secondary message/description */
  description?: string;
  /** Optional icon component to display above the message */
  icon?: React.ReactNode;
  /** Optional action button text */
  actionText?: string;
  /** Optional callback when action button is clicked */
  onAction?: () => void;
  /** Whether to use Paper wrapper (for standalone use) */
  usePaper?: boolean;
}

/**
 * EmptyState - Unified empty state component
 *
 * Displays a centered empty state message with optional icon and action button.
 * Can be used standalone with Paper wrapper or embedded in other components.
 *
 * @component
 * @example
 * ```tsx
 * // Simple usage
 * <EmptyState message="No posts available" icon={<InboxIcon />} />
 *
 * // With action button
 * <EmptyState
 *   message="No scheduled posts yet"
 *   description="Schedule a post to see it appear here!"
 *   actionText="Create Post"
 *   onAction={() => navigate('/posts/create')}
 *   usePaper
 * />
 * ```
 */
const EmptyState: React.FC<EmptyStateProps> = ({
  message = 'No data available',
  description,
  icon = null,
  actionText,
  onAction,
  usePaper = false
}) => {
  const content = (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      py={6}
      sx={usePaper ? { p: 6, textAlign: 'center' } : undefined}
    >
      {icon && (
        <Box
          mb={2}
          sx={{
            opacity: usePaper ? 0.5 : 1,
            '& > svg': {
              fontSize: usePaper ? 64 : undefined,
              color: 'text.secondary'
            }
          }}
        >
          {icon}
        </Box>
      )}
      <Typography
        variant={usePaper ? 'h6' : 'h6'}
        color="textSecondary"
        align="center"
        gutterBottom={!!description || !!actionText}
      >
        {message}
      </Typography>
      {description && (
        <Typography variant="body2" color="textSecondary" sx={{ mb: actionText ? 3 : 0 }}>
          {description}
        </Typography>
      )}
      {actionText && onAction && (
        <Button
          variant="contained"
          onClick={onAction}
          sx={{ mt: 2 }}
        >
          {actionText}
        </Button>
      )}
    </Box>
  );

  if (usePaper) {
    return (
      <Paper sx={{ bgcolor: 'background.paper' }} elevation={2}>
        {content}
      </Paper>
    );
  }

  return content;
};

export default EmptyState;
