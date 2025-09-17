/**
 * 🔄 Loading Spinner Component
 * 
 * Simple loading spinner component used across the application
 */

import React from 'react';
import { CircularProgress, Box } from '@mui/material';

const LoadingSpinner = ({ 
    size = 24, 
    color = 'primary',
    centered = false,
    sx = {}
}) => {
    const spinner = <CircularProgress size={size} color={color} sx={sx} />;

    if (centered) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    ...sx
                }}
            >
                {spinner}
            </Box>
        );
    }

    return spinner;
};

export default LoadingSpinner;