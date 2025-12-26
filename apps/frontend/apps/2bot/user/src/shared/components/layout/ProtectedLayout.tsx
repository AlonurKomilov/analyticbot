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
import { Box } from '@mui/material';
import NavigationBar from '@shared/components/navigation/NavigationBar';

interface ProtectedLayoutProps {
  /** Content to render inside the protected layout */
  children: React.ReactNode;
}

const ProtectedLayout: React.FC<ProtectedLayoutProps> = ({ children }) => {
    return (
        <>
            {/* Global Navigation Bar */}
            <NavigationBar />

            {/* Main Content Area with proper spacing */}
            <Box
                component="main"
                sx={{
                    pt: { xs: 7, sm: 8 },
                    // No left margin - NavigationBar uses temporary drawer (slide-out)
                    width: '100%',
                    minHeight: '100vh',
                    bgcolor: 'background.default',
                }}
            >
                {children}
            </Box>
        </>
    );
};

export default ProtectedLayout;
