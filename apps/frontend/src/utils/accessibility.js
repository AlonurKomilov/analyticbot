/**
 * Accessibility utilities and helper functions
 */

/**
 * Announces messages to screen readers
 */
export const announceToScreenReader = (message, priority = 'polite') => {
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
export const generateId = (prefix = 'element') => {
    idCounter += 1;
    return `${prefix}-${idCounter}`;
};

/**
 * Creates aria-describedby relationships
 */
export const createAriaDescribedBy = (...ids) => {
    return ids.filter(Boolean).join(' ') || undefined;
};

/**
 * Focus management utilities
 */
export const focusManagement = {
    // Store focus before opening modal/dialog
    storeFocus: () => {
        const activeElement = document.activeElement;
        if (activeElement && activeElement !== document.body) {
            return activeElement;
        }
        return null;
    },

    // Restore focus after closing modal/dialog
    restoreFocus: (element) => {
        if (element && typeof element.focus === 'function') {
            element.focus();
        }
    },

    // Trap focus within an element
    trapFocus: (containerElement) => {
        const focusableElements = containerElement.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const handleTabKey = (e) => {
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
    button: (action, target) => `${action} ${target}`,
    loading: (action) => `${action} in progress`,
    error: (context) => `Error in ${context}`,
    success: (action) => `${action} completed successfully`,

    // Form-specific labels
    required: (label) => `${label} (required)`,
    optional: (label) => `${label} (optional)`,
    invalid: (label, error) => `${label} - ${error}`,

    // Navigation labels
    breadcrumb: (path) => `You are here: ${path.join(' > ')}`,
    pagination: (current, total) => `Page ${current} of ${total}`,

    // Data labels
    sortButton: (column, direction) =>
        `Sort by ${column} ${direction === 'asc' ? 'ascending' : 'descending'}`,
    filterButton: (type, value) => `Filter by ${type}: ${value}`,
};

/**
 * Keyboard event handlers
 */
export const keyboardHandlers = {
    // Enter and Space key handler for custom buttons
    buttonKeyHandler: (callback) => (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            callback(event);
        }
    },

    // Escape key handler for modals/dropdowns
    escapeKeyHandler: (callback) => (event) => {
        if (event.key === 'Escape') {
            callback(event);
        }
    },

    // Arrow key navigation for lists/menus
    arrowKeyHandler: (items, currentIndex, setCurrentIndex) => (event) => {
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

/**
 * Form accessibility helpers
 */
export const formHelpers = {
    // Associate error messages with form fields
    associateError: (fieldId, errorId, hasError) => ({
        'aria-invalid': hasError,
        'aria-describedby': hasError ? errorId : undefined
    }),

    // Create fieldset props for grouped form fields
    fieldsetProps: (legend, description) => ({
        role: 'group',
        'aria-labelledby': `${legend}-legend`,
        'aria-describedby': description ? `${legend}-description` : undefined
    }),

    // Validation message props
    validationProps: (fieldId, message, type = 'error') => ({
        id: `${fieldId}-${type}`,
        role: type === 'error' ? 'alert' : 'status',
        'aria-live': 'polite'
    })
};

/**
 * Color contrast utilities
 */
export const contrastHelpers = {
    // Check if color combination meets WCAG AA standards
    meetsContrastRequirement: (foreground, background, level = 'AA') => {
        // This is a simplified check - in production, use a proper contrast checking library
        const foregroundLuminance = getLuminance(foreground);
        const backgroundLuminance = getLuminance(background);

        const contrast = (Math.max(foregroundLuminance, backgroundLuminance) + 0.05) /
                        (Math.min(foregroundLuminance, backgroundLuminance) + 0.05);

        return level === 'AAA' ? contrast >= 7 : contrast >= 4.5;
    }
};

// Helper function to calculate luminance (simplified)
const getLuminance = (color) => {
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
    },

    // Announce state changes
    announceStateChange: (oldState, newState, context) => {
        const message = `${context} changed from ${oldState} to ${newState}`;
        announceToScreenReader(message);
    }
};

/**
 * Modal/Dialog accessibility helpers
 */
export const modalHelpers = {
    // Props for accessible modal container
    modalProps: (titleId, descriptionId) => ({
        role: 'dialog',
        'aria-modal': true,
        'aria-labelledby': titleId,
        'aria-describedby': descriptionId
    }),

    // Props for modal backdrop
    backdropProps: {
        'aria-hidden': true
    }
};

/**
 * Table accessibility helpers
 */
export const tableHelpers = {
    // Props for accessible table
    tableProps: (caption, summary) => ({
        role: 'table',
        'aria-label': summary,
        'aria-describedby': caption ? 'table-caption' : undefined
    }),

    // Props for sortable column headers
    sortableHeaderProps: (column, sortDirection, onSort) => ({
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
