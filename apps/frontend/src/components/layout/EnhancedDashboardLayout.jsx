/**
 * Enhanced Dashboard Layout Component
 * 
 * Improved visual hierarchy with:
 * - Better spacing and card organization
 * - Primary/secondary content areas
 * - Responsive grid system
 * - Visual flow optimization
 * - Reduced cognitive load
 */

import React from 'react';
import { Box, Grid, useTheme, useMediaQuery } from '@mui/material';
import { DESIGN_TOKENS } from '../../theme/designTokens.js';

const EnhancedDashboardLayout = ({ 
  header,
  primaryContent,
  secondaryContent,
  quickActions,
  systemStatus,
  children
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        pb: 4
      }}
    >
      {/* Header Section - Full Width */}
      {header && (
        <Box
          sx={{
            mb: { xs: 3, md: 4 },
            px: { xs: 2, md: 3 },
            py: { xs: 2, md: 3 },
            bgcolor: 'background.paper',
            borderBottom: '1px solid',
            borderColor: 'divider'
          }}
        >
          {header}
        </Box>
      )}

      <Box sx={{ px: { xs: 2, md: 3 } }}>
        {/* System Status - Prominent but not overwhelming */}
        {systemStatus && (
          <Box sx={{ mb: { xs: 3, md: 4 } }}>
            {systemStatus}
          </Box>
        )}

        {/* Main Content Grid */}
        <Grid container spacing={{ xs: 3, md: 4 }}>
          {/* Primary Content Area - 60% width on desktop */}
          <Grid item xs={12} lg={8}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: { xs: 3, md: 4 }
              }}
            >
              {primaryContent}
            </Box>
          </Grid>

          {/* Secondary Content Area - 40% width on desktop */}
          {(secondaryContent || quickActions) && (
            <Grid item xs={12} lg={4}>
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: { xs: 3, md: 4 },
                  position: { lg: 'sticky' },
                  top: { lg: '24px' },
                  maxHeight: { lg: 'calc(100vh - 48px)' },
                  overflowY: { lg: 'auto' }
                }}
              >
                {/* Quick Actions - Most prominent in sidebar */}
                {quickActions && (
                  <Box
                    sx={{
                      order: { xs: 2, lg: 1 },
                      '& > *': {
                        mb: 2,
                        '&:last-child': { mb: 0 }
                      }
                    }}
                  >
                    {quickActions}
                  </Box>
                )}

                {/* Secondary Content - Less prominent */}
                {secondaryContent && (
                  <Box
                    sx={{
                      order: { xs: 1, lg: 2 },
                      '& > *': {
                        mb: 3,
                        '&:last-child': { mb: 0 }
                      }
                    }}
                  >
                    {secondaryContent}
                  </Box>
                )}
              </Box>
            </Grid>
          )}
        </Grid>

        {/* Additional Content - Full Width */}
        {children && (
          <Box sx={{ mt: { xs: 4, md: 6 } }}>
            {children}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default EnhancedDashboardLayout;