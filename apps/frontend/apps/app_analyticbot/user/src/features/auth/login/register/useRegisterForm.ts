/**
 * RegisterForm Hook
 * State management for registration form with real-time availability checks
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/api/client';
import { calculatePasswordStrength } from './passwordUtils';
import type { FormData, FormErrors, AvailabilityStatus } from './types';

// Debounce delay for availability checks
const DEBOUNCE_DELAY = 500;

export function useRegisterForm() {
    const { t } = useTranslation('auth');
    const { register, isLoading } = useAuth();

    const [formData, setFormData] = useState<FormData>({
        email: '',
        password: '',
        confirmPassword: '',
        username: '',
        firstName: '',
        lastName: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [errors, setErrors] = useState<FormErrors>({});
    const [registerError, setRegisterError] = useState('');
    const [registerSuccess, setRegisterSuccess] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

    // Availability status for username and email
    const [usernameStatus, setUsernameStatus] = useState<AvailabilityStatus>({
        checking: false,
        available: null,
        message: ''
    });
    const [emailStatus, setEmailStatus] = useState<AvailabilityStatus>({
        checking: false,
        available: null,
        message: ''
    });

    // Refs for debouncing
    const usernameTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const emailTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Calculate password strength
    const passwordStrength = calculatePasswordStrength(formData.password);

    // Check username availability
    const checkUsernameAvailability = useCallback(async (username: string) => {
        if (username.length < 3) {
            setUsernameStatus({ checking: false, available: null, message: '' });
            return;
        }

        setUsernameStatus(prev => ({ ...prev, checking: true }));
        
        try {
            const response = await apiClient.post('/auth/check-username', { username });
            const data = (response as any).data || response;
            setUsernameStatus({
                checking: false,
                available: data.available,
                message: data.message
            });
        } catch (error) {
            setUsernameStatus({
                checking: false,
                available: null,
                message: 'Could not check username'
            });
        }
    }, []);

    // Check email availability
    const checkEmailAvailability = useCallback(async (email: string) => {
        if (!/\S+@\S+\.\S+/.test(email)) {
            setEmailStatus({ checking: false, available: null, message: '' });
            return;
        }

        setEmailStatus(prev => ({ ...prev, checking: true }));
        
        try {
            const response = await apiClient.post('/auth/check-email', { email });
            const data = (response as any).data || response;
            setEmailStatus({
                checking: false,
                available: data.available,
                message: data.message
            });
        } catch (error) {
            setEmailStatus({
                checking: false,
                available: null,
                message: 'Could not check email'
            });
        }
    }, []);

    // Debounced username check
    useEffect(() => {
        if (usernameTimeoutRef.current) {
            clearTimeout(usernameTimeoutRef.current);
        }

        if (formData.username.length >= 3) {
            usernameTimeoutRef.current = setTimeout(() => {
                checkUsernameAvailability(formData.username);
            }, DEBOUNCE_DELAY);
        } else {
            setUsernameStatus({ checking: false, available: null, message: '' });
        }

        return () => {
            if (usernameTimeoutRef.current) {
                clearTimeout(usernameTimeoutRef.current);
            }
        };
    }, [formData.username, checkUsernameAvailability]);

    // Debounced email check
    useEffect(() => {
        if (emailTimeoutRef.current) {
            clearTimeout(emailTimeoutRef.current);
        }

        if (/\S+@\S+\.\S+/.test(formData.email)) {
            emailTimeoutRef.current = setTimeout(() => {
                checkEmailAvailability(formData.email);
            }, DEBOUNCE_DELAY);
        } else {
            setEmailStatus({ checking: false, available: null, message: '' });
        }

        return () => {
            if (emailTimeoutRef.current) {
                clearTimeout(emailTimeoutRef.current);
            }
        };
    }, [formData.email, checkEmailAvailability]);

    // Form validation
    const validateForm = useCallback((): boolean => {
        const newErrors: FormErrors = {};

        // Username validation
        if (!formData.username.trim()) {
            newErrors.username = t('register.validation.usernameRequired', 'Username is required');
        } else if (formData.username.length < 3) {
            newErrors.username = t('register.validation.usernameMinLength', 'Username must be at least 3 characters');
        } else if (formData.username.length > 50) {
            newErrors.username = t('register.validation.usernameMaxLength', 'Username must be less than 50 characters');
        } else if (usernameStatus.available === false) {
            newErrors.username = usernameStatus.message;
        }

        // First name validation
        if (!formData.firstName.trim()) {
            newErrors.firstName = t('register.validation.firstNameRequired', 'First name is required');
        }

        // Last name validation  
        if (!formData.lastName.trim()) {
            newErrors.lastName = t('register.validation.lastNameRequired', 'Last name is required');
        }

        // Email validation
        if (!formData.email) {
            newErrors.email = t('register.validation.emailRequired', 'Email is required');
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = t('register.validation.emailInvalid', 'Please enter a valid email');
        } else if (emailStatus.available === false) {
            newErrors.email = emailStatus.message;
        }

        // Password validation
        if (!formData.password) {
            newErrors.password = t('register.validation.passwordRequired', 'Password is required');
        } else if (passwordStrength.score < 60) {
            newErrors.password = t('register.validation.passwordWeak', 'Password is too weak');
        }

        // Confirm password validation
        if (!formData.confirmPassword) {
            newErrors.confirmPassword = t('register.validation.confirmPasswordRequired', 'Please confirm your password');
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = t('register.validation.passwordsDoNotMatch', 'Passwords do not match');
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }, [formData, passwordStrength.score, usernameStatus, emailStatus, t]);

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

        // Clear register error/success
        if (registerError) {
            setRegisterError('');
        }
        if (registerSuccess) {
            setRegisterSuccess('');
        }

        // Show password requirements when user starts typing password
        if (name === 'password' && value && !showPasswordRequirements) {
            setShowPasswordRequirements(true);
        }
    }, [errors, registerError, registerSuccess, showPasswordRequirements]);

    // Handle form submission
    const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        // Don't submit if username or email not available
        if (usernameStatus.available === false || emailStatus.available === false) {
            return;
        }

        setIsSubmitting(true);
        setRegisterError('');
        setRegisterSuccess('');

        try {
            const payload = {
                email: formData.email,
                password: formData.password,
                username: formData.username,
                first_name: formData.firstName.trim(),
                last_name: formData.lastName.trim()
            };
            console.log('🚀 Registration payload:', payload);

            const result = await register(payload);

            if (result.success) {
                // Registration successful - show success message and redirect to login
                setRegisterSuccess('Account created successfully! Redirecting to login...');
                setTimeout(() => {
                    window.location.href = '/auth?tab=login&registered=true';
                }, 2000);
            } else {
                setRegisterError(result.error || 'Registration failed. Please try again.');
            }
        } catch (error) {
            setRegisterError('Network error. Please check your connection and try again.');
        } finally {
            setIsSubmitting(false);
        }
    }, [formData, validateForm, register, usernameStatus.available, emailStatus.available]);

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
        registerSuccess,
        isSubmitting,
        isLoading,
        showPassword,
        showConfirmPassword,
        showPasswordRequirements,
        passwordStrength,
        usernameStatus,
        emailStatus,
        handleChange,
        handleSubmit,
        togglePasswordVisibility,
        toggleConfirmPasswordVisibility,
        togglePasswordRequirements
    };
}
