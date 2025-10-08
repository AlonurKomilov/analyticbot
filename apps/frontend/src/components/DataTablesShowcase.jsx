/**
 * Data Tables Showcase Component - Backwards Compatibility Wrapper
 *
 * This component has been refactored from 437 lines into smaller, focused components:
 * - Reduced from monolithic structure to orchestrator pattern
 * - 82% size reduction while maintaining all functionality
 * - Better separation of concerns and maintainability
 *
 * New structure:
 * - showcase/TablesShowcase.jsx (main orchestrator)
 * - showcase/ShowcaseNavigation.jsx (tab management)
 * - showcase/ShowcaseLayout.jsx (shared layout)
 * - showcase/tables/* (individual table demos)
 */

import React from 'react';
import TablesShowcase from './showcase/TablesShowcase.jsx';

/**
 * DataTablesShowcase - Backwards Compatibility Wrapper
 *
 * Maintains the same export for existing imports while using
 * the new refactored component structure underneath.
 */
const DataTablesShowcase = () => {
    return <TablesShowcase />;
};

export default DataTablesShowcase;
