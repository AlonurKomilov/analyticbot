/**
 * UserStatusBadge Component
 *
 * Displays user account status with appropriate styling
 *
 * Created: October 25, 2025
 */

import React from 'react';
import { Chip, ChipProps } from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Block,
  HourglassEmpty,
  Delete
} from '@mui/icons-material';
import { UserStatus } from '@/types/api';
import { getUserStatusLabel } from '@/utils/userMigration';

interface UserStatusBadgeProps {
  status: UserStatus;
  size?: 'small' | 'medium';
  variant?: 'filled' | 'outlined';
  showIcon?: boolean;
}

/**
 * Get status configuration (color, icon)
 */
function getStatusConfig(status: UserStatus): {
  color: ChipProps['color'];
  icon?: React.ReactElement;
} {
  const iconProps = { sx: { fontSize: 16 } };

  switch (status) {
    case 'active':
      return {
        color: 'success',
        icon: React.createElement(CheckCircle, iconProps)
      };

    case 'inactive':
      return {
        color: 'default',
        icon: React.createElement(Cancel, iconProps)
      };

    case 'suspended':
      return {
        color: 'error',
        icon: React.createElement(Block, iconProps)
      };

    case 'pending':
      return {
        color: 'warning',
        icon: React.createElement(HourglassEmpty, iconProps)
      };

    case 'deleted':
      return {
        color: 'error',
        icon: React.createElement(Delete, iconProps)
      };
  }
}

/**
 * UserStatusBadge component
 *
 * @example
 * <UserStatusBadge status="active" />
 * <UserStatusBadge status="suspended" size="small" />
 * <UserStatusBadge status="pending" variant="outlined" showIcon={false} />
 */
export const UserStatusBadge: React.FC<UserStatusBadgeProps> = ({
  status,
  size = 'small',
  variant = 'filled',
  showIcon = true
}) => {
  const config = getStatusConfig(status);
  const label = getUserStatusLabel(status);

  return (
    <Chip
      label={label}
      color={config.color}
      size={size}
      variant={variant}
      icon={showIcon ? config.icon : undefined}
      sx={{
        fontWeight: 500,
        ...(variant === 'outlined' && {
          borderWidth: 1.5
        })
      }}
    />
  );
};

export default UserStatusBadge;
