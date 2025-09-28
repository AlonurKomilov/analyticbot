/**
 * User-friendly error message mapping utility
 * Converts technical error messages to user-friendly ones
 */

export const ERROR_TYPES = {
    NETWORK_ERROR: 'NETWORK_ERROR',
    VALIDATION_ERROR: 'VALIDATION_ERROR',
    SERVER_ERROR: 'SERVER_ERROR',
    AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
    PERMISSION_ERROR: 'PERMISSION_ERROR',
    NOT_FOUND_ERROR: 'NOT_FOUND_ERROR',
    RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
    UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

const ERROR_MESSAGES = {
    [ERROR_TYPES.NETWORK_ERROR]: {
        title: 'Connection Problem',
        message: 'Unable to connect to our servers. Please check your internet connection and try again.',
        action: 'Check your connection and retry'
    },
    [ERROR_TYPES.VALIDATION_ERROR]: {
        title: 'Input Error',
        message: 'Please check your input and make sure all required fields are filled correctly.',
        action: 'Review your input and try again'
    },
    [ERROR_TYPES.SERVER_ERROR]: {
        title: 'Server Error',
        message: 'Our servers are experiencing issues. Please try again in a few moments.',
        action: 'Wait a moment and try again'
    },
    [ERROR_TYPES.AUTHENTICATION_ERROR]: {
        title: 'Authentication Required',
        message: 'You need to sign in to access this feature.',
        action: 'Please sign in and try again'
    },
    [ERROR_TYPES.PERMISSION_ERROR]: {
        title: 'Access Denied',
        message: 'You don\'t have permission to perform this action.',
        action: 'Contact an administrator if you need access'
    },
    [ERROR_TYPES.NOT_FOUND_ERROR]: {
        title: 'Not Found',
        message: 'The requested item could not be found.',
        action: 'Check the information and try again'
    },
    [ERROR_TYPES.RATE_LIMIT_ERROR]: {
        title: 'Too Many Requests',
        message: 'You\'re making requests too quickly. Please wait a moment before trying again.',
        action: 'Wait a moment and try again'
    },
    [ERROR_TYPES.UNKNOWN_ERROR]: {
        title: 'Unexpected Error',
        message: 'Something unexpected happened. Our team has been notified.',
        action: 'Please try again or contact support'
    }
};

/**
 * Categorizes an error based on its properties
 */
export const categorizeError = (error) => {
    if (!error) return ERROR_TYPES.UNKNOWN_ERROR;

    // Network errors
    if (error.name === 'NetworkError' || 
        error.message?.includes('fetch') || 
        error.message?.includes('network') ||
        !navigator.onLine) {
        return ERROR_TYPES.NETWORK_ERROR;
    }

    // HTTP status codes
    if (error.response?.status) {
        const status = error.response.status;
        switch (status) {
            case 400:
            case 422:
                return ERROR_TYPES.VALIDATION_ERROR;
            case 401:
                return ERROR_TYPES.AUTHENTICATION_ERROR;
            case 403:
                return ERROR_TYPES.PERMISSION_ERROR;
            case 404:
                return ERROR_TYPES.NOT_FOUND_ERROR;
            case 429:
                return ERROR_TYPES.RATE_LIMIT_ERROR;
            case 500:
            case 502:
            case 503:
            case 504:
                return ERROR_TYPES.SERVER_ERROR;
            default:
                return ERROR_TYPES.UNKNOWN_ERROR;
        }
    }

    // Validation errors
    if (error.name === 'ValidationError' || 
        error.message?.includes('validation') ||
        error.message?.includes('required') ||
        error.message?.includes('invalid')) {
        return ERROR_TYPES.VALIDATION_ERROR;
    }

    return ERROR_TYPES.UNKNOWN_ERROR;
};

/**
 * Gets user-friendly error information
 */
export const getUserFriendlyError = (error, customMessage = null) => {
    const errorType = categorizeError(error);
    const errorInfo = ERROR_MESSAGES[errorType];

    return {
        type: errorType,
        title: errorInfo.title,
        message: customMessage || errorInfo.message,
        action: errorInfo.action,
        originalError: error
    };
};

/**
 * Context-specific error messages for different operations
 */
export const CONTEXT_ERRORS = {
    'add-channel': {
        [ERROR_TYPES.VALIDATION_ERROR]: 'Please enter a valid channel username starting with @',
        [ERROR_TYPES.PERMISSION_ERROR]: 'Unable to access the channel. Make sure the bot is added as an admin.',
        [ERROR_TYPES.NOT_FOUND_ERROR]: 'Channel not found. Please check the username and try again.',
        [ERROR_TYPES.SERVER_ERROR]: 'Unable to add channel right now. Please try again later.'
    },
    'schedule-post': {
        [ERROR_TYPES.VALIDATION_ERROR]: 'Please fill in all required fields and check your input.',
        [ERROR_TYPES.PERMISSION_ERROR]: 'Unable to post to this channel. Check your permissions.',
        [ERROR_TYPES.SERVER_ERROR]: 'Unable to schedule post right now. Please try again later.'
    },
    'upload-media': {
        [ERROR_TYPES.VALIDATION_ERROR]: 'Please select a valid image or video file.',
        [ERROR_TYPES.SERVER_ERROR]: 'Unable to upload media right now. Please try again later.',
        [ERROR_TYPES.RATE_LIMIT_ERROR]: 'Upload limit reached. Please wait before uploading more files.'
    },
    'load-analytics': {
        [ERROR_TYPES.NETWORK_ERROR]: 'Unable to load analytics data. Check your connection.',
        [ERROR_TYPES.SERVER_ERROR]: 'Analytics service is temporarily unavailable.',
        [ERROR_TYPES.NOT_FOUND_ERROR]: 'No analytics data available for the selected period.'
    }
};

/**
 * Gets context-specific error message
 */
export const getContextualError = (error, context) => {
    const errorType = categorizeError(error);
    const contextMessages = CONTEXT_ERRORS[context];
    
    if (contextMessages && contextMessages[errorType]) {
        return {
            ...getUserFriendlyError(error),
            message: contextMessages[errorType]
        };
    }
    
    return getUserFriendlyError(error);
};

/**
 * Formats error for display in UI components
 */
export const formatErrorForDisplay = (error, context = null) => {
    const errorInfo = context 
        ? getContextualError(error, context)
        : getUserFriendlyError(error);

    return {
        severity: errorInfo.type === ERROR_TYPES.VALIDATION_ERROR ? 'warning' : 'error',
        title: errorInfo.title,
        message: errorInfo.message,
        action: errorInfo.action,
        canRetry: [
            ERROR_TYPES.NETWORK_ERROR,
            ERROR_TYPES.SERVER_ERROR,
            ERROR_TYPES.RATE_LIMIT_ERROR
        ].includes(errorInfo.type)
    };
};

export default {
    ERROR_TYPES,
    categorizeError,
    getUserFriendlyError,
    getContextualError,
    formatErrorForDisplay
};
