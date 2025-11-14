/**
 * PostCreator - Refactored post creation component with focused sub-components
 *
 * This component has been decomposed from a 396-line monolith into:
 * - PostContentInput: Text content input with validation
 * - ChannelSelector: Channel selection with memoized options
 * - ScheduleTimeInput: Date/time scheduling input
 * - PostButtonManager: Inline button management
 * - PostSubmitButton: Submit button with loading states
 * - PostFormValidation: Form validation utilities
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Box, Typography, Alert, Button, CircularProgress, Switch, FormControlLabel, Collapse } from '@mui/material';
import { useChannelStore, usePostStore, useMediaStore } from '@store';
import { useLoadingState, useFormState } from '@/hooks';
import MediaPreview from '@shared/components/ui/MediaPreview';
import { useResponsive } from '@/theme/responsive.js';

// Import decomposed sub-components
import PostContentInput from './PostContentInput.jsx';
import ChannelSelector from './ChannelSelector.jsx';
import ScheduleTimeInput from './ScheduleTimeInput.jsx';
import PostButtonManager from './PostButtonManager';

interface Button {
    text: string;
    url: string;
}

interface FormState {
    text: string;
    selectedChannel: string;
    scheduleTime: string | null;
    hasMedia: boolean;
}

interface PostCreatorProps {
    initialChannelId?: string;
    initialScheduledTime?: string;
    fromRecommendation?: boolean;
}

const PostCreator: React.FC<PostCreatorProps> = React.memo(({
    initialChannelId,
    initialScheduledTime,
    fromRecommendation
}) => {
    const { channels } = useChannelStore();
    const { schedulePost, sendNowPost } = usePostStore();
    const { pendingMedia } = useMediaStore();

    const responsive = useResponsive();

    // Enhanced form state management
    const { state: formState, updateField, resetForm, errors: formErrors } = useFormState<FormState>({
        text: '',
        selectedChannel: '',
        scheduleTime: null,
        hasMedia: false
    });

    const [buttons, setButtons] = useState<Button[]>([]);
    const [isScheduleMode, setIsScheduleMode] = useState(!!initialScheduledTime);
    const { loading, error } = useLoadingState('schedulePost');

    // Initialize form with recommended values from Best Time Recommendations
    useEffect(() => {
        if (fromRecommendation && initialChannelId) {
            updateField('selectedChannel', String(initialChannelId));
        }
        if (fromRecommendation && initialScheduledTime) {
            updateField('scheduleTime', initialScheduledTime);
        }
    }, [fromRecommendation, initialChannelId, initialScheduledTime, updateField]);

    // Update hasMedia when pendingMedia changes
    const prevMediaFile = React.useRef(pendingMedia?.file);
    useEffect(() => {
        if (prevMediaFile.current !== pendingMedia?.file) {
            updateField('hasMedia', !!pendingMedia);
            prevMediaFile.current = pendingMedia?.file;
        }
    }, [pendingMedia, updateField]);

    // Optimized button handlers
    const handleAddButton = useCallback((newButton: Button) => {
        setButtons(prev => [...prev, newButton]);
    }, []);

    const handleRemoveButton = useCallback((index: number) => {
        setButtons(prev => prev.filter((_, i) => i !== index));
    }, []);

    // Handle post submission (either immediate or scheduled)
    const handleSubmitPost = useCallback(async () => {
        // For immediate send, only validate text and channel
        // For scheduled send, also validate scheduleTime
        const errors: Record<string, string> = {};

        if (!formState.text.trim()) {
            errors.text = 'Post text is required';
        }
        if (!formState.selectedChannel) {
            errors.selectedChannel = 'Please select a channel';
        }
        if (isScheduleMode && !formState.scheduleTime) {
            errors.scheduleTime = 'Schedule time is required when scheduling';
        }

        if (Object.keys(errors).length > 0) return;

        try {
            const inline_buttons = buttons.length > 0
                ? buttons.map(btn => [{ text: btn.text, url: btn.url }])
                : undefined;

            if (isScheduleMode) {
                // Schedule for later
                await schedulePost({
                    text: formState.text,
                    selectedChannel: formState.selectedChannel,
                    scheduleTime: formState.scheduleTime || '',
                    inline_buttons,
                    media: pendingMedia ? pendingMedia : undefined
                } as any);
            } else {
                // Send immediately
                await sendNowPost({
                    text: formState.text,
                    selectedChannel: formState.selectedChannel,
                    scheduleTime: null,
                    inline_buttons,
                    media: pendingMedia ? pendingMedia : undefined
                } as any);
            }

            // Reset form on success
            resetForm();
            setButtons([]);
            setIsScheduleMode(false);
        } catch (err) {
            console.error('Failed to submit post:', err);
        }
    }, [formState, buttons, pendingMedia, isScheduleMode, sendNowPost, schedulePost, resetForm]);

    // Determine if form can be submitted
    const canSubmit = useMemo(() => {
        const hasBasicFields = formState.text.trim() && formState.selectedChannel;

        if (isScheduleMode) {
            // In schedule mode, also need valid schedule time
            return hasBasicFields && !!formState.scheduleTime;
        }

        // In send now mode, just need text and channel
        return hasBasicFields;
    }, [formState.text, formState.selectedChannel, formState.scheduleTime, isScheduleMode]);

    return (
        <Box
            sx={{
                width: '100%',
                maxWidth: { xs: '100%', sm: 600 },
                mx: 'auto',
                p: { xs: 2, sm: 3 },
                mb: { xs: 2, sm: 0 }
            }}
            component="form"
            role="form"
            aria-labelledby="post-creator-title"
            noValidate
        >
            <Typography
                variant="h2"
                id="post-creator-title"
                sx={{
                    fontSize: { xs: '1.25rem', sm: '1.5rem' },
                    mb: { xs: 2, sm: 3 },
                    textAlign: { xs: 'center', sm: 'left' }
                }}
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

            {/* Post Content Section */}
            <fieldset style={{
                border: 'none',
                padding: 0,
                margin: 0,
                marginBottom: responsive.isMobile ? 16 : 24
            }}>
                <legend className="sr-only">Post Content</legend>
                <PostContentInput
                    value={formState.text}
                    onChange={(value: string) => updateField('text', value)}
                    error={!!formErrors.text}
                    helperText={formErrors.text}
                    disabled={loading}
                />
            </fieldset>

            {/* Media Preview Section */}
            {pendingMedia && (
                <Box sx={{ mb: 3 }}>
                    <MediaPreview />
                </Box>
            )}

            {/* Channel Selection Section */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0, marginBottom: 24 }}>
                <legend className="sr-only">Channel Selection</legend>
                <ChannelSelector
                    channels={channels}
                    selectedChannel={formState.selectedChannel}
                    onChange={(value: string | number) => updateField('selectedChannel', String(value))}
                    error={formErrors.selectedChannel}
                    disabled={loading}
                />
            </fieldset>

            {/* Schedule Toggle Section */}
            <Box sx={{ mb: 3 }}>
                <FormControlLabel
                    control={
                        <Switch
                            checked={isScheduleMode}
                            onChange={(e) => setIsScheduleMode(e.target.checked)}
                            disabled={loading}
                            color="primary"
                        />
                    }
                    label={
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            Schedule for later
                        </Typography>
                    }
                />

                {/* Collapsible Schedule Settings */}
                <Collapse in={isScheduleMode}>
                    <Box sx={{ mt: 2 }}>
                        <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                            <legend className="sr-only">Schedule Settings</legend>
                            <ScheduleTimeInput
                                value={formState.scheduleTime ? new Date(formState.scheduleTime) : null}
                                onChange={(value: Date | null) => updateField('scheduleTime', value ? value.toISOString() : null)}
                                error={formErrors.scheduleTime}
                                disabled={loading}
                            />
                        </fieldset>
                    </Box>
                </Collapse>
            </Box>

            {/* Inline Buttons Section */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0, marginBottom: 24 }}>
                <legend className="sr-only">Inline Buttons</legend>
                <PostButtonManager
                    buttons={buttons}
                    onAddButton={handleAddButton}
                    onRemoveButton={handleRemoveButton}
                    disabled={loading}
                />
            </fieldset>

            {/* Submit Section - Single Dynamic Button */}
            <Box sx={{
                mt: { xs: 3, sm: 4 },
                display: 'flex',
                flexDirection: 'column',
                alignItems: { xs: 'stretch', sm: 'flex-start' }
            }}>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSubmitPost}
                    disabled={loading || !canSubmit}
                    sx={{
                        minWidth: { xs: '100%', sm: 200 },
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
                            {isScheduleMode ? 'Scheduling...' : 'Sending...'}
                        </>
                    ) : (
                        <>
                            {isScheduleMode ? '📅 Schedule Post' : '🚀 Send Now'}
                        </>
                    )}
                </Button>

                {/* Help text for validation */}
                {!canSubmit && !loading && (
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        id="submit-help"
                        sx={{ mt: 1, display: 'block' }}
                    >
                        {isScheduleMode
                            ? 'Enter post text, select a channel, and set a schedule time'
                            : 'Enter post text and select a channel to send immediately'
                        }
                    </Typography>
                )}
            </Box>
        </Box>
    );
});

PostCreator.displayName = 'PostCreator';

export default PostCreator;
