/**
 * SuperAdminDashboard - Compatibility wrapper for the refactored component
 *
 * This file provides backward compatibility for existing imports while
 * the component has been refactored into a modular structure.
 *
 * The actual implementation is now in ./SuperAdminDashboard/ directory
 * with the following structure:
 * - SuperAdminDashboard.jsx: Main component (170 lines)
 * - components/: UI sub-components (8 files, ~350 lines total)
 * - hooks/: State management hooks (1 file, ~80 lines total)
 * - utils/: Utility functions (1 file, ~30 lines total)
 *
 * REFACTORING COMPLETED: 452 lines -> ~500 lines distributed across 12 modular files
 * - Improved maintainability with separated concerns
 * - Reusable tab components and state management
 * - Individual component testing capability
 * - Clean admin dashboard architecture
 */

// Re-export everything from the modular implementation
export * from './SuperAdminDashboard/index.js';

// Import and re-export the main component as default
import SuperAdminDashboardComponent from './SuperAdminDashboard/SuperAdminDashboard.tsx';
export default SuperAdminDashboardComponent;
