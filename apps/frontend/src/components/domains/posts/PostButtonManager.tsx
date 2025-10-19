/**
 * PostButtonManager - Inline button management component for posts
 */

import React from 'react';
import { Box, Typography, List, ListItem, Chip } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ButtonConstructor from '../../ButtonConstructor';

interface Button {
    text: string;
    url: string;
}

interface PostButtonManagerProps {
    buttons?: Button[];
    onAddButton: (button: Button) => void;
    onRemoveButton: (index: number) => void;
    disabled?: boolean;
}

const PostButtonManager: React.FC<PostButtonManagerProps> = ({
    buttons = [],
    onAddButton,
    onRemoveButton,
    disabled = false
}) => {
    return (
        <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
                Inline Buttons (Optional)
            </Typography>

            <ButtonConstructor
                onAddButton={onAddButton}
                {...(disabled && { disabled })}
                aria-label="Add inline button"
            />

            {buttons.length > 0 && (
                <Box sx={{ mt: 2 }}>
                    <Typography
                        variant="subtitle2"
                        sx={{ mb: 1 }}
                        id="buttons-list-label"
                    >
                        Added Buttons:
                    </Typography>
                    <List
                        dense
                        aria-labelledby="buttons-list-label"
                        sx={{ bgcolor: 'background.paper', borderRadius: 1 }}
                    >
                        {buttons.map((button, index) => (
                            <ListItem
                                key={`${button.text}-${index}`}
                                sx={{
                                    py: 0.5,
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}
                            >
                                <Typography variant="body2">
                                    {button.text} → {button.url}
                                </Typography>
                                <Chip
                                    label="Remove"
                                    variant="outlined"
                                    size="small"
                                    deleteIcon={<CloseIcon />}
                                    onDelete={() => onRemoveButton(index)}
                                    disabled={disabled}
                                    aria-label={`Remove button ${button.text}`}
                                    sx={{ ml: 1 }}
                                />
                            </ListItem>
                        ))}
                    </List>
                </Box>
            )}
        </Box>
    );
};

PostButtonManager.displayName = 'PostButtonManager';

export default PostButtonManager;
