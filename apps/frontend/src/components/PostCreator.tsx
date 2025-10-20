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
import { Box, Typography, Alert } from '@mui/material';
import { useChannelStore, usePostStore, useMediaStore } from '@/stores';
import { useLoadingState, useFormState } from '../hooks';
import MediaPreview from "./MediaPreview.jsx";
import { useResponsive, MOBILE_PATTERNS } from '../theme/responsive.js';

// Import decomposed sub-components
import PostContentInput from './domains/posts/PostContentInput.jsx';
import ChannelSelector from './domains/posts/ChannelSelector.jsx';
import ScheduleTimeInput from './domains/posts/ScheduleTimeInput.jsx';
import PostButtonManager from './domains/posts/PostButtonManager.tsx';
import PostSubmitButton from './domains/posts/PostSubmitButton.jsx';
import { validatePostForm, canSubmitForm } from './domains/posts/PostFormValidation.js';

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

interface FormErrors {
    text?: string;
    selectedChannel?: string;
    scheduleTime?: string;
    [key: string]: string | undefined;
}

const PostCreator: React.FC = React.memo(() => {
    const { channels } = useChannelStore();
    const { schedulePost } = usePostStore();
    const { pendingMedia } = useMediaStore();

    const responsive = useResponsive();

    // Enhanced form state management
    const { state: formState, updateField, resetForm, errors: formErrors, setErrors: setFormErrors } = useFormState<FormState>({
        text: '',
        selectedChannel: '',
        scheduleTime: null,
        hasMedia: false
    });

    const [buttons, setButtons] = useState<Button[]>([]);
    const { loading, error, executeWithLoading } = useLoadingState('schedulePost');

    // Update hasMedia when pendingMedia changes
    const prevMediaFileId = React.useRef(pendingMedia.file_id);
    useEffect(() => {
        if (prevMediaFileId.current !== pendingMedia.file_id) {
            updateField('hasMedia', !!pendingMedia.file_id);
            prevMediaFileId.current = pendingMedia.file_id;
        }
    }, [pendingMedia.file_id, updateField]);

    // Optimized button handlers
    const handleAddButton = useCallback((newButton: Button) => {
        setButtons(prev => [...prev, newButton]);
    }, []);

    const handleRemoveButton = useCallback((index: number) => {
        setButtons(prev => prev.filter((_, i) => i !== index));
    }, []);

    // Main form submission handler
    const handleSchedulePost = useCallback(async () => {
        const errors = validatePostForm(formState);
        setFormErrors(errors);

        if (Object.keys(errors).length > 0) return;

        await executeWithLoading(async () => {
            const inline_buttons = buttons.length > 0
                ? buttons.map(btn => [{ text: btn.text, url: btn.url }])
                : null;

            await schedulePost({
                ...formState,
                inline_buttons,
                media: pendingMedia.file_id ? pendingMedia : null
            });

            // Reset form on success
            resetForm();
            setButtons([]);
        });
    }, [formState, buttons, pendingMedia, executeWithLoading, schedulePost, resetForm, setFormErrors]);

    // Determine if form can be submitted
    const canSubmit = useMemo(() =>
        canSubmitForm(formState, formErrors),
        [formState, formErrors]
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
                    error={formErrors.text}
                    helperText={formErrors.text}
                    disabled={loading}
                />
            </fieldset>

            {/* Media Preview Section */}
            {pendingMedia.file_id && (
                <Box sx={{ mb: 3 }}>
                    <MediaPreview media={[pendingMedia]} />
                </Box>
            )}

            {/* Channel Selection Section */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0, marginBottom: 24 }}>
                <legend className="sr-only">Channel Selection</legend>
                <ChannelSelector
                    channels={channels}
                    selectedChannel={formState.selectedChannel}
                    onChange={(value: string) => updateField('selectedChannel', value)}
                    error={formErrors.selectedChannel}
                    disabled={loading}
                />
            </fieldset>

            {/* Schedule Settings Section */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0, marginBottom: 24 }}>
                <legend className="sr-only">Schedule Settings</legend>
                <ScheduleTimeInput
                    value={formState.scheduleTime}
                    onChange={(value: string | null) => updateField('scheduleTime', value)}
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

            {/* Submit Section */}
            <Box sx={{
                mt: { xs: 3, sm: 4 },
                display: 'flex',
                justifyContent: { xs: 'center', sm: 'flex-start' }
            }}>
                <PostSubmitButton
                    onSubmit={handleSchedulePost}
                    loading={loading}
                    canSubmit={canSubmit}
                />
            </Box>
        </Box>
    );
});

PostCreator.displayName = 'PostCreator';

export default PostCreator;
