/**
 * PostStatusBadge Component
 *
 * Displays post publication status with appropriate styling
 *
 * Created: October 25, 2025
 */

import React from 'react';
import { Chip, ChipProps, Tooltip } from '@mui/material';
import {
  CheckCircle,
  Schedule,
  Publish,
  Edit,
  Error,
  Cancel
} from '@mui/icons-material';
import { PostStatus } from '@/types/api';
import {
  getPostStatusLabel,
  getPostStatusDescription,
  getPostStatusColor
} from '@/utils/postStatus';

interface PostStatusBadgeProps {
  status: PostStatus;
  size?: 'small' | 'medium';
  variant?: 'filled' | 'outlined';
  showIcon?: boolean;
  showTooltip?: boolean;
}

/**
 * Get status icon
 */
function getStatusIcon(status: PostStatus): React.ReactElement {
  const iconProps = { sx: { fontSize: 16 } };

  switch (status) {
    case 'published':
      return React.createElement(CheckCircle, iconProps);
    case 'scheduled':
      return React.createElement(Schedule, iconProps);
    case 'publishing':
      return React.createElement(Publish, iconProps);
    case 'draft':
      return React.createElement(Edit, iconProps);
    case 'failed':
      return React.createElement(Error, iconProps);
    case 'cancelled':
      return React.createElement(Cancel, iconProps);
  }
}

/**
 * PostStatusBadge component
 *
 * @example
 * <PostStatusBadge status="published" />
 * <PostStatusBadge status="scheduled" size="small" />
 * <PostStatusBadge status="failed" showTooltip />
 */
export const PostStatusBadge: React.FC<PostStatusBadgeProps> = ({
  status,
  size = 'small',
  variant = 'filled',
  showIcon = true,
  showTooltip = false
}) => {
  const label = getPostStatusLabel(status);
  const color = getPostStatusColor(status);
  const description = getPostStatusDescription(status);
  const icon = getStatusIcon(status);

  const badge = (
    <Chip
      label={label}
      color={color as ChipProps['color']}
      size={size}
      variant={variant}
      icon={showIcon ? icon : undefined}
      sx={{
        fontWeight: 500,
        ...(variant === 'outlined' && {
          borderWidth: 1.5
        }),
        ...(status === 'publishing' && {
          animation: 'pulse 2s ease-in-out infinite',
          '@keyframes pulse': {
            '0%, 100%': { opacity: 1 },
            '50%': { opacity: 0.7 }
          }
        })
      }}
    />
  );

  if (showTooltip) {
    return (
      <Tooltip title={description} arrow>
        {badge}
      </Tooltip>
    );
  }

  return badge;
};

export default PostStatusBadge;
