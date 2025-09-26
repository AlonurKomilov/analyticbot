/**
 * Typography System - Enhanced visual hierarchy and consistent typography scales
 * 
 * This module provides:
 * - Hierarchical typography components
 * - Consistent font scales and weights
 * - Content area definitions
 * - Semantic text components
 */

import React from 'react';
import { Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import { SEMANTIC_SPACING } from './spacingSystem.js';

/**
 * Typography Scale - Hierarchical heading system
 */
export const TYPOGRAPHY_SCALE = {
  // Display typography (largest, for hero sections)
  display: {
    fontSize: '3.5rem',    // 56px
    fontWeight: 300,
    lineHeight: 1.2,
    letterSpacing: '-0.02em'
  },
  
  // Primary headings
  h1: {
    fontSize: '2.5rem',    // 40px
    fontWeight: 600,
    lineHeight: 1.3,
    letterSpacing: '-0.01em'
  },
  
  // Section headings
  h2: {
    fontSize: '2rem',      // 32px
    fontWeight: 600,
    lineHeight: 1.35,
    letterSpacing: '-0.005em'
  },
  
  // Subsection headings
  h3: {
    fontSize: '1.5rem',    // 24px
    fontWeight: 600,
    lineHeight: 1.4
  },
  
  // Component headings
  h4: {
    fontSize: '1.25rem',   // 20px
    fontWeight: 600,
    lineHeight: 1.4
  },
  
  // Card/widget headings
  h5: {
    fontSize: '1.125rem',  // 18px
    fontWeight: 600,
    lineHeight: 1.4
  },
  
  // Small headings
  h6: {
    fontSize: '1rem',      // 16px
    fontWeight: 600,
    lineHeight: 1.4
  }
};

/**
 * Primary Page Title Component
 */
export const PageTitle = styled(Typography)(({ theme }) => ({
  ...TYPOGRAPHY_SCALE.h1,
  color: theme.palette.text.primary,
  marginBottom: SEMANTIC_SPACING.SECTION_SPACING,
  fontFamily: theme.typography.fontFamily
}));

/**
 * Section Header Component
 */
export const SectionHeader = styled(Typography)(({ theme }) => ({
  ...TYPOGRAPHY_SCALE.h2,
  color: theme.palette.text.primary,
  marginBottom: SEMANTIC_SPACING.COMPONENT_SPACING,
  fontFamily: theme.typography.fontFamily
}));

/**
 * Subsection Header Component
 */
export const SubsectionHeader = styled(Typography)(({ theme }) => ({
  ...TYPOGRAPHY_SCALE.h3,
  color: theme.palette.text.primary,
  marginBottom: SEMANTIC_SPACING.ELEMENT_SPACING,
  fontFamily: theme.typography.fontFamily
}));

/**
 * Card Title Component
 */
export const CardTitle = styled(Typography)(({ theme }) => ({
  ...TYPOGRAPHY_SCALE.h5,
  color: theme.palette.text.primary,
  marginBottom: SEMANTIC_SPACING.ELEMENT_SPACING,
  fontFamily: theme.typography.fontFamily
}));

/**
 * Content Area Containers
 */
export const PrimaryContentArea = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.default,
  borderRadius: SEMANTIC_SPACING.BORDER_RADIUS,
  padding: SEMANTIC_SPACING.SECTION_SPACING,
  marginBottom: SEMANTIC_SPACING.SECTION_SPACING,
  position: 'relative',
  
  // Enhanced visual separation
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '3px',
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
    borderRadius: `${SEMANTIC_SPACING.BORDER_RADIUS}px ${SEMANTIC_SPACING.BORDER_RADIUS}px 0 0`
  }
}));

export const SecondaryContentArea = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: SEMANTIC_SPACING.BORDER_RADIUS,
  padding: SEMANTIC_SPACING.COMPONENT_SPACING,
  marginBottom: SEMANTIC_SPACING.COMPONENT_SPACING
}));

/**
 * Visual Hierarchy Helper Components
 */
export const ContentDivider = styled(Box)(({ theme }) => ({
  height: '1px',
  backgroundColor: theme.palette.divider,
  margin: `${SEMANTIC_SPACING.SECTION_SPACING}px 0`,
  
  // Enhanced divider with gradient
  background: `linear-gradient(90deg, 
    transparent 0%, 
    ${theme.palette.divider} 20%, 
    ${theme.palette.divider} 80%, 
    transparent 100%
  )`
}));

export const SectionSpacer = styled(Box)(() => ({
  height: SEMANTIC_SPACING.SECTION_SPACING,
  width: '100%'
}));

/**
 * Typography Utilities
 */
export const typographyUtils = {
  // Apply consistent heading hierarchy
  applyHeadingScale: (level) => TYPOGRAPHY_SCALE[level] || TYPOGRAPHY_SCALE.h6,
  
  // Get semantic spacing for typography
  getTypographySpacing: (context) => {
    const spacingMap = {
      'title': SEMANTIC_SPACING.SECTION_SPACING,
      'heading': SEMANTIC_SPACING.COMPONENT_SPACING,
      'subheading': SEMANTIC_SPACING.ELEMENT_SPACING,
      'paragraph': SEMANTIC_SPACING.TEXT_SPACING
    };
    return spacingMap[context] || SEMANTIC_SPACING.ELEMENT_SPACING;
  },
  
  // Generate consistent text styles
  textStyles: {
    primary: {
      color: 'text.primary',
      lineHeight: 1.6
    },
    secondary: {
      color: 'text.secondary',
      lineHeight: 1.6
    },
    caption: {
      color: 'text.secondary',
      fontSize: '0.875rem',
      lineHeight: 1.4
    },
    overline: {
      color: 'text.secondary',
      fontSize: '0.75rem',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
      lineHeight: 1.2
    }
  }
};

/**
 * Content Hierarchy Components
 */
export const ContentHierarchy = {
  // Primary content blocks
  Primary: PrimaryContentArea,
  
  // Secondary content blocks  
  Secondary: SecondaryContentArea,
  
  // Typography components
  PageTitle,
  SectionHeader,
  SubsectionHeader,
  CardTitle,
  
  // Layout helpers
  Divider: ContentDivider,
  Spacer: SectionSpacer
};

export default ContentHierarchy;