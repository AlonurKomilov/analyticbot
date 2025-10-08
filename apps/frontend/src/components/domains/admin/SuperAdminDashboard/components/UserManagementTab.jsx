import React from 'react';
import {
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Button,
    Chip
} from '@mui/material';
import { getStatusColor } from '../utils/adminUtils';

/**
 * UserManagementTab Component
 * User management interface with suspend/reactivate functionality
 */
const UserManagementTab = ({
    users = [],
    onSuspendUser,
    onReactivateUser
}) => {
    return (
        <>
            <Typography variant="h6" gutterBottom>System Users</Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>User ID</TableCell>
                            <TableCell>Username</TableCell>
                            <TableCell>Full Name</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Subscription</TableCell>
                            <TableCell>Channels</TableCell>
                            <TableCell>Posts</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {users.map((user) => (
                            <TableRow key={user.id}>
                                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                    {user.telegram_id}
                                </TableCell>
                                <TableCell>{user.username || 'N/A'}</TableCell>
                                <TableCell>{user.full_name || 'N/A'}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.status}
                                        color={getStatusColor(user.status)}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.subscription_tier || 'free'}
                                        variant="outlined"
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>{user.total_channels}</TableCell>
                                <TableCell>{user.total_posts}</TableCell>
                                <TableCell>
                                    {user.status === 'active' ? (
                                        <Button
                                            variant="outlined"
                                            color="error"
                                            size="small"
                                            onClick={() => onSuspendUser(user)}
                                        >
                                            Suspend
                                        </Button>
                                    ) : user.status === 'suspended' ? (
                                        <Button
                                            variant="outlined"
                                            color="success"
                                            size="small"
                                            onClick={() => onReactivateUser(user.id)}
                                        >
                                            Reactivate
                                        </Button>
                                    ) : null}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
};

export default UserManagementTab;
