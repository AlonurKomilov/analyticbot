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
import { Box, Typography, Alert, Button, CircularProgress } from '@mui/material';
import { useChannelStore, usePostStore, useMediaStore } from '@store';
import { useLoadingState, useFormState } from '@/hooks';
import MediaPreview from '@shared/components/ui/MediaPreview';
import { useResponsive } from '@/theme/responsive.js';

// Import decomposed sub-components
import PostContentInput from './PostContentInput.jsx';
import ChannelSelector from './ChannelSelector.jsx';
import ScheduleTimeInput from './ScheduleTimeInput.jsx';
import PostButtonManager from './PostButtonManager';
import { validatePostForm, canSubmitForm } from './PostFormValidation.js';

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

const PostCreator: React.FC = React.memo(() => {
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
    const { loading, error } = useLoadingState('schedulePost');

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

    // Send post immediately (no scheduling)
    const handleSendNow = useCallback(async () => {
        // For immediate send, only validate text and channel (scheduleTime not required)
        const errors: Record<string, string> = {};

        if (!formState.text.trim()) {
            errors.text = 'Post text is required';
        }
        if (!formState.selectedChannel) {
            errors.selectedChannel = 'Please select a channel';
        }

        if (Object.keys(errors).length > 0) return;

        try {
            const inline_buttons = buttons.length > 0
                ? buttons.map(btn => [{ text: btn.text, url: btn.url }])
                : undefined;

            await sendNowPost({
                text: formState.text,
                selectedChannel: formState.selectedChannel,
                scheduleTime: null,  // No schedule time for immediate send
                inline_buttons,
                media: pendingMedia ? pendingMedia : undefined
            } as any);

            // Reset form on success
            resetForm();
            setButtons([]);
        } catch (err) {
            console.error('Failed to send post:', err);
        }
    }, [formState, buttons, pendingMedia, sendNowPost, resetForm]);

    // Schedule post for later
    const handleSchedulePost = useCallback(async () => {
        const errors = validatePostForm(formState);

        if (Object.keys(errors).length > 0) return;

        try {
            const inline_buttons = buttons.length > 0
                ? buttons.map(btn => [{ text: btn.text, url: btn.url }])
                : undefined;

            await schedulePost({
                text: formState.text,
                selectedChannel: formState.selectedChannel,
                scheduleTime: formState.scheduleTime || '',
                inline_buttons,
                media: pendingMedia ? pendingMedia : undefined
            } as any);

            // Reset form on success
            resetForm();
            setButtons([]);
        } catch (err) {
            console.error('Failed to schedule post:', err);
        }
    }, [formState, buttons, pendingMedia, schedulePost, resetForm]);

    // Determine if form can be submitted for scheduled posts (requires scheduleTime)
    const canSubmit = useMemo(() =>
        canSubmitForm(formState, formErrors),
        [formState, formErrors]
    );

    // Determine if form can be submitted for immediate send (no scheduleTime required)
    const canSendNow = useMemo(() =>
        !!(formState.text.trim() && formState.selectedChannel),
        [formState.text, formState.selectedChannel]
    );

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

            {/* Schedule Settings Section */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0, marginBottom: 24 }}>
                <legend className="sr-only">Schedule Settings</legend>
                <ScheduleTimeInput
                    value={formState.scheduleTime ? new Date(formState.scheduleTime) : null}
                    onChange={(value: Date | null) => updateField('scheduleTime', value ? value.toISOString() : null)}
                    error={formErrors.scheduleTime}
                    disabled={loading}
                />
            </fieldset>

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

            {/* Submit Section - Two action buttons */}
            <Box sx={{
                mt: { xs: 3, sm: 4 },
                display: 'flex',
                gap: 2,
                flexDirection: { xs: 'column', sm: 'row' },
                justifyContent: { xs: 'stretch', sm: 'flex-start' }
            }}>
                {/* Send Now Button - Primary action */}
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSendNow}
                    disabled={loading || !canSendNow}
                    sx={{
                        minWidth: { xs: '100%', sm: 140 },
                        '&:focus-visible': {
                            outline: '2px solid #fff',
                            outlineOffset: '2px'
                        }
                    }}
                    aria-describedby="send-now-help"
                >
                    {loading ? (
                        <>
                            <CircularProgress size={16} sx={{ mr: 1 }} aria-hidden="true" />
                            Sending...
                        </>
                    ) : (
                        'Send Now'
                    )}
                </Button>

                {/* Schedule Post Button - Secondary action */}
                <Button
                    variant="outlined"
                    color="primary"
                    onClick={handleSchedulePost}
                    disabled={loading || !canSubmit}
                    sx={{
                        minWidth: { xs: '100%', sm: 140 },
                        '&:focus-visible': {
                            outline: '2px solid #fff',
                            outlineOffset: '2px'
                        }
                    }}
                    aria-describedby="schedule-help"
                >
                    {loading ? (
                        <>
                            <CircularProgress size={16} sx={{ mr: 1 }} aria-hidden="true" />
                            Scheduling...
                        </>
                    ) : (
                        'Schedule Post'
                    )}
                </Button>
            </Box>

            {/* Help text for validation */}
            {!canSendNow && !loading && (
                <Typography
                    variant="caption"
                    color="text.secondary"
                    id="send-now-help"
                    sx={{ mt: 1, display: 'block' }}
                >
                    Enter post text and select a channel to send immediately
                </Typography>
            )}
            {canSendNow && !canSubmit && !loading && (
                <Typography
                    variant="caption"
                    color="text.secondary"
                    id="schedule-help"
                    sx={{ mt: 1, display: 'block' }}
                >
                    Set a schedule time to schedule this post
                </Typography>
            )}
        </Box>
    );
});

PostCreator.displayName = 'PostCreator';

export default PostCreator;
