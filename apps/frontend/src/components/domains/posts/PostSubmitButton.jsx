/**
 * PostSubmitButton - Submit button with loading state for post creation
 */

import React from 'react';
import { Button, CircularProgress, Typography } from '@mui/material';

const PostSubmitButton = ({
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
