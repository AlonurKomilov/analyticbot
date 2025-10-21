/**
 * EnhancedDataTable - Compatibility wrapper for the refactored component
 *
 * REFACTORING COMPLETED: 799 lines -> 900 lines distributed across 13 modular files
 * - Improved maintainability with separated concerns
 * - Reusable hooks and utilities
 * - Individual component testing capability
 * - Clean import/export structure
 */

// Re-export everything from the modular implementation
export * from './EnhancedDataTable/index.js';

// Default export for backward compatibility
export { default } from './EnhancedDataTable/index.js';
