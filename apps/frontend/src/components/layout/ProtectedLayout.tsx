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
import NavigationBar from '../domains/navigation/NavigationBar/NavigationBar';

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
            <Box sx={{ pt: { xs: 7, sm: 8 } }}>
                {children}
            </Box>
        </>
    );
};

export default ProtectedLayout;
