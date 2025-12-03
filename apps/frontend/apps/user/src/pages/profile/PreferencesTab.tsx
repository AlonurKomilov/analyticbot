/**
 * Preferences Tab Component
 * Account preferences (placeholder for future features)
 */

import React from 'react';
import { Box, Typography, Alert } from '@mui/material';

export const PreferencesTab: React.FC = () => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
                Account Preferences
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Manage your account preferences and settings.
            </Typography>

            {/* Placeholder for future preferences */}
            <Alert severity="info">
                Additional preference settings will be available in a future update.
            </Alert>
        </Box>
    );
};
