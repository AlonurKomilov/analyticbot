/**
 * Standardized UI Components Library
 *
 * This file provides consistent, reusable UI components that follow design tokens.
 * All components in the app should use these instead of creating custom variants.
 */

import React from 'react';
import {
  Button as MuiButton,
  Card as MuiCard,
  CardContent as MuiCardContent,
  TextField as MuiTextField,
  Typography as MuiTypography,
  Chip as MuiChip,
  Box,
  ButtonProps as MuiButtonProps,
  CardProps as MuiCardProps,
  TextFieldProps,
  TypographyProps as MuiTypographyProps,
  ChipProps as MuiChipProps,
  BoxProps
} from '@mui/material';
import { DESIGN_TOKENS, getButtonProps, getCardProps, getStatusColor, createTransition, createElevation } from '@/theme/designTokens.js';

/**
 * Type definitions
 */
interface StandardButtonProps extends Omit<MuiButtonProps, 'size' | 'variant'> {
  size?: 'small' | 'medium' | 'large';
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger' | 'success';
  children?: React.ReactNode;
}

interface StandardCardProps extends Omit<MuiCardProps, 'variant'> {
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  children?: React.ReactNode;
  interactive?: boolean;
}

interface StandardInputProps extends Omit<TextFieldProps, 'size'> {
  size?: 'small' | 'medium' | 'large';
}

interface StandardTypographyProps extends MuiTypographyProps {
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';
  weight?: 'light' | 'normal' | 'medium' | 'semibold' | 'bold';
  children?: React.ReactNode;
}

interface StandardStatusChipProps extends Omit<MuiChipProps, 'size'> {
  status?: 'info' | 'success' | 'warning' | 'error';
  label: string;
  size?: 'small' | 'medium';
}

interface SectionHeaderProps {
  children: React.ReactNode;
  level?: 1 | 2 | 3 | 4;
  [key: string]: any;
}

interface PageContainerProps extends BoxProps {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
}

interface GridColumns {
  xs: number;
  sm: number;
  md: number;
  lg: number;
}

interface GridContainerProps extends BoxProps {
  gap?: 'xs' | 'sm' | 'md';
  columns?: GridColumns;
  children: React.ReactNode;
}

// Standardized Button Component
export const StandardButton = React.forwardRef<HTMLButtonElement, StandardButtonProps>(({
  size = 'medium',
  variant = 'primary',
  children,
  ...props
}, ref) => {
  const buttonProps = getButtonProps(size, variant);

  return (
    <MuiButton
      ref={ref}
      variant={buttonProps.variant as any}
      color={buttonProps.color as any}
      sx={{
        height: buttonProps.height,
        padding: buttonProps.padding,
        fontSize: buttonProps.fontSize,
        fontWeight: DESIGN_TOKENS.typography.weights.medium,
        textTransform: 'none',
        borderRadius: '8px',
        ...createTransition('all', 'fast'),
        '&:hover': {
          transform: 'translateY(-1px)',
          ...createElevation(2)
        }
      }}
      {...props}
    >
      {children}
    </MuiButton>
  );
});

StandardButton.displayName = 'StandardButton';

// Standardized Card Component
export const StandardCard = React.forwardRef<HTMLDivElement, StandardCardProps>(({
  variant = 'default',
  children,
  interactive = false,
  ...props
}, ref) => {
  const cardProps = getCardProps(variant) as any;

  return (
    <MuiCard
      ref={ref}
      elevation={cardProps.elevation}
      sx={{
        borderRadius: cardProps.borderRadius,
        ...(cardProps.border && { border: cardProps.border }),
        cursor: interactive ? 'pointer' : 'default',
        ...createTransition('all', 'normal'),
        ...(interactive && {
          '&:hover': {
            ...createElevation(6),
            transform: 'translateY(-2px)'
          }
        })
      }}
      {...props}
    >
      <MuiCardContent sx={{ padding: cardProps.padding }}>
        {children}
      </MuiCardContent>
    </MuiCard>
  );
});

StandardCard.displayName = 'StandardCard';

// Standardized Input Component
export const StandardInput = React.forwardRef<HTMLDivElement, StandardInputProps>(({
  size = 'medium',
  ...props
}, ref) => {
  const inputSize = DESIGN_TOKENS.components.input.sizes[size];

  return (
    <MuiTextField
      ref={ref}
      variant="outlined"
      size={size as any}
      sx={{
        '& .MuiOutlinedInput-root': {
          height: inputSize.height,
          fontSize: inputSize.fontSize,
          borderRadius: '8px'
        }
      }}
      {...props}
    />
  );
});

