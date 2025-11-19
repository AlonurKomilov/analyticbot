/**
 * Channel Form Dialog Components
 *
 * Reusable form dialogs for:
 * - Creating new channels
 * - Editing existing channels
 * - Deleting channels (confirmation)
 */

import React from 'react';
import {
    Box,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Alert,
    CircularProgress
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon
} from '@mui/icons-material';
import { Channel } from '@/types';

export interface ChannelFormData {
    name: string;
    description: string;
    username: string;
    telegram_id: string;
}

interface CreateChannelDialogProps {
    open: boolean;
    formData: ChannelFormData;
    formError: string;
    submitting: boolean;
    onClose: () => void;
    onInputChange: (field: keyof ChannelFormData) => (event: React.ChangeEvent<HTMLInputElement>) => void;
    onSubmit: () => void;
}

export const CreateChannelDialog: React.FC<CreateChannelDialogProps> = ({
    open,
    formData,
    formError,
    submitting,
    onClose,
    onInputChange,
    onSubmit
}) => {
    return (
        <Dialog open={open} onClose={() => !submitting && onClose()} maxWidth="sm" fullWidth>
            <DialogTitle>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AddIcon />
                    Add Existing Telegram Channel
                </Box>
            </DialogTitle>
            <DialogContent>
                <Alert severity="warning" sx={{ mb: 2 }}>
                    <strong>Important:</strong> This adds an existing Telegram channel to your analytics system.
                    It does NOT create a new channel on Telegram. The channel must already exist.
                </Alert>

                {formError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {formError}
                    </Alert>
                )}

                <TextField
                    autoFocus
                    margin="dense"
                    label="Channel Name"
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.name}
                    onChange={onInputChange('name')}
                    disabled={submitting}
                    required
                    helperText="Friendly name for your reference (can be different from Telegram channel name)"
                    sx={{ mb: 2 }}
                />

                <TextField
                    margin="dense"
                    label="Description"
                    type="text"
                    fullWidth
                    variant="outlined"
                    multiline
                    rows={3}
                    value={formData.description}
                    onChange={onInputChange('description')}
                    disabled={submitting}
                    placeholder="Optional notes about this channel"
                    sx={{ mb: 2 }}
                />

                <TextField
                    margin="dense"
                    label="Telegram Username"
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.username}
                    onChange={onInputChange('username')}
                    disabled={submitting}
                    required
                    helperText="Channel username (e.g., @abclegacynews)"
                    placeholder="@mychannel"
                    sx={{ mb: 2 }}
                />

                <TextField
                    margin="dense"
                    label="Telegram Channel ID (Optional)"
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.telegram_id}
                    onChange={onInputChange('telegram_id')}
                    disabled={submitting}
                    helperText="Numeric channel ID from Telegram (e.g., -1082618876654). Leave empty to auto-detect."
                    placeholder="-1001234567890"
                    sx={{ mb: 1 }}
                />

                <Alert severity="info" sx={{ mt: 1, mb: 2 }}>
                    <strong>How to get Channel ID:</strong>
                    <ol style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                        <li>Forward a message from the channel to <strong>@userinfobot</strong></li>
                        <li>The bot will show you the Channel ID (e.g., -1082618876654)</li>
                        <li>Paste it in the field above</li>
                    </ol>
                </Alert>

                <Alert severity="info" sx={{ mt: 0 }}>
                    <strong>Requirements for Analytics:</strong>
                    <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                        <li>The channel must already exist on Telegram</li>
                        <li>Your bot must be added as an administrator to the channel</li>
                        <li>This will track/monitor the channel for analytics only</li>
                    </ul>
                </Alert>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={submitting}>
                    Cancel
                </Button>
                <Button
                    onClick={onSubmit}
                    variant="contained"
                    disabled={submitting || !formData.name.trim() || !formData.username.trim()}
                >
                    {submitting ? <CircularProgress size={24} /> : 'Add Channel'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

interface EditChannelDialogProps {
    open: boolean;
    formData: ChannelFormData;
    formError: string;
    submitting: boolean;
    onClose: () => void;
    onInputChange: (field: keyof ChannelFormData) => (event: React.ChangeEvent<HTMLInputElement>) => void;
    onSubmit: () => void;
}

export const EditChannelDialog: React.FC<EditChannelDialogProps> = ({
    open,
    formData,
    formError,
    submitting,
    onClose,
    onInputChange,
    onSubmit
}) => {
    return (
        <Dialog open={open} onClose={() => !submitting && onClose()} maxWidth="sm" fullWidth>
            <DialogTitle>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <EditIcon />
                    Edit Channel
                </Box>
            </DialogTitle>
            <DialogContent>
                {formError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {formError}
                    </Alert>
                )}

                <TextField
                    autoFocus
                    margin="dense"
                    label="Channel Name"
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.name}
                    onChange={onInputChange('name')}
                    disabled={submitting}
                    required
                    sx={{ mb: 2 }}
                />

                <TextField
                    margin="dense"
                    label="Description"
                    type="text"
                    fullWidth
                    variant="outlined"
                    multiline
                    rows={3}
                    value={formData.description}
                    onChange={onInputChange('description')}
                    disabled={submitting}
                    sx={{ mb: 2 }}
                />

                <TextField
                    margin="dense"
                    label="Telegram Username"
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.username}
                    onChange={onInputChange('username')}
                    disabled={submitting}
                    required
                    placeholder="@mychannel"
                    sx={{ mb: 2 }}
                />

                <TextField
                    margin="dense"
                    label="Telegram Channel ID"
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.telegram_id}
                    onChange={onInputChange('telegram_id')}
                    disabled={submitting}
                    placeholder="-1001234567890"
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={submitting}>
                    Cancel
                </Button>
                <Button
                    onClick={onSubmit}
                    variant="contained"
                    disabled={submitting || !formData.name.trim() || !formData.username.trim()}
                >
                    {submitting ? <CircularProgress size={24} /> : 'Save Changes'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

interface DeleteChannelDialogProps {
    open: boolean;
    channel: Channel | null;
    submitting: boolean;
    onClose: () => void;
    onConfirm: () => void;
}

export const DeleteChannelDialog: React.FC<DeleteChannelDialogProps> = ({
    open,
    channel,
    submitting,
    onClose,
    onConfirm
}) => {
    return (
        <Dialog open={open} onClose={() => !submitting && onClose()} maxWidth="sm" fullWidth>
            <DialogTitle>Delete Channel?</DialogTitle>
            <DialogContent>
                <Alert severity="warning" sx={{ mb: 2 }}>
                    Are you sure you want to delete <strong>{channel?.name}</strong>?
                    This action cannot be undone. All analytics data for this channel will be permanently removed.
                </Alert>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={submitting}>
                    Cancel
                </Button>
                <Button
                    onClick={onConfirm}
                    variant="contained"
                    color="error"
                    disabled={submitting}
                >
                    {submitting ? <CircularProgress size={24} /> : 'Delete'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};
