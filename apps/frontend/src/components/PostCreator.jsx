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
import CloseIcon from '@mui/icons-material/Close';
import { useAppStore } from '../store/appStore';
import { useLoadingState, useFormState, useTelegramWebApp } from '../hooks';
import ButtonConstructor from './ButtonConstructor';
import MediaPreview from "./MediaPreview.jsx";

// Form validation with user-friendly messages
const validatePostForm = (values) => {
    const errors = {};
    
    if (!values.text?.trim() && !values.hasMedia) {
        errors.text = 'Please add some text or upload an image to create your post';
    }
    
    if (values.text && values.text.length > 4096) {
        errors.text = `Your message is too long (${values.text.length}/4096 characters). Please shorten it.`;
    }
    
    if (!values.selectedChannel) {
        errors.selectedChannel = 'Please select a channel to post to';
    }
    
    if (!values.scheduleTime) {
        errors.scheduleTime = 'Please select when you want to publish this post';
    } else if (new Date(values.scheduleTime) <= new Date()) {
        errors.scheduleTime = 'Please choose a time in the future for scheduling';
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

    // Update hasMedia when pendingMedia changes - using a ref to avoid infinite loops
    const prevMediaFileId = React.useRef(pendingMedia.file_id);
    React.useEffect(() => {
        if (prevMediaFileId.current !== pendingMedia.file_id) {
            updateField('hasMedia', !!pendingMedia.file_id);
            prevMediaFileId.current = pendingMedia.file_id;
        }
    }, [pendingMedia.file_id]);

    // Memoized channel options
    const channelOptions = useMemo(() => 
        channels.map((channel) => ({
            value: channel.id,
            label: `${channel.title} (@${channel.username})`
        })), [channels]
    );

    // Optimized button handlers
    const handleAddButton = useCallback((newButton) => {
        setButtons(prev => [...prev, newButton]);
        hapticFeedback('light');
    }, [hapticFeedback]);

    const handleRemoveButton = useCallback((index) => {
        setButtons(prev => prev.filter((_, i) => i !== index));
        hapticFeedback('light');
    }, [hapticFeedback]);

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
        } catch {
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
        <Box 
            component="form" 
            sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}
            role="form"
            aria-labelledby="post-creator-title"
            noValidate
        >
            <Typography 
                variant="h2" 
                id="post-creator-title"
                sx={{ fontSize: '1.5rem', mb: 1 }}
            >
                Create New Post
            </Typography>
            
            {/* Live region for form status */}
            <div aria-live="polite" aria-atomic="true" className="sr-only">
                {loading && "Creating your post..."}
                {error && `Error: ${error}`}
            </div>
            
            {error && (
                <Alert severity="error" sx={{ mb: 2 }} role="alert">
                    <strong>Unable to create post:</strong> {error}
                </Alert>
            )}

            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="sr-only">Post Content</legend>
                
                <TextField
                    label="Post content"
                    multiline
                    rows={4}
                    value={formState.text}
                    onChange={(e) => updateField('text', e.target.value)}
                    variant="outlined"
                    fullWidth
                    error={!!formErrors.text}
                    helperText={formErrors.text}
                    aria-describedby={formErrors.text ? "text-error" : "text-help"}
                    id="post-text"
                    placeholder="What would you like to share with your audience?"
                    autoComplete="off"
                    inputProps={{
                        'aria-label': 'Post content',
                        'aria-required': 'true',
                        maxLength: 4096
                    }}
                />
                
                {!formErrors.text && (
                    <Typography 
                        variant="caption" 
                        color="text.secondary" 
                        id="text-help"
                        sx={{ mt: 0.5, display: 'block' }}
                    >
                        {formState.text.length}/4096 characters
                        {formState.text.length === 0 && " • You can also upload media instead of text"}
                    </Typography>
                )}
                
                {formErrors.text && (
                    <Typography 
                        variant="caption" 
                        color="error" 
                        id="text-error"
                        role="alert"
                        sx={{ mt: 0.5, display: 'block' }}
                    >
                        {formErrors.text}
                    </Typography>
                )}
            </fieldset>

            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="sr-only">Channel Selection</legend>
                
                <FormControl fullWidth error={!!formErrors.selectedChannel}>
                    <InputLabel id="channel-select-label">Select Channel</InputLabel>
                    <Select
                        labelId="channel-select-label"
                        value={formState.selectedChannel}
                        label="Select Channel"
                        onChange={(e) => updateField('selectedChannel', e.target.value)}
                        aria-describedby={formErrors.selectedChannel ? "channel-error" : "channel-help"}
                        id="channel-select"
                    >
                        {channelOptions.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </Select>
                    
                    {!formErrors.selectedChannel && channelOptions.length === 0 && (
                        <Typography 
                            variant="caption" 
                            color="text.secondary" 
                            id="channel-help"
                            sx={{ mt: 0.5, display: 'block' }}
                        >
                            No channels available. Please add a channel first.
                        </Typography>
                    )}
                    
                    {formErrors.selectedChannel && (
                        <Typography 
                            variant="caption" 
                            color="error" 
                            id="channel-error"
                            role="alert"
                            sx={{ mt: 0.5, display: 'block' }}
                        >
                            {formErrors.selectedChannel}
                        </Typography>
                    )}
                </FormControl>
            </fieldset>

            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="sr-only">Schedule Settings</legend>
                
                <TextField
                    label="Schedule for"
                    type="datetime-local"
                    value={formState.scheduleTime ? 
                        new Date(formState.scheduleTime).toISOString().slice(0, 16) : ''}
                    onChange={(e) => updateField('scheduleTime', e.target.value ? new Date(e.target.value) : null)}
                    InputLabelProps={{ shrink: true }}
                    error={!!formErrors.scheduleTime}
                    helperText={formErrors.scheduleTime}
                    aria-describedby={formErrors.scheduleTime ? "schedule-error" : "schedule-help"}
                    id="schedule-time"
                    autoComplete="off"
                    fullWidth
                />
                
                {!formErrors.scheduleTime && (
                    <Typography 
                        variant="caption" 
                        color="text.secondary" 
                        id="schedule-help"
                        sx={{ mt: 0.5, display: 'block' }}
                    >
                        Choose when your post should be published
                    </Typography>
                )}
                
                {formErrors.scheduleTime && (
                    <Typography 
                        variant="caption" 
                        color="error" 
                        id="schedule-error"
                        role="alert"
                        sx={{ mt: 0.5, display: 'block' }}
                    >
                        {formErrors.scheduleTime}
                    </Typography>
                )}
            </fieldset>

            {pendingMedia.file_id && (
                <Box role="group" aria-labelledby="media-preview-label">
                    <Typography variant="h3" id="media-preview-label" sx={{ fontSize: '1rem', mb: 1 }}>
                        Attached Media
                    </Typography>
                    <MediaPreview 
                        media={pendingMedia} 
                        onClear={clearPendingMedia}
                    />
                </Box>
            )}

            <Box role="group" aria-labelledby="button-constructor-label">
                <Typography variant="h3" id="button-constructor-label" sx={{ fontSize: '1rem', mb: 1 }}>
                    Interactive Buttons (Optional)
                </Typography>
                <ButtonConstructor onAddButton={handleAddButton} />
            </Box>

            {buttons.length > 0 && (
                <Box sx={{ mt: 1 }} role="group" aria-labelledby="added-buttons-label">
                    <Typography variant="h3" id="added-buttons-label" sx={{ fontSize: '1rem', mb: 1 }}>
                        Added Buttons ({buttons.length})
                    </Typography>
                    <List dense>
                        {buttons.map((button, index) => (
                            <ListItem key={index} sx={{ px: 0 }}>
                                <Chip
                                    label={`${button.text} (${button.type})`}
                                    onDelete={() => handleRemoveButton(index)}
                                    size="small"
                                    deleteIcon={<CloseIcon />}
                                    aria-label={`Remove button: ${button.text}`}
                                />
                            </ListItem>
                        ))}
                    </List>
                </Box>
            )}

            <Button
                variant="contained"
                onClick={handleSchedulePost}
                disabled={loading || !canSubmit}
                sx={{ 
                    mt: 2,
                    '&:focus-visible': {
                        outline: '2px solid #fff',
                        outlineOffset: '2px'
                    }
                }}
                aria-describedby="submit-help"
            >
                {loading ? (
                    <>
                        <CircularProgress size={16} sx={{ mr: 1 }} aria-hidden="true" />
                        Creating Post...
                    </>
                ) : (
                    'Schedule Post'
                )}
            </Button>
            
            {!canSubmit && !loading && (
                <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    id="submit-help"
                    sx={{ mt: 0.5 }}
                >
                    Please fill in all required fields to schedule your post
                </Typography>
            )}
        </Box>
    );
});

PostCreator.displayName = 'PostCreator';

export default PostCreator;
