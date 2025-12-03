/**
 * 🛡️ Protected Layout Component
 *
 * Layout wrapper for authenticated routes that includes navigation bar
 * and proper spacing for protected content.
 *
 * @component
 * @example
 * ```tsx
 * <ProtectedLayout>
 *   <DashboardPage />
 * </ProtectedLayout>
 * ```
 */

import React from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import NavigationBar from '@shared/components/navigation/NavigationBar';

const DRAWER_WIDTH = 260; // Match DesktopSidebar width

interface ProtectedLayoutProps {
  /** Content to render inside the protected layout */
  children: React.ReactNode;
}

const ProtectedLayout: React.FC<ProtectedLayoutProps> = ({ children }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    return (
        <>
            {/* Global Navigation Bar */}
            <NavigationBar />

            {/* Main Content Area with proper spacing */}
            <Box
                sx={{
                    pt: { xs: 7, sm: 8 },
                    // Add left margin on desktop to account for sidebar
                    ml: isMobile ? 0 : `${DRAWER_WIDTH}px`,
                    transition: theme.transitions.create(['margin'], {
                        easing: theme.transitions.easing.sharp,
                        duration: theme.transitions.duration.leavingScreen,
                    }),
                }}
            >
                {children}
            </Box>
        </>
    );
};

export default ProtectedLayout;
