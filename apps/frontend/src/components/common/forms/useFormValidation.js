import { useState, useCallback, useMemo } from 'react';

/**
 * useFormValidation - Comprehensive form validation hook
 *
 * Features:
 * - Real-time field validation
 * - Form-level validation
 * - Custom validation rules
 * - Error state management
 * - Form submission handling
 */

export const useFormValidation = (initialValues = {}, validationRules = {}) => {
    const [values, setValues] = useState(initialValues);
    const [errors, setErrors] = useState({});
    const [touched, setTouched] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Validation functions
    const validateField = useCallback((name, value) => {
        const rules = validationRules[name];
        if (!rules) return '';

        // Required validation
        if (rules.required && (!value || (typeof value === 'string' && !value.trim()))) {
            return rules.requiredMessage || `${name} is required`;
        }

        // Type-specific validations
        if (value) {
            // Email validation
            if (rules.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                return rules.emailMessage || 'Invalid email format';
            }

            // URL validation
            if (rules.url && !/^https?:\/\/.+/.test(value)) {
                return rules.urlMessage || 'URL must start with http:// or https://';
            }

            // Min length validation
            if (rules.minLength && value.length < rules.minLength) {
                return rules.minLengthMessage || `Must be at least ${rules.minLength} characters`;
            }

            // Max length validation
            if (rules.maxLength && value.length > rules.maxLength) {
                return rules.maxLengthMessage || `Must be no more than ${rules.maxLength} characters`;
            }

            // Pattern validation
            if (rules.pattern && !rules.pattern.test(value)) {
                return rules.patternMessage || 'Invalid format';
            }

            // Custom validation
            if (rules.custom && typeof rules.custom === 'function') {
                const customError = rules.custom(value);
                if (customError) return customError;
            }
        }

        return '';
    }, [validationRules]);

    // Handle field changes
    const handleChange = useCallback((event) => {
        const { name, value, type, checked } = event.target;
        const fieldValue = type === 'checkbox' ? checked : value;

        setValues(prev => ({
            ...prev,
            [name]: fieldValue
        }));

        // Validate field if it has been touched
        if (touched[name]) {
            const error = validateField(name, fieldValue);
            setErrors(prev => ({
                ...prev,
                [name]: error
            }));
        }
    }, [validateField, touched]);

    // Handle field blur (mark as touched)
    const handleBlur = useCallback((event) => {
        const { name } = event.target;
        const value = values[name];

        setTouched(prev => ({
            ...prev,
            [name]: true
        }));

        // Validate field on blur
        const error = validateField(name, value);
        setErrors(prev => ({
            ...prev,
            [name]: error
        }));
    }, [validateField, values]);

    // Validate entire form
    const validateForm = useCallback(() => {
        const newErrors = {};
        let isValid = true;

        Object.keys(validationRules).forEach(name => {
            const error = validateField(name, values[name]);
            if (error) {
                newErrors[name] = error;
                isValid = false;
            }
        });

        setErrors(newErrors);
        setTouched(
            Object.keys(validationRules).reduce((acc, name) => {
                acc[name] = true;
                return acc;
            }, {})
        );

        return isValid;
    }, [validateField, values, validationRules]);

    // Reset form
    const resetForm = useCallback(() => {
        setValues(initialValues);
        setErrors({});
        setTouched({});
        setIsSubmitting(false);
    }, [initialValues]);

    // Set field value
    const setValue = useCallback((name, value) => {
        setValues(prev => ({
            ...prev,
            [name]: value
        }));

        // Clear error if field becomes valid
        if (errors[name]) {
            const error = validateField(name, value);
            if (!error) {
                setErrors(prev => ({
                    ...prev,
                    [name]: ''
                }));
            }
        }
    }, [validateField, errors]);

    // Set multiple values
    const setMultipleValues = useCallback((newValues) => {
        setValues(prev => ({
            ...prev,
            ...newValues
        }));
    }, []);

    // Handle form submission
    const handleSubmit = useCallback(async (onSubmit) => {
        setIsSubmitting(true);

        const isValid = validateForm();

        if (isValid && onSubmit) {
            try {
                await onSubmit(values);
            } catch (error) {
                console.error('Form submission error:', error);
            }
        }

        setIsSubmitting(false);
        return isValid;
    }, [validateForm, values]);

    // Computed properties
    const isValid = useMemo(() => {
        return Object.keys(validationRules).every(name => !validateField(name, values[name]));
    }, [values, validationRules, validateField]);

    const hasErrors = useMemo(() => {
        return Object.values(errors).some(error => error);
    }, [errors]);

    return {
        // Values
        values,
        errors,
        touched,
        isSubmitting,
        isValid,
        hasErrors,

        // Methods
        handleChange,
        handleBlur,
        handleSubmit,
        validateForm,
        resetForm,
        setValue,
        setValues: setMultipleValues,

        // Helpers
        getFieldProps: (name) => ({
            name,
            value: values[name] || '',
            onChange: handleChange,
            onBlur: handleBlur,
            error: !!errors[name],
            helperText: errors[name]
        })
    };
};

export default useFormValidation;
