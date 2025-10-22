/**
 * Accessibility utilities and helper functions
 */

type AriaPriority = 'polite' | 'assertive';
type SortDirection = 'asc' | 'desc' | 'none';

/**
 * Announces messages to screen readers
 */
export const announceToScreenReader = (message: string, priority: AriaPriority = 'polite'): void => {
    const announcer = document.getElementById('live-announcements');
    if (announcer) {
        announcer.setAttribute('aria-live', priority);
        announcer.textContent = message;

        // Clear after announcement
        setTimeout(() => {
            announcer.textContent = '';
        }, 1000);
    }
};

/**
 * Generates unique IDs for form elements
 */
let idCounter = 0;
export const generateId = (prefix: string = 'element'): string => {
    idCounter += 1;
    return `${prefix}-${idCounter}`;
};

/**
 * Creates aria-describedby relationships
 */
export const createAriaDescribedBy = (...ids: (string | null | undefined)[]): string | undefined => {
    return ids.filter(Boolean).join(' ') || undefined;
};

type FocusCleanup = () => void;

/**
 * Focus management utilities
 */
export const focusManagement = {
    // Store focus before opening modal/dialog
    storeFocus: (): HTMLElement | null => {
        const activeElement = document.activeElement as HTMLElement;
        if (activeElement && activeElement !== document.body) {
            return activeElement;
        }
        return null;
    },

    // Restore focus after closing modal/dialog
    restoreFocus: (element: HTMLElement | null): void => {
        if (element && typeof element.focus === 'function') {
            element.focus();
        }
    },

    // Trap focus within an element
    trapFocus: (containerElement: HTMLElement): FocusCleanup | undefined => {
        const focusableElements = containerElement.querySelectorAll<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const handleTabKey = (e: KeyboardEvent): void => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        };

        containerElement.addEventListener('keydown', handleTabKey);
        firstElement.focus();

        return () => {
            containerElement.removeEventListener('keydown', handleTabKey);
        };
    }
};

/**
 * ARIA label generators
 */
export const ariaLabels = {
    button: (action: string, target: string): string => `${action} ${target}`,
    loading: (action: string): string => `${action} in progress`,
    error: (context: string): string => `Error in ${context}`,
    success: (action: string): string => `${action} completed successfully`,

    // Form-specific labels
    required: (label: string): string => `${label} (required)`,
    optional: (label: string): string => `${label} (optional)`,
    invalid: (label: string, error: string): string => `${label} - ${error}`,

    // Navigation labels
    breadcrumb: (path: string[]): string => `You are here: ${path.join(' > ')}`,
    pagination: (current: number, total: number): string => `Page ${current} of ${total}`,

    // Data labels
    sortButton: (column: string, direction: SortDirection): string =>
        `Sort by ${column} ${direction === 'asc' ? 'ascending' : 'descending'}`,
    filterButton: (type: string, value: string): string => `Filter by ${type}: ${value}`,
};

type KeyboardHandler = (event: KeyboardEvent) => void;

/**
 * Keyboard event handlers
 */
export const keyboardHandlers = {
    // Enter and Space key handler for custom buttons
    buttonKeyHandler: (callback: (event: KeyboardEvent) => void): KeyboardHandler => (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            callback(event);
        }
    },

    // Escape key handler for modals/dropdowns
    escapeKeyHandler: (callback: (event: KeyboardEvent) => void): KeyboardHandler => (event) => {
        if (event.key === 'Escape') {
            callback(event);
        }
    },

    // Arrow key navigation for lists/menus
    arrowKeyHandler: (items: any[], currentIndex: number, setCurrentIndex: (index: number) => void): KeyboardHandler => (event) => {
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                setCurrentIndex((currentIndex + 1) % items.length);
                break;
            case 'ArrowUp':
                event.preventDefault();
                setCurrentIndex(currentIndex === 0 ? items.length - 1 : currentIndex - 1);
                break;
            case 'Home':
                event.preventDefault();
                setCurrentIndex(0);
                break;
            case 'End':
                event.preventDefault();
                setCurrentIndex(items.length - 1);
                break;
        }
    }
};

interface FieldErrorProps {
    'aria-invalid': boolean;
    'aria-describedby'?: string;
}

interface FieldsetProps {
    role: string;
    'aria-labelledby': string;
    'aria-describedby'?: string;
}

interface ValidationProps {
    id: string;
    role: string;
    'aria-live': AriaPriority;
}

