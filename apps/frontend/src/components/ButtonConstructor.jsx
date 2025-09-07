import React, { useState } from 'react';
import { TextField, Button, Box, Select, MenuItem, FormControl, InputLabel, Typography } from '@mui/material';

const ButtonConstructor = ({ onAddButton }) => {
    const [buttonText, setButtonText] = useState('');
    const [buttonUrl, setButtonUrl] = useState('');
    const [buttonType, setButtonType] = useState('url');
    const [urlError, setUrlError] = useState('');

    const validateUrl = (url) => {
        if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
            setUrlError('URL must start with http:// or https://');
            return false;
        }
        setUrlError('');
        return true;
    };

    const handleAddButton = () => {
        if (buttonType === 'url') {
            if (!validateUrl(buttonUrl)) {
                return;
            }
        }

        onAddButton({ text: buttonText, url: buttonUrl, type: buttonType });
        setButtonText('');
        setButtonUrl('');
    };

    const handleUrlChange = (e) => {
        const newUrl = e.target.value;
        setButtonUrl(newUrl);
        validateUrl(newUrl);
    };

    const canAdd = buttonText.trim() && (buttonType !== 'url' || (buttonUrl.trim() && !urlError));

    return (
        <fieldset style={{ 
            border: '1px solid #e0e0e0', 
            borderRadius: '8px', 
            padding: '16px',
            margin: 0
        }}>
            <legend style={{ 
                padding: '0 8px',
                fontWeight: 'bold',
                color: '#666'
            }}>
                Button Configuration
            </legend>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                    label="Button Text"
                    value={buttonText}
                    onChange={(e) => setButtonText(e.target.value)}
                    size="small"
                    required
                    id="button-text"
                    aria-describedby="button-text-help"
                    placeholder="e.g., Learn More"
                    autoComplete="off"
                    inputProps={{
                        'aria-label': 'Button text',
                        'aria-required': 'true',
                        maxLength: 50
                    }}
                />
                <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    id="button-text-help"
                    sx={{ mt: -1 }}
                >
                    Text that will appear on the button ({buttonText.length}/50 characters)
                </Typography>
                
                <FormControl size="small">
                    <InputLabel id="button-type-label">Button Type</InputLabel>
                    <Select
                        labelId="button-type-label"
                        value={buttonType}
                        label="Button Type"
                        onChange={(e) => setButtonType(e.target.value)}
                        id="button-type"
                        aria-describedby="button-type-help"
                    >
                        <MenuItem value="url">URL Link</MenuItem>
                    </Select>
                    <Typography 
                        variant="caption" 
                        color="text.secondary" 
                        id="button-type-help"
                        sx={{ mt: 0.5 }}
                    >
                        Choose what happens when users click the button
                    </Typography>
                </FormControl>
                
                {buttonType === 'url' && (
                    <>
                        <TextField
                            label="Button URL"
                            value={buttonUrl}
                            onChange={handleUrlChange}
                            size="small"
                            required
                            error={!!urlError}
                            helperText={urlError || "Full URL including https://"}
                            id="button-url"
                            aria-describedby={urlError ? "url-error" : "url-help"}
                            placeholder="https://example.com"
                            autoComplete="url"
                            inputProps={{
                                'aria-label': 'Button URL',
                                'aria-required': 'true',
                                type: 'url'
                            }}
                        />
                        
                        {urlError && (
                            <Typography 
                                variant="caption" 
                                color="error" 
                                id="url-error"
                                role="alert"
                                sx={{ mt: -1 }}
                            >
                                {urlError}
                            </Typography>
                        )}
                        
                        {!urlError && buttonUrl && (
                            <Typography 
                                variant="caption" 
                                color="text.secondary" 
                                id="url-help"
                                sx={{ mt: -1 }}
                            >
                                <span aria-hidden="true">✓</span> Valid URL format
                            </Typography>
                        )}
                    </>
                )}
                
                <Button 
                    onClick={handleAddButton} 
                    variant="outlined" 
                    disabled={!canAdd}
                    aria-describedby="add-button-help"
                    sx={{
                        '&:focus-visible': {
                            outline: '2px solid #2196F3',
                            outlineOffset: '2px'
                        }
                    }}
                >
                    Add Button
                </Button>
                
                {!canAdd && (
                    <Typography 
                        variant="caption" 
                        color="text.secondary" 
                        id="add-button-help"
                        sx={{ mt: -1 }}
                    >
                        {!buttonText.trim() ? "Enter button text to continue" : 
                         (buttonType === 'url' && !buttonUrl.trim()) ? "Enter a valid URL" :
                         urlError ? "Fix the URL error" : ""}
                    </Typography>
                )}
            </Box>
        </fieldset>
    );
};

export default ButtonConstructor;
