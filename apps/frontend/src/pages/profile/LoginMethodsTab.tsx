/**
 * Login Methods Tab Component
 * Manage account linking methods
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { AccountLinking } from '@features/auth/components/profile/AccountLinking';

interface LoginMethodsTabProps {
    user: any;
    onSuccess: () => void;
}

export const LoginMethodsTab: React.FC<LoginMethodsTabProps> = ({ user, onSuccess }) => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
                Login Methods
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Manage how you sign in to your account. You can have multiple login methods for convenience.
            </Typography>

            <AccountLinking
                user={user}
                onUpdate={async () => {
                    onSuccess();
                }}
            />
        </Box>
    );
};
