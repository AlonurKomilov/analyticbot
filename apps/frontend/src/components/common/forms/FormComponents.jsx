import React, { useState, useCallback } from 'react';
import {
    TextField,
    FormControl,
    FormHelperText,
    InputLabel,
    Select,
    MenuItem,
    Checkbox,
    FormControlLabel,
    RadioGroup,
    Radio,
    Chip,
    Box,
    Typography,
    Button
} from '@mui/material';

/**
 * Enhanced form field components with built-in validation and consistent styling
 */

/**
 * ValidatedTextField - TextField with built-in validation
 */
export const ValidatedTextField = React.forwardRef(({
    name,
    value,
    onChange,
    validation,
    errors = {},
    required = false,
    label,
    placeholder,
    multiline = false,
    rows = 1,
    type = 'text',
    fullWidth = true,
    variant = 'outlined',
    size = 'medium',
    helperText,
    showCharacterCount = false,
    maxLength,
    sx = {},
    ...props
}, ref) => {
    const error = errors[name];
    const characterCount = value?.length || 0;

    const handleChange = useCallback((event) => {
        const newValue = event.target.value;

        // Apply maxLength if specified
        if (maxLength && newValue.length > maxLength) {
            return;
        }

        onChange?.(event);
    }, [onChange, maxLength]);

    const getHelperText = () => {
        if (error) return error;
        if (showCharacterCount && maxLength) {
            return `${characterCount}/${maxLength} characters${helperText ? ` • ${helperText}` : ''}`;
        }
        return helperText;
    };

    return (
        <TextField
            ref={ref}
            name={name}
            value={value || ''}
            onChange={handleChange}
            label={required ? `${label} *` : label}
            placeholder={placeholder}
            multiline={multiline}
            rows={multiline ? rows : undefined}
            type={type}
            fullWidth={fullWidth}
            variant={variant}
            size={size}
            error={!!error}
            helperText={getHelperText()}
            sx={{
                '& .MuiOutlinedInput-root': {
                    '&.Mui-focused': {
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderWidth: '2px',
                        },
                    },
                    '&.Mui-error': {
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderWidth: '2px',
                        },
                    },
                },
                ...sx,
            }}
            {...props}
        />
    );
});

ValidatedTextField.displayName = 'ValidatedTextField';

/**
 * ValidatedSelect - Select with built-in validation
 */
export const ValidatedSelect = ({
    name,
    value,
    onChange,
    options = [],
    errors = {},
    required = false,
    label,
    placeholder = 'Select an option...',
    fullWidth = true,
    variant = 'outlined',
    size = 'medium',
    helperText,
    multiple = false,
    sx = {},
    ...props
}) => {
    const error = errors[name];

    return (
        <FormControl
            fullWidth={fullWidth}
            variant={variant}
            size={size}
            error={!!error}
            sx={sx}
        >
            <InputLabel>{required ? `${label} *` : label}</InputLabel>
            <Select
                name={name}
                value={value || (multiple ? [] : '')}
                onChange={onChange}
                label={required ? `${label} *` : label}
                multiple={multiple}
                displayEmpty
                renderValue={multiple ? (selected) => {
                    if (selected.length === 0) return <em>{placeholder}</em>;
                    return (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {selected.map((val) => (
                                <Chip key={val} label={val} size="small" />
                            ))}
                        </Box>
                    );
                } : undefined}
                {...props}
            >
                {!multiple && (
                    <MenuItem value="" disabled>
                        <em>{placeholder}</em>
                    </MenuItem>
                )}
                {options.map((option) => (
                    <MenuItem
                        key={option.value}
                        value={option.value}
                        disabled={option.disabled}
                    >
                        {option.label}
                    </MenuItem>
                ))}
            </Select>
            {(error || helperText) && (
                <FormHelperText>{error || helperText}</FormHelperText>
            )}
        </FormControl>
    );
};

/**
 * FormSection - Reusable form section with consistent styling
 */
export const FormSection = ({
    title,
    subtitle,
    children,
    required = false,
    sx = {}
}) => (
    <Box sx={{ mb: 3, ...sx }}>
        {title && (
            <Typography
                variant="h6"
                fontWeight={600}
                sx={{ mb: subtitle ? 0.5 : 2 }}
            >
                {required ? `${title} *` : title}
            </Typography>
        )}
        {subtitle && (
            <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2 }}
            >
                {subtitle}
            </Typography>
        )}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {children}
        </Box>
    </Box>
);

/**
 * FormActions - Standardized form action buttons
 */
export const FormActions = ({
    onSubmit,
    onCancel,
    onReset,
    submitLabel = 'Submit',
    cancelLabel = 'Cancel',
    resetLabel = 'Reset',
    loading = false,
    disabled = false,
    submitColor = 'primary',
    align = 'right', // 'left', 'center', 'right', 'space-between'
    sx = {}
}) => (
    <Box
        sx={{
            display: 'flex',
            gap: 2,
            mt: 3,
            justifyContent: align === 'space-between' ? 'space-between' :
                           align === 'center' ? 'center' :
                           align === 'left' ? 'flex-start' : 'flex-end',
            ...sx
        }}
    >
        {align === 'space-between' && onReset && (
            <Box>
                <Button
                    variant="outlined"
                    color="inherit"
                    onClick={onReset}
                    disabled={loading || disabled}
                >
                    {resetLabel}
                </Button>
            </Box>
        )}

        <Box sx={{ display: 'flex', gap: 1 }}>
            {onCancel && (
                <Button
                    variant="outlined"
                    color="inherit"
                    onClick={onCancel}
                    disabled={loading}
                >
                    {cancelLabel}
                </Button>
            )}

            {align !== 'space-between' && onReset && (
                <Button
                    variant="outlined"
                    color="inherit"
                    onClick={onReset}
                    disabled={loading || disabled}
                >
                    {resetLabel}
                </Button>
            )}

            <Button
                variant="contained"
                color={submitColor}
                onClick={onSubmit}
                disabled={loading || disabled}
                sx={{ minWidth: 100 }}
            >
                {loading ? 'Submitting...' : submitLabel}
            </Button>
        </Box>
    </Box>
);
