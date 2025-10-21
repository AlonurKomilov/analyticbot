import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Typography
} from '@mui/material';

/**
 * User type for suspension dialog
 */
interface SuspendUser {
    username?: string;
    full_name?: string;
}

/**
 * Props for SuspendUserDialog component
 */
interface SuspendUserDialogProps {
    /** Dialog open state */
    open: boolean;
    /** User to suspend */
    user: SuspendUser | null;
    /** Current suspension reason text */
    suspensionReason: string;
    /** Callback when reason changes */
    onReasonChange: (reason: string) => void;
    /** Callback when suspension is confirmed */
    onConfirm: () => void;
    /** Callback when dialog is cancelled */
    onCancel: () => void;
}

/**
 * SuspendUserDialog Component
 * Modal dialog for user suspension with reason input
 */
const SuspendUserDialog: React.FC<SuspendUserDialogProps> = ({
    open,
    user,
    suspensionReason,
    onReasonChange,
    onConfirm,
    onCancel
}) => {
    return (
        <Dialog open={open} onClose={onCancel}>
            <DialogTitle>Suspend User</DialogTitle>
            <DialogContent>
                <Typography gutterBottom>
                    Are you sure you want to suspend user: <strong>
                        {user?.username || user?.full_name || 'Unknown'}
                    </strong>?
                </Typography>
                <TextField
                    autoFocus
                    margin="dense"
                    label="Suspension Reason"
                    fullWidth
                    variant="outlined"
                    multiline
                    rows={3}
                    value={suspensionReason}
                    onChange={(e) => onReasonChange(e.target.value)}
                    placeholder="Please provide a detailed reason for suspension..."
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onCancel}>
                    Cancel
                </Button>
                <Button onClick={onConfirm} color="error" variant="contained">
                    Suspend User
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default SuspendUserDialog;
