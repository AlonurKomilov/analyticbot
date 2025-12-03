/**
 * Accessibility testing utilities and configuration
 * This file provides helpers for automated accessibility testing
 */

// ESLint configuration for accessibility
export const eslintA11yRules = {
    "extends": ["plugin:jsx-a11y/recommended"],
    "plugins": ["jsx-a11y"],
    "rules": {
        // Enforce alt text on img elements
        "jsx-a11y/alt-text": "error",

        // Enforce ARIA attributes are valid
        "jsx-a11y/aria-props": "error",
        "jsx-a11y/aria-proptypes": "error",
        "jsx-a11y/aria-unsupported-elements": "error",

        // Enforce form controls have labels
        "jsx-a11y/label-has-associated-control": "error",

        // Enforce onclick is paired with onKeyDown/onKeyUp
        "jsx-a11y/click-events-have-key-events": "error",

        // Enforce semantic HTML
        "jsx-a11y/no-redundant-roles": "error",
        "jsx-a11y/role-has-required-aria-props": "error",

        // Enforce focus management
        "jsx-a11y/no-autofocus": "warn",
        "jsx-a11y/tabindex-no-positive": "error",

        // Enforce heading hierarchy
        "jsx-a11y/heading-has-content": "error",

        // Enforce interactive elements
        "jsx-a11y/interactive-supports-focus": "error",
        "jsx-a11y/no-noninteractive-element-interactions": "error"
    }
} as const;

// Axe-core configuration for automated testing
export const axeConfig = {
    rules: {
        // Color contrast checking
        'color-contrast': { enabled: true },
        'color-contrast-enhanced': { enabled: true },

        // Focus management
        'focus-order-semantics': { enabled: true },
        'focusable-element': { enabled: true },

        // Form accessibility
        'label': { enabled: true },
        'label-title-only': { enabled: true },
        'form-field-multiple-labels': { enabled: true },

        // Semantic HTML
        'landmark-one-main': { enabled: true },
        'landmark-complementary-is-top-level': { enabled: true },
        'page-has-heading-one': { enabled: true },

        // ARIA usage
        'aria-valid-attr': { enabled: true },
        'aria-valid-attr-value': { enabled: true },
        'aria-required-attr': { enabled: true },

        // Images
        'image-alt': { enabled: true },
        'image-redundant-alt': { enabled: true },

        // Tables
        'table-fake-caption': { enabled: true },
        'td-headers-attr': { enabled: true },
        'th-has-data-cells': { enabled: true },

        // Links and buttons
        'link-name': { enabled: true },
        'button-name': { enabled: true }
    },
    tags: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice']
} as const;

// Manual testing checklist
export const manualTestingChecklist = {
    keyboard: [
        'All interactive elements are keyboard accessible',
        'Tab order follows logical sequence',
        'Focus indicators are clearly visible',
        'No keyboard traps exist',
        'Skip links work correctly',
        'Modal dialogs trap focus appropriately',
        'Dropdown menus can be navigated with arrow keys',
        'Form submission works with Enter key'
    ],

    screenReader: [
        'All content is announced correctly',
        'Headings create logical document structure',
        'Form labels are associated properly',
        'Error messages are announced',
        'Live regions announce dynamic changes',
        'Images have appropriate alt text',
        'Tables have proper headers and captions',
        'ARIA labels provide context where needed'
    ],

    visual: [
        'Text meets WCAG contrast requirements (4.5:1)',
        'Focus indicators are clearly visible',
        'Text remains readable when zoomed to 200%',
        'Content reflows properly on mobile devices',
        'No information is conveyed by color alone',
        'Interactive elements are minimum 44px touch targets',
        'Loading states provide visual feedback',
        'Error states are clearly indicated'
    ],

    cognitive: [
        'Error messages are clear and actionable',
        'Form instructions are provided',
        'Complex interactions have help text',
        'Users can undo destructive actions',
        'Session timeouts are announced',
        'Page titles describe the content',
        'Navigation is consistent across pages',
        'Content is organized logically'
    ]
} as const;

// Testing tools recommendations
export const testingTools = {
    automated: [
        'axe DevTools - Browser extension for automated testing',
        'Lighthouse - Built into Chrome DevTools',
        'WAVE - Web accessibility evaluation tool',
        'Pa11y - Command line accessibility testing',
        'jest-axe - Integration with Jest testing framework'
    ],

    manual: [
        'NVDA - Free screen reader for Windows',
        'JAWS - Popular commercial screen reader',
        'VoiceOver - Built-in Mac/iOS screen reader',
        'ChromeVox - Chrome extension screen reader',
        'Keyboard-only navigation testing',
        'Color Contrast Analyzer - Desktop tool',
        'Browser zoom testing (up to 400%)',
        'Mobile device testing'
    ],

    userTesting: [
        'Test with actual users who use assistive technology',
        'Include users with various disabilities',
        'Test on different devices and operating systems',
        'Observe real usage patterns and pain points',
        'Gather feedback on clarity and usability'
    ]
} as const;

// Performance testing for accessibility features
export const performanceChecklist = [
    'Focus management doesn\'t cause layout thrashing',
    'ARIA live regions don\'t update too frequently',
    'Screen reader announcements don\'t queue up',
    'Keyboard navigation is responsive',
    'Focus indicators animate smoothly',
    'Loading states don\'t interfere with assistive technology',
    'Large datasets are paginated or virtualized',
    'Images have appropriate loading strategies'
] as const;

interface BrowserSupportInfo {
    'ARIA support': string;
    'Focus management': string;
    'Screen reader compat': string;
    'Keyboard navigation': string;
}

// Browser support matrix for accessibility features
export const browserSupport: Record<string, BrowserSupportInfo> = {
    'Chrome': {
        'ARIA support': 'Excellent',
        'Focus management': 'Excellent',
        'Screen reader compat': 'Good with NVDA/JAWS',
        'Keyboard navigation': 'Excellent'
    },
    'Firefox': {
        'ARIA support': 'Excellent',
        'Focus management': 'Excellent',
        'Screen reader compat': 'Excellent with NVDA',
        'Keyboard navigation': 'Excellent'
    },
    'Safari': {
        'ARIA support': 'Good',
        'Focus management': 'Good',
        'Screen reader compat': 'Excellent with VoiceOver',
        'Keyboard navigation': 'Good'
    },
    'Edge': {
        'ARIA support': 'Excellent',
        'Focus management': 'Excellent',
        'Screen reader compat': 'Good with JAWS/NVDA',
        'Keyboard navigation': 'Excellent'
    }
};

export default {
    eslintA11yRules,
    axeConfig,
    manualTestingChecklist,
    testingTools,
    performanceChecklist,
    browserSupport
};
