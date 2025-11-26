/**
 * Owner Feature - Types
 *
 * Type definitions for owner-only features including database backup management.
 * Access: OWNER ROLE ONLY (Level 4)
 */

/**
 * Database backup information
 */
export interface BackupInfo {
  filename: string;
  size_bytes: number;
  size_human: string;
  created_at: string;
  age_days: number;
  database_name: string;
  database_size?: string;
  checksum?: string;
  verified: boolean;
}

/**
 * Database statistics
 */
export interface DatabaseStats {
  database_name: string;
  size_bytes: number;
  size_human: string;
  table_count: number;
  total_records: number;
  backup_count: number;
  last_backup?: {
    filename: string;
    size: string;
    created_at: string;
    age_days: number;
  };
}

/**
 * Backup operation result
 */
export interface BackupOperationResult {
  success: boolean;
  message: string;
  backup?: {
    filename: string;
    size: string;
    created_at: string;
  };
  error?: string;
  output?: string;
}

/**
 * Backup verification result
 */
export interface BackupVerificationResult {
  success: boolean;
  verified: boolean;
  message: string;
  filename: string;
  error?: string;
  output?: string;
}

/**
 * Backup list response
 */
export interface BackupListResponse {
  count: number;
  backups: BackupInfo[];
}
