import React from 'react';
import { Box, Typography } from '@mui/material';

interface EmptyStateProps {
  /** Message to display in the empty state */
  message?: string;
  /** Optional icon component to display above the message */
  icon?: React.ReactNode;
}

/**
 * EmptyState - Displays a centered empty state message with optional icon
 *
 * @component
 * @example
 * ```tsx
 * <EmptyState
 *   message="No posts available"
 *   icon={<InboxIcon />}
 * />
 * ```
 */
const EmptyState: React.FC<EmptyStateProps> = ({
  message = 'No data available',
  icon = null
}) => (
  <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={6}>
    {icon && <Box mb={2}>{icon}</Box>}
    <Typography variant="h6" color="textSecondary" align="center">
      {message}
    </Typography>
  </Box>
);

export default EmptyState;
