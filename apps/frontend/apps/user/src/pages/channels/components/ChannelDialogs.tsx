/**
 * Channel Form Dialog Components
 *
 * Reusable form dialogs for:
 * - Creating new channels (simplified - just username, auto-fetch info)
 * - Editing existing channels
 * - Deleting channels (confirmation)
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Box,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Alert,
    CircularProgress,
    Typography,
    Chip,
    Divider,
    InputAdornment,
    IconButton,
    Skeleton
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Search as SearchIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Verified as VerifiedIcon,
    Group as GroupIcon,
    CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { Channel } from '@/types';
import { channelsApi } from '@/api/channels';

export interface ChannelFormData {
    name: string;
    description: string;
    username: string;
    telegram_id: string;
    subscriber_count?: number;
}

interface ChannelLookupResult {
    is_valid: boolean;
    telegram_id: number | null;
    username: string | null;
    title: string | null;
    subscriber_count: number | null;
    description: string | null;
    telegram_created_at: string | null;
    is_verified: boolean;
    is_scam: boolean;
    is_admin: boolean | null;
    error_message: string | null;
}

interface CreateChannelDialogProps {
    open: boolean;
    formData: ChannelFormData;
    formError: string;
    submitting: boolean;
    onClose: () => void;
    onInputChange: (field: keyof ChannelFormData) => (event: React.ChangeEvent<HTMLInputElement>) => void;
    onSubmit: () => void;
    onFormDataChange?: (data: Partial<ChannelFormData>) => void;
    onClearError?: () => void;
}

export const CreateChannelDialog: React.FC<CreateChannelDialogProps> = ({
    open,
    formData,
    formError,
    submitting,
    onClose,
    onInputChange,
    onSubmit,
    onFormDataChange,
    onClearError
}) => {
    const { t } = useTranslation('channels');
    const [lookupResult, setLookupResult] = useState<ChannelLookupResult | null>(null);
    const [isLookingUp, setIsLookingUp] = useState(false);
    const [lookupError, setLookupError] = useState<string | null>(null);

    // Reset state when dialog opens/closes
    useEffect(() => {
        if (!open) {
            setLookupResult(null);
            setIsLookingUp(false);
            setLookupError(null);
        }
    }, [open]);

    const handleLookup = useCallback(async () => {
        const username = formData.username.trim();
        if (!username) {
            setLookupError(t('dialog.lookupError'));
            return;
        }

        setIsLookingUp(true);
        setLookupError(null);
        setLookupResult(null);
        onClearError?.();  // Clear any previous form submission errors

        try {
            const result = await channelsApi.lookupChannel(username);
            setLookupResult(result);

            if (result.is_valid && result.title) {
                // Auto-populate form with fetched data
                onFormDataChange?.({
                    name: result.title,
                    description: result.description || '',
                    telegram_id: result.telegram_id ? String(result.telegram_id) : '',
                    subscriber_count: result.subscriber_count || 0
                });
            }

            if (!result.is_valid) {
                setLookupError(result.error_message || t('dialog.notFound'));
            }
        } catch (error: any) {
            setLookupError(error.message || t('errors.generic'));
        } finally {
            setIsLookingUp(false);
        }
    }, [formData.username, onFormDataChange, onClearError]);

    // Handle Enter key in username field
    const handleUsernameKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleLookup();
        }
    };

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return 'Unknown';
        try {
            return new Date(dateStr).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return 'Unknown';
        }
    };

    const formatSubscribers = (count: number | null) => {
        if (count === null) return 'Unknown';
        if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
        if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
        return count.toString();
    };

    const canSubmit = lookupResult?.is_valid && lookupResult?.is_admin && !submitting;

    return (
        <Dialog open={open} onClose={() => !submitting && onClose()} maxWidth="sm" fullWidth>
            <DialogTitle>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AddIcon />
                    {t('dialog.addTitle')}
                </Box>
            </DialogTitle>
            <DialogContent>
                {formError && (
                    <Alert severity="error" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
                        <strong>{t('dialog.error')}</strong> {formError}
                    </Alert>
                )}

                {/* Step 1: Enter Username */}
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    {t('dialog.step1')}
                </Typography>

                <TextField
                    autoFocus
                    margin="dense"
                    label={t('dialog.channelUsername')}
                    type="text"
                    fullWidth
                    variant="outlined"
                    value={formData.username}
                    onChange={onInputChange('username')}
                    onKeyDown={handleUsernameKeyDown}
                    disabled={submitting || isLookingUp}
                    required
                    placeholder={t('dialog.usernamePlaceholder')}
                    helperText={t('dialog.usernameHelp')}
                    sx={{ mb: 2 }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton
                                    onClick={handleLookup}
                                    disabled={!formData.username.trim() || isLookingUp}
                                    color="primary"
                                >
                                    {isLookingUp ? <CircularProgress size={20} /> : <SearchIcon />}
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />

                <Button
                    variant="outlined"
                    onClick={handleLookup}
                    disabled={!formData.username.trim() || isLookingUp}
                    startIcon={isLookingUp ? <CircularProgress size={16} /> : <SearchIcon />}
                    fullWidth
                    sx={{ mb: 2 }}
                >
                    {isLookingUp ? t('dialog.searching') : t('dialog.searchButton')}
                </Button>

                {lookupError && !lookupResult && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {lookupError}
                    </Alert>
                )}

                {/* Step 2: Preview Channel Info */}
                {isLookingUp && (
                    <Box sx={{ mb: 2 }}>
                        <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 1 }} />
                    </Box>
                )}

                {lookupResult && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                            {t('dialog.step2')}
                        </Typography>

                        <Box
                            sx={{
                                p: 2,
                                border: '1px solid',
                                borderColor: lookupResult.is_valid && lookupResult.is_admin
                                    ? 'success.main'
                                    : lookupResult.is_valid
                                        ? 'warning.main'
                                        : 'error.main',
                                borderRadius: 1,
                                bgcolor: lookupResult.is_valid && lookupResult.is_admin
                                    ? 'success.dark'
                                    : lookupResult.is_valid
                                        ? 'warning.dark'
                                        : 'rgba(211, 47, 47, 0.15)',
                                opacity: 0.9
                            }}
                        >
                            {lookupResult.is_valid ? (
                                <>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                            {lookupResult.title}
                                        </Typography>
                                        {lookupResult.is_verified && (
                                            <VerifiedIcon color="primary" fontSize="small" />
                                        )}
                                    </Box>

                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                        @{lookupResult.username}
                                    </Typography>

                                    {lookupResult.description && (
                                        <Typography variant="body2" sx={{ mb: 1.5, opacity: 0.9 }}>
                                            {lookupResult.description.length > 100
                                                ? lookupResult.description.substring(0, 100) + '...'
                                                : lookupResult.description}
                                        </Typography>
                                    )}

                                    <Divider sx={{ my: 1.5 }} />

                                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                        <Chip
                                            icon={<GroupIcon />}
                                            label={`${formatSubscribers(lookupResult.subscriber_count)} ${t('dialog.subscribers')}`}
                                            size="small"
                                            variant="outlined"
                                        />
                                        <Chip
                                            icon={<CalendarIcon />}
                                            label={`${t('dialog.created')} ${formatDate(lookupResult.telegram_created_at)}`}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>

                                    <Divider sx={{ my: 1.5 }} />

                                    {/* Admin Status */}
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        {lookupResult.is_admin ? (
                                            <>
                                                <CheckCircleIcon color="success" fontSize="small" />
                                                <Typography variant="body2" color="success.main">
                                                    {t('dialog.adminSuccess')}
                                                </Typography>
                                            </>
                                        ) : (
                                            <>
                                                <ErrorIcon color="error" fontSize="small" />
                                                <Typography variant="body2" color="error.main">
                                                    {t('dialog.adminError')}
                                                </Typography>
                                            </>
                                        )}
                                    </Box>

                                    {lookupResult.is_scam && (
                                        <Alert severity="warning" sx={{ mt: 1 }}>
                                            {t('dialog.scamWarning')}
                                        </Alert>
                                    )}
                                </>
                            ) : (
                                <Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                        <ErrorIcon sx={{ color: '#ff6b6b' }} />
                                        <Typography sx={{ color: '#fff', fontWeight: 600 }}>
                                            {t('dialog.notFound')}
                                        </Typography>
                                    </Box>
                                    <Typography sx={{ color: 'rgba(255,255,255,0.9)', fontSize: '0.9rem', mb: 1.5 }}>
                                        {t('dialog.notFoundMessage')} "<strong>{formData.username.replace('@', '')}</strong>"
                                    </Typography>
                                    <Typography sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.85rem' }}>
                                        <strong>{t('dialog.checkTitle')}</strong>
                                    </Typography>
                                    <Box component="ul" sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.85rem', m: 0, pl: 2.5, mt: 0.5 }}>
                                        <li>{t('dialog.checkUsername')}</li>
                                        <li>{t('dialog.checkPublic')}</li>
                                        <li>{t('dialog.checkExists')}</li>
                                    </Box>
                                    <Typography sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem', mt: 1.5, fontStyle: 'italic' }}>
                                        {t('dialog.tip')}
                                    </Typography>
                                </Box>
                            )}
                        </Box>
                    </Box>
                )}

                {/* Admin Access Help */}
                {lookupResult && lookupResult.is_valid && !lookupResult.is_admin && (
                    <Alert severity="info" sx={{ mt: 1 }}>
                        <strong>How to add bot as admin:</strong>
                        <ol style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                            <li>Open your channel in Telegram</li>
                            <li>Go to Channel Settings → Administrators</li>
                            <li>Add <strong>@YourBotUsername</strong> as administrator</li>
                            <li>Grant "Post messages" permission</li>
                            <li>Click "Search Channel" again to verify</li>
                        </ol>
                    </Alert>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={submitting}>
                    Cancel
                </Button>
                <Button
                    onClick={onSubmit}
                    variant="contained"
                    disabled={!canSubmit}
                    startIcon={submitting ? <CircularProgress size={16} /> : <AddIcon />}
                >
                    {submitting ? 'Adding...' : 'Add Channel'}
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
                    <Alert severity="error" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
                        <strong>Error:</strong> {formError}
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
