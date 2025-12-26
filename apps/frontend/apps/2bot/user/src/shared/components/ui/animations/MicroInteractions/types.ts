/**
 * Micro-interactions Types
 */
import { BoxProps } from '@mui/material';
import { ReactNode } from 'react';

export type HoverEffect = 'lift' | 'glow' | 'scale';
export type ButtonVariant = 'contained' | 'outlined';
export type AnimationType = 'slideIn' | 'fadeIn' | 'bounce';
export type FeedbackType = 'success' | 'error' | 'pulse';
export type ProgressType = 'linear' | 'circular';
export type SkeletonVariant = 'rectangular' | 'circular';
export type SkeletonAnimation = 'pulse' | 'wave';

export interface InteractiveCardProps extends BoxProps {
  interactive?: boolean;
  hoverEffect?: HoverEffect;
}

export interface AnimatedButtonProps extends BoxProps {
  variant?: ButtonVariant;
  disabled?: boolean;
}

export interface FloatingElementProps {
  children: ReactNode;
  duration?: number;
  delay?: number;
}

export interface StaggeredAnimationProps {
  children: ReactNode;
  animation?: AnimationType;
  delay?: number;
  duration?: number;
}

export interface SkeletonLoaderProps {
  width?: string | number;
  height?: string | number;
  variant?: SkeletonVariant;
  animation?: SkeletonAnimation;
}

export interface FeedbackAnimationProps {
  type?: FeedbackType;
  show?: boolean;
  children: ReactNode;
  duration?: number;
}

export interface AnimatedProgressProps {
  value?: number;
  type?: ProgressType;
  showValue?: boolean;
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

export interface TouchRippleProps extends BoxProps {
  children: ReactNode;
}

export interface Ripple {
  x: number;
  y: number;
  size: number;
  id: number;
}
