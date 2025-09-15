import React from 'react';
import {
    Typography,
    Grid,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Avatar,
    Divider,
    Box
} from '@mui/material';
import {
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import { formatDate } from '../utils/adminUtils';

/**
 * OverviewTab Component
 * System overview with recent activity and health status
 */
const OverviewTab = ({ auditLogs = [] }) => {
    return (
        <>
            <Typography variant="h6" gutterBottom>System Overview</Typography>
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>Recent Activity</Typography>
                            <List>
                                {auditLogs.slice(0, 5).map((log, index) => (
                                    <React.Fragment key={log.id}>
                                        <ListItem>
                                            <ListItemAvatar>
                                                <Avatar sx={{ 
                                                    bgcolor: log.success ? 'success.main' : 'error.main' 
                                                }}>
                                                    {log.success ? <CheckCircleIcon /> : <WarningIcon />}
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={`${log.admin_username} - ${log.action}`}
                                                secondary={formatDate(log.created_at)}
                                            />
                                        </ListItem>
                                        {index < 4 && <Divider />}
                                    </React.Fragment>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>System Health</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                                <Typography>Database: Operational</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                                <Typography>API Services: Healthy</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                                <Typography>Security System: Active</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </>
    );
};

export default OverviewTab;