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

/**
 * AdminStatsCards Component
 * Displays system statistics in card format
 */
const AdminStatsCards = ({ stats }) => {
    if (!stats) return null;
    
    return (
        <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                        <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                        <Typography variant="h4" color="primary">
                            {stats.users.total}
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
                            {stats.users.active}
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
                            {stats.users.suspended}
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
                            {stats.activity.admin_logins_24h}
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