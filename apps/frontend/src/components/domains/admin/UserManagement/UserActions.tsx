import React, { useState, MouseEvent, ChangeEvent } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Divider,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Box,
    Typography
} from '@mui/material';
import {
    MoreVert as MoreVertIcon,
    Edit as EditIcon,
    Block as SuspendIcon,
    LockOpen as ReactivateIcon,
    Delete as DeleteIcon,
    Send as MessageIcon
} from '@mui/icons-material';

interface User {
    id?: string | number;
    username: string;
    status: string;
    [key: string]: any;
}

interface UserActionsProps {
    user: User;
    onEdit?: (user: User) => void;
    onSuspend?: (user: User, reason: string) => void;
    onReactivate?: (user: User) => void;
    onDelete?: (user: User) => void;
    onMessage?: (user: User) => void;
}

/**
 * UserActions - Action menu for individual user rows
 */
export const UserActions: React.FC<UserActionsProps> = ({
    user,
    onEdit,
    onSuspend,
    onReactivate,
    onDelete,
    onMessage
}) => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [suspendDialog, setSuspendDialog] = useState<boolean>(false);
    const [suspendReason, setSuspendReason] = useState<string>('');

    const handleMenuOpen = (event: MouseEvent<HTMLButtonElement>): void => {
        event.stopPropagation();
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = (): void => {
        setAnchorEl(null);
    };

    const handleSuspend = (): void => {
        setSuspendDialog(true);
        handleMenuClose();
    };

    const handleSuspendConfirm = (): void => {
        onSuspend?.(user, suspendReason);
        setSuspendDialog(false);
        setSuspendReason('');
    };

    const handleAction = (action?: (user: User) => void): void => {
        handleMenuClose();
        action?.(user);
    };

    const handleSuspendDialogClose = (): void => {
        setSuspendDialog(false);
    };

    const handleSuspendReasonChange = (e: ChangeEvent<HTMLInputElement>): void => {
        setSuspendReason(e.target.value);
    };

    return (
        <>
            <IconButton
                size="small"
                onClick={handleMenuOpen}
                aria-label={`Actions for ${user.username}`}
            >
                <MoreVertIcon />
            </IconButton>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                <MenuItem onClick={() => handleAction(onEdit)}>
                    <ListItemIcon>
                        <EditIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Edit User</ListItemText>
                </MenuItem>

                <MenuItem onClick={() => handleAction(onMessage)}>
                    <ListItemIcon>
                        <MessageIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Send Message</ListItemText>
                </MenuItem>

                <Divider />

                {user.status === 'active' ? (
                    <MenuItem onClick={handleSuspend}>
                        <ListItemIcon>
                            <SuspendIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText>Suspend User</ListItemText>
                    </MenuItem>
                ) : (
                    <MenuItem onClick={() => handleAction(onReactivate)}>
                        <ListItemIcon>
                            <ReactivateIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText>Reactivate User</ListItemText>
                    </MenuItem>
                )}

                <Divider />

                <MenuItem
                    onClick={() => handleAction(onDelete)}
                    sx={{ color: 'error.main' }}
                >
                    <ListItemIcon>
                        <DeleteIcon fontSize="small" color="error" />
                    </ListItemIcon>
                    <ListItemText>Delete User</ListItemText>
                </MenuItem>
            </Menu>

            {/* Suspend Dialog */}
            <Dialog
                open={suspendDialog}
                onClose={handleSuspendDialogClose}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    Suspend User: {user.username}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                            Please provide a reason for suspending this user account.
                        </Typography>
                    </Box>
                    <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Suspension Reason"
                        value={suspendReason}
                        onChange={handleSuspendReasonChange}
                        placeholder="e.g., Violation of terms of service..."
                    />
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={handleSuspendDialogClose}
                        color="inherit"
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSuspendConfirm}
                        color="error"
                        variant="contained"
                        disabled={!suspendReason.trim()}
                    >
                        Suspend User
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};
