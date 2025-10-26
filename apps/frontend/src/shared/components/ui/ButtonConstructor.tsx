import React, { useState, ChangeEvent } from 'react';
import {
    Box,
    TextField,
    Select,
    MenuItem,
    Button,
    Typography,
    FormControl,
    InputLabel,
    FormHelperText
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

type ButtonType = 'url';

interface ButtonConfig {
    text: string;
    url: string;
}

interface ButtonConstructorProps {
    onAddButton?: (button: ButtonConfig) => void;
}

/**
 * ButtonConstructor - Inline keyboard button configuration
 *
 * Allows users to add URL buttons to Telegram messages.
 * Validates URL format and character limits.
 */
const ButtonConstructor: React.FC<ButtonConstructorProps> = ({ onAddButton }) => {
    const [buttonText, setButtonText] = useState<string>('');
    const [buttonUrl, setButtonUrl] = useState<string>('');
    const [buttonType, setButtonType] = useState<ButtonType>('url');
    const [urlError, setUrlError] = useState<string>('');

    // URL validation
    const validateUrl = (url: string): boolean => {
        if (!url.trim()) {
            setUrlError('URL is required');
            return false;
        }

        try {
            new URL(url);
            setUrlError('');
            return true;
        } catch {
            setUrlError('Please enter a valid URL (e.g., https://example.com)');
            return false;
        }
    };

    const handleUrlChange = (e: ChangeEvent<HTMLInputElement>): void => {
        const url = e.target.value;
        setButtonUrl(url);
        if (url.trim()) {
            validateUrl(url);
        } else {
            setUrlError('');
        }
    };

    const handleAddButton = (): void => {
        if (!buttonText.trim()) {
            return;
        }

        if (!validateUrl(buttonUrl)) {
            return;
        }

        onAddButton?.({
            text: buttonText,
            url: buttonUrl
        });

        // Reset form
        setButtonText('');
        setButtonUrl('');
        setUrlError('');
    };

    const isValid = buttonText.trim() && buttonUrl.trim() && !urlError;

    return (
        <Box
            sx={{
                p: 3,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                bgcolor: 'background.paper'
            }}
        >
            <Typography variant="h6" gutterBottom>
                Button Constructor
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Add interactive buttons to your message
            </Typography>

            {/* Button Type Selector */}
            <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="button-type-label">Button Type</InputLabel>
                <Select
                    labelId="button-type-label"
                    value={buttonType}
                    onChange={(e) => setButtonType(e.target.value as ButtonType)}
                    label="Button Type"
                    aria-label="Select button type"
                >
                    <MenuItem value="url">URL Button</MenuItem>
                </Select>
                <FormHelperText>
                    URL buttons open a link when clicked
                </FormHelperText>
            </FormControl>

            {/* Button Text */}
            <TextField
                fullWidth
                label="Button Text"
                placeholder="Click here"
                value={buttonText}
                onChange={(e) => setButtonText(e.target.value)}
                sx={{ mb: 2 }}
                inputProps={{
                    maxLength: 30,
                    'aria-label': 'Button text',
                    'aria-describedby': 'button-text-helper'
                }}
                helperText={`${buttonText.length}/30 characters`}
                FormHelperTextProps={{
                    id: 'button-text-helper'
                }}
            />

            {/* Button URL */}
            <TextField
                fullWidth
                label="Button URL"
                placeholder="https://example.com"
                value={buttonUrl}
                onChange={handleUrlChange}
                error={!!urlError}
                helperText={urlError || 'Enter the full URL including https://'}
                sx={{ mb: 2 }}
                inputProps={{
                    'aria-label': 'Button URL',
                    'aria-describedby': 'button-url-helper',
                    'aria-invalid': !!urlError
                }}
                FormHelperTextProps={{
                    id: 'button-url-helper'
                }}
            />

            {/* Add Button */}
            <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddButton}
                disabled={!isValid}
                fullWidth
                aria-label="Add button to message"
            >
                Add Button
            </Button>

            {/* Preview */}
            {buttonText && (
                <Box
                    sx={{
                        mt: 3,
                        p: 2,
                        bgcolor: 'action.hover',
                        borderRadius: 1
                    }}
                >
                    <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                        Preview:
                    </Typography>
                    <Button
                        variant="outlined"
                        fullWidth
                        sx={{
                            textTransform: 'none',
                            pointerEvents: 'none'
                        }}
                    >
                        {buttonText || 'Button text'}
                    </Button>
                </Box>
            )}
        </Box>
    );
};

export default ButtonConstructor;
