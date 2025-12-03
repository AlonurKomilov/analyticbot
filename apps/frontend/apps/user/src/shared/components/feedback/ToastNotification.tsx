import React, { useState, useEffect } from 'react';
import {
    Snackbar,
    Alert,
    Slide,
    IconButton,
    Box,
    Typography,
    SlideProps,
    AlertColor
} from '@mui/material';
import {
    CheckCircle as SuccessIcon,
    Error as ErrorIcon,
    Warning as WarningIcon,
    Info as InfoIcon,
    Close as CloseIcon
} from '@mui/icons-material';

const SlideTransition = (props: SlideProps) => <Slide {...props} direction="up" />;

/**
 * Accessible toast notification component with enhanced UX
 *
 * @component
 * @example
 * ```tsx
 * <ToastNotification
 *   open={true}
 *   message="Operation successful!"
 *   severity="success"
 *   onClose={() => setOpen(false)}
 * />
 * ```
 */
export interface ToastNotificationProps {
  /** Whether toast is visible */
  open?: boolean;
  /** Close handler */
  onClose?: (event: React.SyntheticEvent | Event, reason?: string) => void;
  /** Main message text */
  message: string;
  /** Optional title */
  title?: string;
  /** Notification type */
  severity?: AlertColor;
  /** Auto close time (ms) */
  autoHideDuration?: number;
  /** Optional action text */
  action?: React.ReactNode;
  /** Action click handler */
  onAction?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Don't auto-hide */
  persistent?: boolean;
}

const ToastNotification: React.FC<ToastNotificationProps> = ({
    open = false,
    onClose,
    message,
    title,
    severity = 'success',
    autoHideDuration = 6000,
    action,
    onAction,
    persistent = false
}) => {
    const [isVisible, setIsVisible] = useState(open);

    useEffect(() => {
        setIsVisible(open);
    }, [open]);

    const handleClose = (event: React.SyntheticEvent | Event, reason?: string): void => {
        if (reason === 'clickaway' && persistent) {
            return;
        }
        setIsVisible(false);
        if (onClose) {
            onClose(event, reason);
        }
    };

    const getIcon = (): React.ReactElement => {
        const iconProps = { fontSize: 'inherit' as const, 'aria-hidden': true };
        switch (severity) {
            case 'success':
                return <SuccessIcon {...iconProps} />;
            case 'error':
                return <ErrorIcon {...iconProps} />;
            case 'warning':
                return <WarningIcon {...iconProps} />;
            case 'info':
                return <InfoIcon {...iconProps} />;
            default:
                return <InfoIcon {...iconProps} />;
        }
    };

    const actionButton = action && onAction ? (
        <IconButton
            size="small"
            aria-label={`${action} notification`}
            color="inherit"
            onClick={(e) => {
                onAction(e);
                handleClose(e, 'action');
            }}
            sx={{
                '&:focus-visible': {
                    outline: '2px solid #ffffff',
                    outlineOffset: '2px'
                }
            }}
        >
            {action}
        </IconButton>
    ) : null;

    const closeButton = (
        <IconButton
            size="small"
            aria-label="Close notification"
            color="inherit"
            onClick={handleClose}
            sx={{
                '&:focus-visible': {
                    outline: '2px solid #ffffff',
                    outlineOffset: '2px'
                }
            }}
        >
            <CloseIcon fontSize="small" aria-hidden="true" />
        </IconButton>
    );

    return (
        <Snackbar
            open={isVisible}
            autoHideDuration={persistent ? null : autoHideDuration}
            onClose={handleClose}
            TransitionComponent={SlideTransition}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            sx={{
                '& .MuiSnackbar-root': {
                    maxWidth: '500px'
                }
            }}
        >
            <Alert
                onClose={handleClose}
                severity={severity}
                variant="filled"
                icon={getIcon()}
                action={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {actionButton}
                        {closeButton}
                    </Box>
                }
                sx={{
                    width: '100%',
                    alignItems: 'flex-start',
                    '& .MuiAlert-icon': {
                        alignSelf: 'center',
                        marginTop: 0,
                    },
                    '& .MuiAlert-message': {
                        padding: 0,
                        paddingTop: '2px'
                    }
                }}
                role="alert"
                aria-live="assertive"
                aria-atomic="true"
            >
                {title && (
                    <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 0.5 }}>
                        {title}
                    </Typography>
                )}
                <Typography variant="body2">
                    {message}
                </Typography>
            </Alert>
        </Snackbar>
    );
};

/**
 * Hook for managing toast notifications
 *
 * @example
 * ```tsx
 * const { showSuccess, showError } = useToast();
 * showSuccess('Saved successfully!');
 * ```
 */
export interface Toast extends ToastNotificationProps {
  id: number;
}

export const useToast = () => {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const showToast = (options: Omit<Toast, 'id' | 'open'>): number => {
        const id = Date.now() + Math.random();
        const toast = {
            id,
            open: true,
            ...options
        };

        setToasts(prev => [...prev, toast]);

        // Auto-remove after duration
        if (!options.persistent) {
            setTimeout(() => {
                removeToast(id);
            }, options.autoHideDuration || 6000);
        }

        return id;
    };

    const removeToast = (id: number): void => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    };

    const showSuccess = (message: string, options: Partial<ToastNotificationProps> = {}) =>
        showToast({ message, severity: 'success', ...options });

    const showError = (message: string, options: Partial<ToastNotificationProps> = {}) =>
        showToast({ message, severity: 'error', ...options });

    const showWarning = (message: string, options: Partial<ToastNotificationProps> = {}) =>
        showToast({ message, severity: 'warning', ...options });

    const showInfo = (message: string, options: Partial<ToastNotificationProps> = {}) =>
        showToast({ message, severity: 'info', ...options });

    return {
        toasts,
        showToast,
        showSuccess,
        showError,
        showWarning,
        showInfo,
        removeToast
    };
};

/**
 * Toast container component to render all active toasts
 */
export const ToastContainer = () => {
    const { toasts, removeToast } = useToast();

    return (
        <>
            {toasts.map((toast) => (
                <ToastNotification
                    key={toast.id}
                    {...toast}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </>
    );
};

export default ToastNotification;
