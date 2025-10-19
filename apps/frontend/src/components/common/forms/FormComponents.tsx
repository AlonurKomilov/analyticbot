import React, { useCallback } from 'react';
import {
    TextField,
    FormControl,
    FormHelperText,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    Box,
    Typography,
    Button,
    TextFieldProps,
    SxProps,
    Theme
} from '@mui/material';

/**
 * Enhanced form field components with built-in validation and consistent styling
 */

interface ValidationRules {
    [key: string]: any;
}

interface FormErrors {
    [key: string]: string;
}

interface ValidatedTextFieldProps extends Omit<TextFieldProps, 'error' | 'helperText'> {
    name: string;
    value?: string;
    onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
    validation?: ValidationRules;
    errors?: FormErrors;
    required?: boolean;
    label?: string;
    placeholder?: string;
    multiline?: boolean;
    rows?: number;
    type?: string;
    fullWidth?: boolean;
    variant?: 'outlined' | 'filled' | 'standard';
    size?: 'small' | 'medium';
    helperText?: string;
    showCharacterCount?: boolean;
    maxLength?: number;
    sx?: SxProps<Theme>;
}

interface SelectOption {
    value: string | number;
    label: string;
    disabled?: boolean;
}

interface ValidatedSelectProps {
    name: string;
    value?: string | number | string[] | number[];
    onChange?: (event: any) => void;
    options?: SelectOption[];
    errors?: FormErrors;
    required?: boolean;
    label?: string;
    placeholder?: string;
    fullWidth?: boolean;
    variant?: 'outlined' | 'filled' | 'standard';
    size?: 'small' | 'medium';
    helperText?: string;
    multiple?: boolean;
    sx?: SxProps<Theme>;
    [key: string]: any;
}

interface FormSectionProps {
    title?: string;
    subtitle?: string;
    children: React.ReactNode;
    required?: boolean;
    sx?: SxProps<Theme>;
}

interface FormActionsProps {
    onSubmit?: () => void;
    onCancel?: () => void;
    onReset?: () => void;
    submitLabel?: string;
    cancelLabel?: string;
    resetLabel?: string;
    loading?: boolean;
    disabled?: boolean;
    submitColor?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
    align?: 'left' | 'center' | 'right' | 'space-between';
    sx?: SxProps<Theme>;
}

/**
 * ValidatedTextField - TextField with built-in validation
 */
export const ValidatedTextField = React.forwardRef<HTMLDivElement, ValidatedTextFieldProps>(({
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

    const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = event.target.value;

        // Apply maxLength if specified
        if (maxLength && newValue.length > maxLength) {
            return;
        }

        onChange?.(event);
    }, [onChange, maxLength]);

    const getHelperText = (): string | undefined => {
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
export const ValidatedSelect: React.FC<ValidatedSelectProps> = ({
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
                renderValue={multiple ? (selected: any) => {
                    if ((selected as any[]).length === 0) return <em>{placeholder}</em>;
                    return (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {(selected as any[]).map((val: any) => (
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
export const FormSection: React.FC<FormSectionProps> = ({
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
export const FormActions: React.FC<FormActionsProps> = ({
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
