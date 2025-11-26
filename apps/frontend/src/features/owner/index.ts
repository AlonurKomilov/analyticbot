/**
 * Owner Feature - Public Exports
 *
 * Central export point for owner-only features.
 * Access: OWNER ROLE ONLY (Level 4)
 */

// Main Dashboard
export { default as OwnerDashboard } from './OwnerDashboard';

// Components
export { DatabaseStatsComponent } from './components/DatabaseStats';
export { DatabaseBackupComponent } from './components/DatabaseBackup';

// Services
export { ownerApi } from './services/ownerApi';

// Types
export type {
  BackupInfo,
  BackupListResponse,
  BackupOperationResult,
  BackupVerificationResult,
  DatabaseStats,
} from './types';