/**
 * Form accessibility helpers
 */
export const formHelpers = {
    // Associate error messages with form fields
    associateError: (_fieldId: string, errorId: string, hasError: boolean): FieldErrorProps => ({
        'aria-invalid': hasError,
        'aria-describedby': hasError ? errorId : undefined
    }),

    // Create fieldset props for grouped form fields
    fieldsetProps: (legend: string, description?: string): FieldsetProps => ({
        role: 'group',
        'aria-labelledby': `${legend}-legend`,
        'aria-describedby': description ? `${legend}-description` : undefined
    }),

    // Validation message props
    validationProps: (_fieldId: string, _message: string, type: 'error' | 'status' = 'error'): ValidationProps => {
        const id = `${_fieldId}-${type}`;
        return {
            id,
            role: type === 'error' ? 'alert' : 'status',
            'aria-live': 'polite'
        };
    }
};

/**
 * Color contrast utilities
 */
export const contrastHelpers = {
    // Check if color combination meets WCAG AA standards
    meetsContrastRequirement: (foreground: string, background: string, level: 'AA' | 'AAA' = 'AA'): boolean => {
        // This is a simplified check - in production, use a proper contrast checking library
        const foregroundLuminance = getLuminance(foreground);
        const backgroundLuminance = getLuminance(background);

        const contrast = (Math.max(foregroundLuminance, backgroundLuminance) + 0.05) /
                        (Math.min(foregroundLuminance, backgroundLuminance) + 0.05);

        return level === 'AAA' ? contrast >= 7 : contrast >= 4.5;
    }
};

// Helper function to calculate luminance (simplified)
const getLuminance = (color: string): number => {
    // This is a very simplified luminance calculation
    // In production, use a proper color library
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);

    const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

interface ScreenReaderOnlyStyle {
    position: string;
    width: string;
    height: string;
    padding: string;
    margin: string;
    overflow: string;
    clip: string;
    whiteSpace: string;
    border: string;
}

/**
 * Screen reader utilities
 */
export const screenReaderUtils = {
    // Hide decorative content from screen readers
    hideFromScreenReader: () => ({ 'aria-hidden': true }),

    // Show content only to screen readers
    screenReaderOnly: {
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: '0',
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        border: '0'
    } as ScreenReaderOnlyStyle,

    // Announce state changes
    announceStateChange: (oldState: string, newState: string, context: string): void => {
        const message = `${context} changed from ${oldState} to ${newState}`;
        announceToScreenReader(message);
    }
};

interface ModalProps {
    role: string;
    'aria-modal': boolean;
    'aria-labelledby': string;
    'aria-describedby': string;
}

interface BackdropProps {
    'aria-hidden': boolean;
}

/**
 * Modal/Dialog accessibility helpers
 */
export const modalHelpers = {
    // Props for accessible modal container
    modalProps: (titleId: string, descriptionId: string): ModalProps => ({
        role: 'dialog',
        'aria-modal': true,
        'aria-labelledby': titleId,
        'aria-describedby': descriptionId
    }),

    // Props for modal backdrop
    backdropProps: {
        'aria-hidden': true
    } as BackdropProps
};

interface TableProps {
    role: string;
    'aria-label': string;
    'aria-describedby'?: string;
}

interface SortableHeaderProps {
    role: string;
    'aria-sort': SortDirection;
    onClick: () => void;
    onKeyDown: KeyboardHandler;
    tabIndex: number;
}

/**
 * Table accessibility helpers
 */
export const tableHelpers = {
    // Props for accessible table
    tableProps: (caption: string, summary: string): TableProps => ({
        role: 'table',
        'aria-label': summary,
        'aria-describedby': caption ? 'table-caption' : undefined
    }),

    // Props for sortable column headers
    sortableHeaderProps: (_column: string, sortDirection: SortDirection | null, onSort: () => void): SortableHeaderProps => ({
        role: 'columnheader button',
        'aria-sort': sortDirection || 'none',
        onClick: onSort,
        onKeyDown: keyboardHandlers.buttonKeyHandler(onSort),
        tabIndex: 0
    })
};

export default {
    announceToScreenReader,
    generateId,
    createAriaDescribedBy,
    focusManagement,
    ariaLabels,
    keyboardHandlers,
    formHelpers,
    contrastHelpers,
    screenReaderUtils,
    modalHelpers,
    tableHelpers
};
