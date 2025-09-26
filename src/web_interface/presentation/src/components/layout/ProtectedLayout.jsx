/**
 * 🛡️ Protected Layout Component
 * 
 * Layout wrapper for authenticated routes that includes navigation bar
 * and proper spacing for protected content.
 */

import React from 'react';
import { Box } from '@mui/material';
import NavigationBar from '../domains/navigation/NavigationBar';

const ProtectedLayout = ({ children }) => {
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