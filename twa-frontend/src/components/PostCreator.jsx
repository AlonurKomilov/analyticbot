import React, { useState, useCallback, useMemo } from 'react';
import {
    Box,
    TextField,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography,
    CircularProgress,
    List,
    ListItem,
    Chip,
    Alert
} from '@mui/material';
import { LocalizationProvider, DateTimePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useAppStore } from '../store/appStore';
import { useLoadingState, useFormState, useTelegramWebApp } from '../hooks';
import ButtonConstructor from './ButtonConstructor';
import MediaPreview from "./MediaPreview.jsx";

// Form validation
const validatePostForm = (values) => {
    const errors = {};
    
    if (!values.text?.trim() && !values.hasMedia) {
        errors.text = 'Post text or media is required';
    }
    
    if (!values.selectedChannel) {
        errors.selectedChannel = 'Channel selection is required';
    }
    
    if (!values.scheduleTime) {
        errors.scheduleTime = 'Schedule time is required';
    } else if (new Date(values.scheduleTime) <= new Date()) {
        errors.scheduleTime = 'Schedule time must be in the future';
    }
    
    return errors;
};

const PostCreator = React.memo(() => {
    const {
        channels,
        schedulePost,
        pendingMedia,
        clearPendingMedia,
    } = useAppStore();

    const { hapticFeedback } = useTelegramWebApp();
    const { loading, error } = useLoadingState('schedulePost');

    const [buttons, setButtons] = useState([]);

    // Enhanced form state management
    const {
        state: formState,
        errors: formErrors,
        updateField,
        validateForm,
        resetForm,
        isValid
    } = useFormState({
        text: '',
        selectedChannel: '',
        scheduleTime: null,
        hasMedia: false
    }, validatePostForm);

    // Update hasMedia when pendingMedia changes
    React.useEffect(() => {
        updateField('hasMedia', !!pendingMedia.file_id);
    }, [pendingMedia.file_id, updateField]);

    // Memoized channel options
    const channelOptions = useMemo(() => 
        channels.map((channel) => ({
            value: channel.id,
            label: `${channel.title} (@${channel.username})`
        })), [channels]
    );

    // Optimized button handlers
    const handleAddButton = useCallback((newButton) => {
        setButtons(prevButtons => [...prevButtons, newButton]);
        hapticFeedback('light');
    }, [hapticFeedback]);

    const handleRemoveButton = useCallback((index) => {
        setButtons(buttons.filter((_, i) => i !== index));
        hapticFeedback('light');
    }, [buttons, hapticFeedback]);

    const handleSchedulePost = useCallback(async () => {
        if (!validateForm()) return;

        try {
            hapticFeedback('medium');
            
            const inline_buttons = buttons.length > 0 
                ? { inline_keyboard: [buttons] } 
                : null;

            await schedulePost({
                text: formState.text,
                channel_id: formState.selectedChannel,
                schedule_time: formState.scheduleTime.toISOString(),
                media_file_id: pendingMedia.file_id,
                media_type: pendingMedia.file_type,
                inline_buttons
            });

            // Reset form on success
            resetForm();
            setButtons([]);
            clearPendingMedia();
            
            hapticFeedback('success');
        } catch (err) {
            hapticFeedback('error');
        }
    }, [
        validateForm, hapticFeedback, buttons, schedulePost, 
        formState, pendingMedia, resetForm, clearPendingMedia
    ]);

    // Determine if form can be submitted
    const canSubmit = useMemo(() => {
        return isValid && 
               (formState.text.trim() || pendingMedia.file_id) && 
               formState.selectedChannel && 
               formState.scheduleTime &&
               !loading;
    }, [isValid, formState, pendingMedia.file_id, loading]);

    return (
        <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Typography variant="h6">Post Yaratish</Typography>
                
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}
                
                <TextField
                    label="Post matni"
                    multiline
                    rows={4}
                    value={formState.text}
                    onChange={(e) => updateField('text', e.target.value)}
                    variant="outlined"
                    fullWidth
                    error={!!formErrors.text}
                    helperText={formErrors.text}
                />
                
                <FormControl fullWidth error={!!formErrors.selectedChannel}>
                    <InputLabel id="channel-select-label">Kanalni tanlang</InputLabel>
                    <Select
                        labelId="channel-select-label"
                        value={formState.selectedChannel}
                        label="Kanalni tanlang"
                        onChange={(e) => updateField('selectedChannel', e.target.value)}
                    >
                        {channelOptions.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </Select>
                    {formErrors.selectedChannel && (
                        <Typography variant="caption" color="error">
                            {formErrors.selectedChannel}
                        </Typography>
                    )}
                </FormControl>
                
                <DateTimePicker
                    label="Yuborish vaqti"
                    value={formState.scheduleTime}
                    onChange={(newValue) => updateField('scheduleTime', newValue)}
                    slotProps={{
                        textField: {
                            error: !!formErrors.scheduleTime,
                            helperText: formErrors.scheduleTime
                        }
                    }}
                />

                {pendingMedia.file_id && (
                    <MediaPreview 
                        media={pendingMedia} 
                        onClear={clearPendingMedia}
                    />
                )}

                <ButtonConstructor onAddButton={handleAddButton} />

                {buttons.length > 0 && (
                    <Box>
                        <Typography variant="subtitle2">Qo'shilgan tugmalar:</Typography>
                        <List dense>
                            {buttons.map((button, index) => (
                                <ListItem key={index}>
                                    <Chip 
                                        label={`${button.text} -> ${button.url}`} 
                                        onDelete={() => handleRemoveButton(index)}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}

                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSchedulePost}
                    disabled={!canSubmit}
                    sx={{ minHeight: 48 }}
                >
                    {loading ? (
                        <CircularProgress size={24} />
                    ) : (
                        'Postni Rejalashtirish'
                    )}
                </Button>
            </Box>
        </LocalizationProvider>
    );
});

PostCreator.displayName = 'PostCreator';

export default PostCreator;
