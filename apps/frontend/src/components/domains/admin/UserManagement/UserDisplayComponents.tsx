import React from 'react';
import {
    Box,
    Avatar,
    Typography,
    Badge
} from '@mui/material';
import {
    Verified as VerifiedIcon
} from '@mui/icons-material';

interface User {
    profile_photo_url?: string;
    full_name?: string;
    username?: string;
    full_name_display: string;
    username_display: string;
    telegram_id: number | string;
    email?: string;
    email_verified?: boolean;
    is_premium?: boolean;
    phone?: string;
    phone_verified?: boolean;
}

interface UserAvatarProps {
    user: User;
    size?: number;
}

interface UserInfoProps {
    user: User;
}

interface UserContactProps {
    user: User;
}

/**
 * UserAvatar - Reusable user avatar component
 */
export const UserAvatar: React.FC<UserAvatarProps> = ({ user, size = 40 }) => (
    <Avatar
        src={user.profile_photo_url}
        sx={{
            width: size,
            height: size,
            bgcolor: 'primary.main',
            fontSize: size * 0.4
        }}
    >
        {user.full_name ? user.full_name.charAt(0).toUpperCase() :
         user.username ? user.username.charAt(0).toUpperCase() : '?'}
    </Avatar>
);

/**
 * UserInfo - Displays user's basic information with verification status
 */
export const UserInfo: React.FC<UserInfoProps> = ({ user }) => (
    <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Typography variant="body2" fontWeight="medium">
                {user.full_name_display}
            </Typography>
            {user.email_verified && <VerifiedIcon fontSize="small" color="success" />}
            {user.is_premium && <Badge badgeContent="PRO" color="primary" />}
        </Box>
        <Typography variant="caption" color="text.secondary" display="block">
            {user.username_display}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
            ID: {user.telegram_id}
        </Typography>
    </Box>
);

/**
 * UserContact - Displays user's contact information
 */
export const UserContact: React.FC<UserContactProps> = ({ user }) => (
    <Box>
        {user.email && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption">{user.email}</Typography>
                {user.email_verified && <VerifiedIcon fontSize="small" color="success" />}
            </Box>
        )}
        {user.phone && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="caption">{user.phone}</Typography>
                {user.phone_verified && <VerifiedIcon fontSize="small" color="success" />}
            </Box>
        )}
    </Box>
);
