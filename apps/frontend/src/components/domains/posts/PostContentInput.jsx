/**
 * PostContentInput - Text content input component for post creation
 */

import React from 'react';
import { TextField, Typography } from '@mui/material';

const PostContentInput = ({
    value,
    onChange,
    error,
    helperText,
    disabled = false
}) => {
    return (
        <>
            <TextField
                label="Post content"
                multiline
                rows={4}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                variant="outlined"
                fullWidth
                error={!!error}
                helperText={helperText}
                aria-describedby={error ? "text-error" : "text-help"}
                id="post-text"
                placeholder="What would you like to share with your audience?"
                autoComplete="off"
                disabled={disabled}
                inputProps={{
                    'aria-label': 'Post content',
                    'aria-required': 'true',
                    maxLength: 4096
                }}
            />

            {!error && (
                <Typography
                    variant="caption"
                    color="text.secondary"
                    id="text-help"
                    sx={{ mt: 0.5, display: 'block' }}
                >
                    Share your thoughts, updates, or multimedia content ({value?.length || 0}/4096)
                </Typography>
            )}
        </>
    );
};

PostContentInput.displayName = 'PostContentInput';

export default PostContentInput;
