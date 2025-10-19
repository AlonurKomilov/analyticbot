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

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    status: 'active' | 'suspended';
    subscription: string;
    joinedDate: string;
}

interface UserManagementTabProps {
    users: User[];
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
                                <TableCell>{user.email}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.role}
                                        size="small"
                                        color={user.role === 'admin' ? 'primary' : 'default'}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.status}
                                        size="small"
                                        color={user.status === 'active' ? 'success' : 'error'}
                                    />
                                </TableCell>
                                <TableCell>{user.subscription}</TableCell>
                                <TableCell>{user.joinedDate}</TableCell>
                                <TableCell align="right">
                                    {user.status === 'active' ? (
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            color="error"
                                            startIcon={<BlockIcon />}
                                            onClick={() => onSuspendUser(user.id)}
                                        >
                                            Suspend
                                        </Button>
                                    ) : (
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            color="success"
                                            startIcon={<CheckCircleIcon />}
                                            onClick={() => onReactivateUser(user.id)}
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