StandardInput.displayName = 'StandardInput';

// Standardized Typography Component
export const StandardTypography = React.forwardRef<HTMLElement, StandardTypographyProps>(({
  variant = 'body1',
  size,
  weight = 'normal',
  children,
  ...props
}, ref) => {
  const fontSize = size ? DESIGN_TOKENS.typography.scale[size] : undefined;
  const fontWeight = DESIGN_TOKENS.typography.weights[weight];

  return (
    <MuiTypography
      ref={ref as any}
      variant={variant}
      sx={{
        ...(fontSize && { fontSize }),
        fontWeight,
        lineHeight: 1.5
      }}
      {...props}
    >
      {children}
    </MuiTypography>
  );
});

StandardTypography.displayName = 'StandardTypography';

// Standardized Status Chip Component
export const StandardStatusChip = React.forwardRef<HTMLDivElement, StandardStatusChipProps>(({
  status = 'info',
  label,
  size = 'medium',
  ...props
}, ref) => {
  const statusColors = getStatusColor(status);

  return (
    <MuiChip
      ref={ref}
      label={label}
      size={size}
      sx={{
        backgroundColor: statusColors.background,
        color: statusColors.main,
        border: `1px solid ${statusColors.border}`,
        fontWeight: DESIGN_TOKENS.typography.weights.medium,
        '& .MuiChip-label': {
          fontSize: size === 'small' ? DESIGN_TOKENS.typography.scale.xs : DESIGN_TOKENS.typography.scale.sm
        }
      }}
      {...props}
    />
  );
});

StandardStatusChip.displayName = 'StandardStatusChip';

// Standardized Section Header Component
export const SectionHeader = React.forwardRef<HTMLElement, SectionHeaderProps>(({
  children,
  level = 2,
  ...props
}, ref) => {
  const variants: Record<number, { variant: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'; size: StandardTypographyProps['size'] }> = {
    1: { variant: 'h1', size: '3xl' },
    2: { variant: 'h2', size: '2xl' },
    3: { variant: 'h3', size: 'xl' },
    4: { variant: 'h4', size: 'lg' }
  };

  const config = variants[level] || variants[2];

  return (
    <StandardTypography
      ref={ref}
      variant={config.variant}
      size={config.size}
      weight="semibold"
      sx={{
        mb: DESIGN_TOKENS.layout.grid.gap.sm,
        color: 'text.primary'
      }}
      {...props}
    >
      {children}
    </StandardTypography>
  );
});

SectionHeader.displayName = 'SectionHeader';

// Standardized Page Container
export const PageContainer = React.forwardRef<HTMLDivElement, PageContainerProps>(({
  maxWidth = 'xl',
  children,
  ...props
}, ref) => {
  return (
    <Box
      ref={ref}
      sx={{
        maxWidth: DESIGN_TOKENS.layout.maxWidth[maxWidth],
        margin: '0 auto',
        padding: DESIGN_TOKENS.layout.container.padding.md,
        '@media (max-width: 768px)': {
          padding: DESIGN_TOKENS.layout.container.padding.sm
        },
        '@media (max-width: 480px)': {
          padding: DESIGN_TOKENS.layout.container.padding.xs
        }
      }}
      {...props}
    >
      {children}
    </Box>
  );
});

PageContainer.displayName = 'PageContainer';

// Standardized Grid Container
export const GridContainer = React.forwardRef<HTMLDivElement, GridContainerProps>(({
  gap = 'md',
  columns = { xs: 1, sm: 2, md: 3, lg: 4 },
  children,
  ...props
}, ref) => {
  const gridGap = DESIGN_TOKENS.layout.grid.gap[gap];

  return (
    <Box
      ref={ref}
      sx={{
        display: 'grid',
        gap: `${gridGap * 8}px`,
        gridTemplateColumns: `repeat(${columns.xs}, 1fr)`,
        '@media (min-width: 600px)': {
          gridTemplateColumns: `repeat(${columns.sm}, 1fr)`
        },
        '@media (min-width: 900px)': {
          gridTemplateColumns: `repeat(${columns.md}, 1fr)`
        },
        '@media (min-width: 1200px)': {
          gridTemplateColumns: `repeat(${columns.lg}, 1fr)`
        }
      }}
      {...props}
    >
      {children}
    </Box>
  );
});

GridContainer.displayName = 'GridContainer';

// Export all components
export {
  StandardButton as Button,
  StandardCard as Card,
  StandardInput as Input,
  StandardTypography as Typography,
  StandardStatusChip as StatusChip
};
