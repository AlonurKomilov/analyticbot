/**
 * Enhanced Section Component
 * 
 * Improved visual section with:
 * - Better typography hierarchy
 * - Consistent spacing
 * - Optional descriptions and actions
 * - Visual separators and emphasis
 */

import React from 'react';
import { Box, Typography, Divider, Tooltip } from '@mui/material';
import { IconButton } from '../common/TouchTargetCompliance.jsx';
import { 
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

const EnhancedSection = ({
  title,
  subtitle,
  description,
  level = 2,
  collapsible = false,
  collapsed = false,
  onToggleCollapse,
  actions,
  info,
  emphasis = false,
  children,
  ...props
}) => {
  const getTitleVariant = (level) => {
    switch (level) {
      case 1: return 'h4';
      case 2: return 'h5';
      case 3: return 'h6';
      default: return 'h6';
    }
  };

  const getTitleColor = (level, emphasis) => {
    if (emphasis) return 'primary.main';
    return level === 1 ? 'text.primary' : 'text.primary';
  };

  return (
    <Box {...props}>
      {/* Section Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          mb: subtitle || description ? 1 : 2,
          gap: 2
        }}
      >
        {/* Title and Description */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Typography
              variant={getTitleVariant(level)}
              sx={{
                color: getTitleColor(level, emphasis),
                fontWeight: emphasis ? 700 : 600,
                lineHeight: 1.2
              }}
            >
              {title}
            </Typography>
            
            {info && (
              <Tooltip title={info}>
                <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </Tooltip>
            )}
          </Box>

          {subtitle && (
            <Typography 
              variant="subtitle1" 
              sx={{ 
                color: 'text.secondary',
                fontWeight: 500,
                mb: description ? 0.5 : 0
              }}
            >
              {subtitle}
            </Typography>
          )}

          {description && (
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'text.secondary',
                lineHeight: 1.4,
                maxWidth: '80%'
              }}
            >
              {description}
            </Typography>
          )}
        </Box>

        {/* Actions and Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
          {actions}
          
          {collapsible && (
            <IconButton
              onClick={onToggleCollapse}
              size="small"
              sx={{ 
                color: 'text.secondary',
                '&:hover': { 
                  color: 'text.primary',
                  bgcolor: 'action.hover'
                }
              }}
            >
              {collapsed ? <ExpandIcon /> : <CollapseIcon />}
            </IconButton>
          )}
        </Box>
      </Box>

      {/* Visual Separator for emphasized sections */}
      {emphasis && level <= 2 && (
        <Divider 
          sx={{ 
            mb: 3,
            borderColor: 'primary.main',
            borderWidth: 1
          }} 
        />
      )}

      {/* Section Content */}
      {!collapsed && (
        <Box
          sx={{
            pl: level > 2 ? 2 : 0,
            borderLeft: level > 2 ? '2px solid' : 'none',
            borderColor: level > 2 ? 'divider' : 'transparent'
          }}
        >
          {children}
        </Box>
      )}
    </Box>
  );
};

export default EnhancedSection;