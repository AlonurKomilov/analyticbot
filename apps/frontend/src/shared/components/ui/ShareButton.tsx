import React from 'react';
import UnifiedButton, { ButtonVariant, ButtonSize } from './UnifiedButton';

export interface ShareButtonProps {
  label?: string;
  onClick?: () => void;
  size?: ButtonSize;
  variant?: ButtonVariant;
  disabled?: boolean;
}

/**
 * Backwards-compatible ShareButton wrapper.
 * Previously the project had a legacy ShareButton component that was archived.
 * To avoid breaking imports we provide a small shim that uses UnifiedButton under the hood.
 */
const ShareButton: React.FC<ShareButtonProps> = ({
  label = 'Share',
  onClick,
  size = 'medium',
  variant = 'secondary',
  disabled = false
}) => {
  return (
    <UnifiedButton
      size={size}
      variant={variant}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </UnifiedButton>
  );
};

export default ShareButton;
