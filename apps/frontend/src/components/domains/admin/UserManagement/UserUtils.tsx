import React from 'react';
import {
    Box,
    Typography,
    Chip,
    Tooltip
} from '@mui/material';

// Types
interface User {
    status?: string;
    email_verified?: boolean;
    phone_verified?: boolean;
    total_channels?: number;
    total_posts?: number;
    last_active?: string;
}

type ActivityLevel = 'high' | 'medium' | 'low' | 'none';
type RiskColor = 'error' | 'warning' | 'info' | 'success';
type StatusColor = 'success' | 'warning' | 'error' | 'primary' | 'default';

interface UserActivityProps {
    user: User;
}

interface UserRiskScoreProps {
    user: User;
}

interface UserLastActiveProps {
    user: User;
}

/**
 * User utility functions
 */
export const calculateRiskScore = (user: User): number => {
    let score = 0;
    if (user.status === 'suspended') score += 50;
    if (!user.email_verified) score += 20;
    if (!user.phone_verified) score += 15;
    if ((user.total_channels ?? 0) > 50) score += 10;
    if ((user.total_posts ?? 0) > 1000) score += 5;
    return Math.min(score, 100);
};

export const getActivityLevel = (user: User): ActivityLevel => {
    const posts = user.total_posts || 0;
    const channels = user.total_channels || 0;
    const score = posts + (channels * 10);

    if (score > 500) return 'high';
    if (score > 100) return 'medium';
    if (score > 0) return 'low';
    return 'none';
};

export const getStatusColor = (status: string): StatusColor => {
    const colors: Record<string, StatusColor> = {
        'active': 'success',
        'inactive': 'warning',
        'suspended': 'error',
        'premium': 'primary'
    };
    return colors[status] || 'default';
};

export const formatDateAgo = (dateString?: string): string => {
    if (!dateString) return 'Never';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
};

export const formatDate = (dateString?: string): string => {
    if (!dateString) return 'N/A';

    try {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return 'Invalid Date';
    }
};

/**
 * UserActivity - Displays user's activity metrics
 */
export const UserActivity: React.FC<UserActivityProps> = ({ user }) => {
    const activityLevel = getActivityLevel(user);

    return (
        <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" fontWeight="medium">
                {user.total_channels || 0} / {user.total_posts || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
                Channels / Posts
            </Typography>
            <Box sx={{ mt: 0.5 }}>
                <Chip
                    label={activityLevel}
                    size="small"
                    variant="outlined"
                    color={
                        activityLevel === 'high' ? 'success' :
                        activityLevel === 'medium' ? 'warning' :
                        activityLevel === 'low' ? 'info' : 'default'
                    }
                />
            </Box>
        </Box>
    );
};

/**
 * UserRiskScore - Displays calculated risk score with visual indicator
 */
export const UserRiskScore: React.FC<UserRiskScoreProps> = ({ user }) => {
    const riskScore = calculateRiskScore(user);

    const getRiskColor = (score: number): RiskColor => {
        if (score >= 70) return 'error';
        if (score >= 40) return 'warning';
        if (score >= 20) return 'info';
        return 'success';
    };

    const getRiskLevel = (score: number): string => {
        if (score >= 70) return 'High Risk';
        if (score >= 40) return 'Medium Risk';
        if (score >= 20) return 'Low Risk';
        return 'Safe';
    };

    return (
        <Tooltip title={`Risk Score: ${riskScore}/100`}>
            <Box sx={{ textAlign: 'center' }}>
                <Typography
                    variant="h6"
                    color={`${getRiskColor(riskScore)}.main`}
                    fontWeight="bold"
                >
                    {riskScore}%
                </Typography>
                <Chip
                    label={getRiskLevel(riskScore)}
                    size="small"
                    color={getRiskColor(riskScore)}
                    variant="outlined"
                />
            </Box>
        </Tooltip>
    );
};

/**
 * UserLastActive - Displays last active information
 */
export const UserLastActive: React.FC<UserLastActiveProps> = ({ user }) => (
    <Box sx={{ textAlign: 'center' }}>
        <Typography variant="body2">
            {formatDateAgo(user.last_active)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
            {user.last_active ? formatDate(user.last_active).split(' ')[0] : 'Never'}
        </Typography>
    </Box>
);
