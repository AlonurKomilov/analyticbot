/**
 * RegisterForm Hook
 * State management for registration form
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { calculatePasswordStrength } from './passwordUtils';
import type { FormData, FormErrors } from './types';

export function useRegisterForm() {
    const { t } = useTranslation('auth');
    const { register, isLoading } = useAuth();

    const [formData, setFormData] = useState<FormData>({
        email: '',
        password: '',
        confirmPassword: '',
        username: '',
        fullName: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [errors, setErrors] = useState<FormErrors>({});
    const [registerError, setRegisterError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

    // Calculate password strength
    const passwordStrength = calculatePasswordStrength(formData.password);

    // Form validation
    const validateForm = useCallback((): boolean => {
        const newErrors: FormErrors = {};

        // Username validation
        if (!formData.username.trim()) {
            newErrors.username = t('register.validation.usernameRequired');
        } else if (formData.username.length < 3) {
            newErrors.username = t('register.validation.usernameMinLength');
        } else if (formData.username.length > 50) {
            newErrors.username = t('register.validation.usernameMaxLength');
        }

        // Full name validation
        if (!formData.fullName.trim()) {
            newErrors.fullName = t('register.validation.fullNameRequired');
        }

        // Email validation
        if (!formData.email) {
            newErrors.email = t('register.validation.emailRequired');
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = t('register.validation.emailInvalid');
        }

        // Password validation
        if (!formData.password) {
            newErrors.password = t('register.validation.passwordRequired');
        } else if (passwordStrength.score < 60) {
            newErrors.password = t('register.validation.passwordWeak');
        }

        // Confirm password validation
        if (!formData.confirmPassword) {
            newErrors.confirmPassword = t('register.validation.confirmPasswordRequired');
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = t('register.validation.passwordsDoNotMatch');
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }, [formData, passwordStrength.score, t]);

    // Handle input changes
    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Clear field error when user starts typing
        if (errors[name as keyof FormErrors]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }

        // Clear register error
        if (registerError) {
            setRegisterError('');
        }

        // Show password requirements when user starts typing password
        if (name === 'password' && value && !showPasswordRequirements) {
            setShowPasswordRequirements(true);
        }
    }, [errors, registerError, showPasswordRequirements]);

    // Handle form submission
    const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        setRegisterError('');

        try {
            const payload = {
                email: formData.email,
                password: formData.password,
                username: formData.username,
                full_name: formData.fullName
            };
            console.log('🚀 Registration payload:', payload);

            const result = await register(payload);

            if (!result.success) {
                setRegisterError(result.error || 'Registration failed. Please try again.');
            }
        } catch (error) {
            setRegisterError('Network error. Please check your connection and try again.');
        } finally {
            setIsSubmitting(false);
        }
    }, [formData, validateForm, register]);

    // Toggle password visibility
    const togglePasswordVisibility = useCallback(() => {
        setShowPassword(prev => !prev);
    }, []);

    const toggleConfirmPasswordVisibility = useCallback(() => {
        setShowConfirmPassword(prev => !prev);
    }, []);

    const togglePasswordRequirements = useCallback(() => {
        setShowPasswordRequirements(prev => !prev);
    }, []);

    return {
        formData,
        errors,
        registerError,
        isSubmitting,
        isLoading,
        showPassword,
        showConfirmPassword,
        showPasswordRequirements,
        passwordStrength,
        handleChange,
        handleSubmit,
        togglePasswordVisibility,
        toggleConfirmPasswordVisibility,
        togglePasswordRequirements
    };
}
