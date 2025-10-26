/**
 * UserManagementTab Component
 *
 * Admin interface for managing users - view, suspend, and reactivate accounts.
 * Displays user information in a table with action buttons.
 */

import React from 'react';
import {
    Box,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Chip,
    Typography
} from '@mui/material';
import { Block as BlockIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import type { AdminUser } from '@/hooks/useAdminAPI';

interface UserManagementTabProps {
    users: AdminUser[];
    onSuspendUser: (userId: number) => void;
    onReactivateUser: (userId: number) => void;
}

const UserManagementTab: React.FC<UserManagementTabProps> = ({
    users,
    onSuspendUser,
    onReactivateUser
}) => {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                User Management
            </Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Username</TableCell>
                            <TableCell>Email</TableCell>
                            <TableCell>Role</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Subscription</TableCell>
                            <TableCell>Joined</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {users.map((user) => (
                            <TableRow key={user.id} hover>
                                <TableCell>{user.id}</TableCell>
                                <TableCell>
                                    <Typography variant="body2" fontWeight={600}>
                                        {user.username}
                                    </Typography>
                                </TableCell>
                                <TableCell>{user.email || 'N/A'}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.role || 'user'}
                                        size="small"
                                        color={user.role === 'admin' ? 'primary' : 'default'}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.status || 'active'}
                                        size="small"
                                        color={user.status === 'active' ? 'success' : 'error'}
                                    />
                                </TableCell>
                                <TableCell>{user.subscription || 'free'}</TableCell>
                                <TableCell>{user.joinedDate || 'N/A'}</TableCell>
                                <TableCell align="right">
                                    {user.status === 'active' ? (
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            color="error"
                                            startIcon={<BlockIcon />}
                                            onClick={() => onSuspendUser(Number(user.id))}
                                        >
                                            Suspend
                                        </Button>
                                    ) : (
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            color="success"
                                            startIcon={<CheckCircleIcon />}
                                            onClick={() => onReactivateUser(Number(user.id))}
                                        >
                                            Reactivate
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

export default UserManagementTab;
