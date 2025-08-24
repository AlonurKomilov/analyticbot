import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useAppStore } from '../store/appStore.js';

/**
 * Custom hook for managing loading states with debouncing
 */
export const useLoadingState = (operation, delay = 300) => {
    const [debouncedLoading, setDebouncedLoading] = useState(false);
    const { isLoading, getError, clearError } = useAppStore();
    const timeoutRef = useRef();

    const loading = isLoading(operation);
    const error = getError(operation);

    useEffect(() => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        if (loading) {
            setDebouncedLoading(true);
        } else {
            timeoutRef.current = setTimeout(() => {
                setDebouncedLoading(false);
            }, delay);
        }

        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [loading, delay]);

    const clearOperationError = useCallback(() => {
        clearError(operation);
    }, [clearError, operation]);

    return {
        loading,
        debouncedLoading,
        error,
        clearError: clearOperationError
    };
};

/**
 * Custom hook for form handling with validation
 */
export const useFormState = (initialState, validator) => {
    const [state, setState] = useState(initialState);
    const [errors, setErrors] = useState({});
    const [touched, setTouched] = useState({});

    const updateField = useCallback((field, value) => {
        setState(prev => ({ ...prev, [field]: value }));
        setTouched(prev => ({ ...prev, [field]: true }));
        
        if (validator && touched[field]) {
            const fieldErrors = validator({ ...state, [field]: value });
            setErrors(prev => ({ ...prev, [field]: fieldErrors[field] }));
        }
    }, [state, touched, validator]);

    const validateForm = useCallback(() => {
        if (!validator) return true;
        
        const formErrors = validator(state);
        setErrors(formErrors);
        
        return Object.keys(formErrors).length === 0;
    }, [state, validator]);

    const resetForm = useCallback(() => {
        setState(initialState);
        setErrors({});
        setTouched({});
    }, [initialState]);

    return {
        state,
        errors,
        touched,
        updateField,
        validateForm,
        resetForm,
        isValid: Object.keys(errors).length === 0
    };
};

/**
 * Custom hook for optimized list operations
 */
export const useOptimizedList = (items, keyExtractor) => {
    const itemsMap = useMemo(() => {
        return items.reduce((map, item) => {
            map[keyExtractor(item)] = item;
            return map;
        }, {});
    }, [items, keyExtractor]);

    const getItem = useCallback((key) => itemsMap[key], [itemsMap]);
    
    const sortedItems = useMemo(() => {
        return [...items].sort((a, b) => {
            const aKey = keyExtractor(a);
            const bKey = keyExtractor(b);
            return aKey.localeCompare(bKey);
        });
    }, [items, keyExtractor]);

    return {
        items,
        itemsMap,
        sortedItems,
        getItem,
        count: items.length
    };
};

/**
 * Custom hook for managing media uploads (Enhanced for TWA Phase 2.1)
 */
export const useMediaUpload = () => {
    const { uploadMedia, uploadMediaDirect, pendingMedia, clearPendingMedia } = useAppStore();
    const [uploadProgress, setUploadProgress] = useState(0);
    const { loading, error } = useLoadingState('uploadMedia');

    // Enhanced upload handler with direct upload support
    const handleUpload = useCallback(async (file, channelId = null) => {
        if (!file) return;

        // Validate file
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/webm', 'video/mov',
            'application/pdf', 'text/plain'
        ];

        if (file.size > maxSize) {
            throw new Error('File size must be less than 50MB');
        }

        if (!allowedTypes.includes(file.type)) {
            throw new Error('File type not supported');
        }

        setUploadProgress(0);
        
        // Use direct upload if channel specified, otherwise use regular upload
        if (channelId) {
            return uploadMediaDirect(file, channelId);
        } else {
            return uploadMedia(file);
        }
    }, [uploadMedia, uploadMediaDirect]);

    // Enhanced upload with progress tracking
    const handleUploadWithProgress = useCallback(async (file, channelId = null, onProgress = null) => {
        if (!file) return;

        try {
            const result = await handleUpload(file, channelId);
            
            // Update progress state if callback provided
            if (onProgress && pendingMedia.uploadProgress !== undefined) {
                setUploadProgress(pendingMedia.uploadProgress);
                onProgress(pendingMedia.uploadProgress);
            }
            
            return result;
        } catch (error) {
            setUploadProgress(0);
            throw error;
        }
    }, [handleUpload, pendingMedia.uploadProgress]);

    useEffect(() => {
        setUploadProgress(pendingMedia.uploadProgress || 0);
    }, [pendingMedia.uploadProgress]);

    return {
        handleUpload,
        handleUploadWithProgress,
        uploadProgress,
        pendingMedia,
        clearPendingMedia,
        loading,
        error,
        // Enhanced metadata
        uploadSpeed: pendingMedia.uploadSpeed || 0,
        uploadType: pendingMedia.uploadType || 'storage',
        metadata: pendingMedia.metadata || {}
    };
};

/**
 * Custom hook for Telegram Web App integration
 */
export const useTelegramWebApp = () => {
    const [webApp, setWebApp] = useState(null);
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        const tg = window.Telegram?.WebApp;
        
        if (tg) {
            // Initialize Telegram Web App
            tg.ready();
            tg.expand();
            
            // Set theme
            if (tg.colorScheme === 'dark') {
                document.body.setAttribute('data-theme', 'dark');
            }
            
            setWebApp(tg);
            setIsReady(true);
        } else {
            console.warn('Telegram Web App not available');
        }
    }, []);

    const showAlert = useCallback((message) => {
        if (webApp) {
            webApp.showAlert(message);
        } else {
            alert(message);
        }
    }, [webApp]);

    const showConfirm = useCallback((message) => {
        return new Promise((resolve) => {
            if (webApp) {
                webApp.showConfirm(message, resolve);
            } else {
                resolve(confirm(message));
            }
        });
    }, [webApp]);

    const hapticFeedback = useCallback((type = 'impact') => {
        if (webApp?.HapticFeedback) {
            switch (type) {
                case 'light':
                    webApp.HapticFeedback.impactOccurred('light');
                    break;
                case 'medium':
                    webApp.HapticFeedback.impactOccurred('medium');
                    break;
                case 'heavy':
                    webApp.HapticFeedback.impactOccurred('heavy');
                    break;
                case 'success':
                    webApp.HapticFeedback.notificationOccurred('success');
                    break;
                case 'error':
                    webApp.HapticFeedback.notificationOccurred('error');
                    break;
                default:
                    webApp.HapticFeedback.impactOccurred('medium');
            }
        }
    }, [webApp]);

    return {
        webApp,
        isReady,
        showAlert,
        showConfirm,
        hapticFeedback,
        user: webApp?.initDataUnsafe?.user,
        theme: webApp?.colorScheme || 'light'
    };
};
