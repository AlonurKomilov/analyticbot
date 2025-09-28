import React, { useState } from 'react';
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

/**
 * UserActions - Action menu for individual user rows
 */
export const UserActions = ({ 
    user, 
    onEdit, 
    onSuspend, 
    onReactivate, 
    onDelete, 
    onMessage 
}) => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [suspendDialog, setSuspendDialog] = useState(false);
    const [suspendReason, setSuspendReason] = useState('');
    
    const handleMenuOpen = (event) => {
        event.stopPropagation();
        setAnchorEl(event.currentTarget);
    };
    
    const handleMenuClose = () => {
        setAnchorEl(null);
    };
    
    const handleSuspend = () => {
        setSuspendDialog(true);
        handleMenuClose();
    };
    
    const handleSuspendConfirm = () => {
        onSuspend?.(user, suspendReason);
        setSuspendDialog(false);
        setSuspendReason('');
    };
    
    const handleAction = (action) => {
        handleMenuClose();
        action?.(user);
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
                onClose={() => setSuspendDialog(false)}
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
                        onChange={(e) => setSuspendReason(e.target.value)}
                        placeholder="e.g., Violation of terms of service..."
                    />
                </DialogContent>
                <DialogActions>
                    <Button 
                        onClick={() => setSuspendDialog(false)}
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