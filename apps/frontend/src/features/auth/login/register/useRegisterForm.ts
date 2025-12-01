/**
 * RegisterForm Hook
 * State management for registration form
 */

import { useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { calculatePasswordStrength } from './passwordUtils';
import type { FormData, FormErrors } from './types';

export function useRegisterForm() {
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
            newErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        } else if (formData.username.length > 50) {
            newErrors.username = 'Username must be less than 50 characters';
        }

        // Full name validation
        if (!formData.fullName.trim()) {
            newErrors.fullName = 'Full name is required';
        }

        // Email validation
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        // Password validation
        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (passwordStrength.score < 60) {
            newErrors.password = 'Password is too weak. Please follow the requirements below.';
        }

        // Confirm password validation
        if (!formData.confirmPassword) {
            newErrors.confirmPassword = 'Please confirm your password';
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }, [formData, passwordStrength.score]);

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
