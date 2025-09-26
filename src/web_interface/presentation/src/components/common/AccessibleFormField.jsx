import React from 'react';
import { 
    TextField, 
    FormControl, 
    FormHelperText, 
    Typography,
    Box
} from '@mui/material';
import { generateId } from '../../utils/accessibility.js';

/**
 * Enhanced accessible form field component
 * 
 * @param {Object} props - Component props
 * @param {string} props.label - Field label
 * @param {string} props.value - Field value
 * @param {Function} props.onChange - Change handler
 * @param {string} props.error - Error message
 * @param {string} props.helperText - Helper text
 * @param {boolean} props.required - Whether field is required
 * @param {string} props.type - Input type
 * @param {string} props.autoComplete - Autocomplete hint
 * @param {Object} props.validation - Validation rules
 * @param {number} props.maxLength - Maximum character length
 * @param {string} props.placeholder - Placeholder text
 */
const AccessibleFormField = React.forwardRef(({
    label,
    value = '',
    onChange,
    error,
    helperText,
    required = false,
    type = 'text',
    autoComplete,
    validation = {},
    maxLength,
    placeholder,
    multiline = false,
    rows = 1,
    size = 'medium',
    disabled = false,
    ...props
}, ref) => {
    
    // Generate unique IDs for accessibility
    const fieldId = React.useMemo(() => generateId('form-field'), []);
    const helperId = React.useMemo(() => generateId('helper'), []);
    const errorId = React.useMemo(() => generateId('error'), []);
    
    // Character count for fields with maxLength
    const characterCount = maxLength ? `${value.length}/${maxLength}` : null;
    
    // Helper text with character count
    const enhancedHelperText = React.useMemo(() => {
        const parts = [];
        if (helperText) parts.push(helperText);
        if (characterCount) parts.push(characterCount);
        return parts.join(' • ');
    }, [helperText, characterCount]);
    
    // Accessibility attributes
    const ariaProps = {
        'aria-required': required,
        'aria-invalid': !!error,
        'aria-describedby': [
            error ? errorId : null,
            enhancedHelperText ? helperId : null
        ].filter(Boolean).join(' ') || undefined
    };
    
    return (
        <FormControl 
            fullWidth 
            error={!!error}
            size={size}
            disabled={disabled}
        >
            <TextField
                ref={ref}
                id={fieldId}
                label={required ? `${label} *` : label}
                value={value}
                onChange={onChange}
                error={!!error}
                type={type}
                autoComplete={autoComplete}
                placeholder={placeholder}
                multiline={multiline}
                rows={multiline ? rows : undefined}
                disabled={disabled}
                inputProps={{
                    maxLength,
                    ...ariaProps,
                    ...props.inputProps
                }}
                InputLabelProps={{
                    shrink: type === 'datetime-local' || !!value || !!placeholder,
                    ...props.InputLabelProps
                }}
                sx={{
                    '& .MuiInputBase-root': {
                        minHeight: size === 'small' ? '40px' : '48px',
                    },
                    ...props.sx
                }}
                {...props}
            />
            
            {/* Error message */}
            {error && (
                <FormHelperText 
                    id={errorId}
                    role="alert"
                    sx={{ 
                        color: 'error.main',
                        fontWeight: 500,
                        mt: 0.5
                    }}
                >
                    {error}
                </FormHelperText>
            )}
            
            {/* Helper text and character count */}
            {enhancedHelperText && !error && (
                <FormHelperText 
                    id={helperId}
                    sx={{ mt: 0.5 }}
                >
                    {enhancedHelperText}
                </FormHelperText>
            )}
        </FormControl>
    );
});

AccessibleFormField.displayName = 'AccessibleFormField';

/**
 * Form fieldset component for grouping related fields
 */
export const FormFieldset = ({ 
    legend, 
    children, 
    description,
    required = false,
    ...props 
}) => {
    const legendId = React.useMemo(() => generateId('legend'), []);
    const descriptionId = React.useMemo(() => generateId('description'), []);
    
    return (
        <Box
            component="fieldset"
            sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                p: 2,
                m: 0,
                mb: 2,
                '& legend': {
                    px: 1,
                    fontWeight: 600,
                    color: 'text.primary'
                }
            }}
            role="group"
            aria-labelledby={legendId}
            aria-describedby={description ? descriptionId : undefined}
            {...props}
        >
            <legend id={legendId}>
                {required ? `${legend} *` : legend}
            </legend>
            
            {description && (
                <Typography 
                    variant="body2" 
                    color="text.secondary" 
                    id={descriptionId}
                    sx={{ mb: 2 }}
                >
                    {description}
                </Typography>
            )}
            
            {children}
        </Box>
    );
};

/**
 * Form validation summary component
 */
export const FormValidationSummary = ({ 
    errors = {}, 
    title = "Please fix the following errors:"
}) => {
    const errorList = Object.entries(errors).filter(([_, error]) => error);
    
    if (errorList.length === 0) return null;
    
    return (
        <Box
            role="alert"
            aria-live="assertive"
            sx={{
                p: 2,
                mb: 2,
                border: '2px solid',
                borderColor: 'error.main',
                borderRadius: 1,
                bgcolor: 'error.light',
                color: 'error.contrastText'
            }}
        >
            <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
                {title}
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2 }}>
                {errorList.map(([field, error]) => (
                    <li key={field}>
                        <Typography variant="body2">
                            {error}
                        </Typography>
                    </li>
                ))}
            </Box>
        </Box>
    );
};

export default AccessibleFormField;
