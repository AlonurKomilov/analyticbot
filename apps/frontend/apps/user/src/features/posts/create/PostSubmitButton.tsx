/**
 * PostSubmitButton - Submit button with loading state for post creation
 */

import React from 'react';
import { Button, CircularProgress, Typography } from '@mui/material';

/**
 * Props for PostSubmitButton component
 */
interface PostSubmitButtonProps {
    /** Callback when submit button is clicked */
    onSubmit: () => void;
    /** Loading state indicator */
    loading?: boolean;
    /** Disabled state */
    disabled?: boolean;
    /** Whether form can be submitted (validation passed) */
    canSubmit?: boolean;
}

/**
 * PostSubmitButton Component
 * Submit button with loading state and validation feedback
 */
const PostSubmitButton: React.FC<PostSubmitButtonProps> = ({
    onSubmit,
    loading = false,
    disabled = false,
    canSubmit = true
}) => {
    return (
        <>
            <Button
                variant="contained"
                onClick={onSubmit}
                disabled={loading || disabled || !canSubmit}
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
        </>
    );
};

PostSubmitButton.displayName = 'PostSubmitButton';

export default PostSubmitButton;
