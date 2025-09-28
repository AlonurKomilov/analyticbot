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
  IconButton as MuiIconButton
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { DESIGN_TOKENS, getButtonProps, getCardProps, getStatusColor, createTransition, createElevation } from '../../theme/designTokens.js';

// Standardized Button Component
export const StandardButton = React.forwardRef(({ 
  size = 'medium', 
  variant = 'primary', 
  children, 
  ...props 
}, ref) => {
  const buttonProps = getButtonProps(size, variant);
  
  return (
    <MuiButton
      ref={ref}
      variant={buttonProps.variant}
      color={buttonProps.color}
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

// Standardized Card Component
export const StandardCard = React.forwardRef(({ 
  variant = 'default', 
  children, 
  interactive = false,
  ...props 
}, ref) => {
  const cardProps = getCardProps(variant);
  
  return (
    <MuiCard
      ref={ref}
      elevation={cardProps.elevation}
      sx={{
        borderRadius: cardProps.borderRadius,
        border: cardProps.border,
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

// Standardized Input Component
export const StandardInput = React.forwardRef(({ 
  size = 'medium', 
  ...props 
}, ref) => {
  const inputSize = DESIGN_TOKENS.components.input.sizes[size];
  
  return (
    <MuiTextField
      ref={ref}
      variant="outlined"
      size={size}
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

// Standardized Typography Component
export const StandardTypography = React.forwardRef(({ 
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
      ref={ref}
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

// Standardized Status Chip Component
export const StandardStatusChip = React.forwardRef(({ 
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

// Standardized Section Header Component
export const SectionHeader = React.forwardRef(({ 
  children, 
  level = 2,
  ...props 
}, ref) => {
  const variants = {
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

// Standardized Page Container
export const PageContainer = React.forwardRef(({ 
  maxWidth = 'xl',
  children,
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      style={{
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
    </div>
  );
});

// Standardized Grid Container
export const GridContainer = React.forwardRef(({ 
  gap = 'md',
  columns = { xs: 1, sm: 2, md: 3, lg: 4 },
  children,
  ...props 
}, ref) => {
  const gridGap = DESIGN_TOKENS.layout.grid.gap[gap];
  
  return (
    <div
      ref={ref}
      style={{
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
    </div>
  );
});

// Export all components
export {
  StandardButton as Button,
  StandardCard as Card,
  StandardInput as Input,
  StandardTypography as Typography,
  StandardStatusChip as StatusChip
};