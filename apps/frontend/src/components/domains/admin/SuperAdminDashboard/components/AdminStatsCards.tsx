import React from 'react';
import {
    Grid,
    Card,
    CardContent,
    Typography
} from '@mui/material';
import {
    People as PeopleIcon,
    CheckCircle as CheckCircleIcon,
    Block as BlockIcon,
    Security as SecurityIcon
} from '@mui/icons-material';
import type { AdminStats } from '@hooks/useAdminAPI';

interface AdminStatsCardsProps {
    stats: AdminStats | null;
}

/**
 * AdminStatsCards Component
 * Displays system statistics in card format
 */
const AdminStatsCards: React.FC<AdminStatsCardsProps> = ({ stats }) => {
    if (!stats) return null;

    // AdminStats has flat structure, map to expected nested structure
    const totalUsers = (stats as any).users?.total ?? stats.totalUsers ?? 0;
    const activeUsers = (stats as any).users?.active ?? stats.activeUsers ?? 0;
    const suspendedUsers = (stats as any).users?.suspended ?? 0;
    const adminLogins = (stats as any).activity?.admin_logins_24h ?? 0;

    return (
        <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                        <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                        <Typography variant="h4" color="primary">
                            {totalUsers}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Total Users
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                        <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                        <Typography variant="h4" color="success.main">
                            {activeUsers}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Active Users
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                        <BlockIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                        <Typography variant="h4" color="error.main">
                            {suspendedUsers}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Suspended Users
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                        <SecurityIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                        <Typography variant="h4" color="info.main">
                            {adminLogins}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Admin Logins (24h)
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
};

export default AdminStatsCards;
