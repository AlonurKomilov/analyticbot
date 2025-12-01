/**
 * EmptyState Component - Re-export from shared feedback
 * 
 * @deprecated Import from '@shared/components/feedback/EmptyState' instead
 */

import React from 'react';
import { Schedule } from '@mui/icons-material';
import SharedEmptyState from '@shared/components/feedback/EmptyState';
import { EmptyStateProps } from '../types';

/**
 * ScheduledPosts-specific EmptyState with Schedule icon preset
 */
const EmptyState: React.FC<EmptyStateProps> = ({
  message = "No scheduled posts yet",
  actionText,
  onAction
}) => {
  return (
    <SharedEmptyState
      message={message}
      description="Schedule a post to see it appear here!"
      icon={<Schedule sx={{ fontSize: 64, color: 'text.secondary' }} />}
      actionText={actionText}
      onAction={onAction}
      usePaper
    />
  );
};

export default EmptyState;
