/**
 * Profile Header Component
 * Displays user avatar, name and status chips
 */

import React from 'react';
import { Box, Typography, Avatar, Chip } from '@mui/material';
import {
    Person as PersonIcon,
    Badge as BadgeIcon
} from '@mui/icons-material';

interface ProfileHeaderProps {
    user: any;
}

export const ProfileHeader: React.FC<ProfileHeaderProps> = ({ user }) => {
    return (
        <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Avatar
                sx={{
                    width: 80,
                    height: 80,
                    mx: 'auto',
                    mb: 2,
                    bgcolor: 'primary.main',
                    fontSize: '2rem'
                }}
            >
                {user?.username ? user.username.charAt(0).toUpperCase() : <PersonIcon />}
            </Avatar>
            <Typography variant="h4" gutterBottom>
                {user?.full_name || user?.username || 'User Profile'}
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 2 }}>
                <Chip
                    label={user?.role || 'User'}
                    color="primary"
                    variant="outlined"
                    icon={<BadgeIcon />}
                />
                <Chip
                    label={user?.status || 'Active'}
                    color="success"
                    variant="outlined"
                />
            </Box>
        </Box>
    );
};
