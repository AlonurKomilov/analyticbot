import React from 'react';
import { Box, IconButton, Tooltip, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useMediaStore } from '@/stores';

const MediaPreview = () => {
    const { pendingMedia, clearPendingMedia } = useMediaStore();

    if (!pendingMedia?.previewUrl) {
        return null;
    }

    return (
        <figure style={{ margin: 0 }}>
            <Box sx={{
                position: 'relative',
                mb: 2,
                border: '1px solid #30363d',
                borderRadius: '6px',
                overflow: 'hidden',
                maxWidth: '200px',
                '&:focus-within': {
                    outline: '2px solid #2196F3',
                    outlineOffset: '2px'
                }
            }}>
                <Tooltip title="Remove Media">
                    <IconButton
                        onClick={clearPendingMedia}
                        size="small"
                        aria-label="Remove this media file from your post"
                        sx={{
                            position: 'absolute',
                            top: 4,
                            right: 4,
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            color: 'white',
                            '&:hover': {
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                transform: 'scale(1.1)'
                            },
                            '&:focus-visible': {
                                outline: '2px solid #fff',
                                outlineOffset: '2px'
                            }
                        }}
                    >
                        <CloseIcon sx={{ fontSize: '1rem' }} aria-hidden="true" />
                    </IconButton>
                </Tooltip>
                <img
                    src={pendingMedia.previewUrl}
                    alt={pendingMedia.description || `${pendingMedia.file_type || 'Media'} file selected for your post`}
                    style={{
                        width: '100%',
                        display: 'block',
                        borderRadius: '6px'
                    }}
                />
                <figcaption className="sr-only">
                    Media preview: {pendingMedia.file_type || 'file'} ready to be included in your post
                </figcaption>
            </Box>

            {/* File info for screen readers */}
            <Typography variant="caption" color="text.secondary" sx={{
                display: 'block',
                mt: 1,
                fontSize: '0.75rem'
            }}>
                <span aria-hidden="true">📎</span>
                {pendingMedia.file_type ? pendingMedia.file_type.toUpperCase() : 'Media'} file attached
            </Typography>
        </figure>
    );
};

export default MediaPreview;
