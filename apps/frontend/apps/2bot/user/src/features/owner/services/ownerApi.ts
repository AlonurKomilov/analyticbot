/**
 * Owner API Service
 *
 * API client for owner-only features including database backup management.
 * All endpoints require owner role authentication.
 *
 * Access: OWNER ROLE ONLY (Level 4)
 */

import type {
  BackupInfo,
  BackupListResponse,
  BackupOperationResult,
  BackupVerificationResult,
  DatabaseStats,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Get authorization headers with token
 */
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

/**
 * Handle API response
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.detail || error.message || 'Request failed');
  }
  return response.json();
}

/**
 * Database Backup Management API
 */
export const ownerApi = {
  /**
   * Get current database statistics
   * GET /owner/database/stats
   */
  async getDatabaseStats(): Promise<DatabaseStats> {
    const response = await fetch(`${API_BASE_URL}/owner/database/stats`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    return handleResponse<DatabaseStats>(response);
  },

  /**
   * List all available backups
   * GET /owner/database/backups
   */
  async listBackups(): Promise<BackupListResponse> {
    const response = await fetch(`${API_BASE_URL}/owner/database/backups`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    return handleResponse<BackupListResponse>(response);
  },

  /**
   * Create a new database backup
   * POST /owner/database/backup
   */
  async createBackup(): Promise<BackupOperationResult> {
    const response = await fetch(`${API_BASE_URL}/owner/database/backup`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return handleResponse<BackupOperationResult>(response);
  },

  /**
   * Verify a backup file's integrity
   * POST /owner/database/verify/{filename}
   */
  async verifyBackup(filename: string): Promise<BackupVerificationResult> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/verify/${encodeURIComponent(filename)}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<BackupVerificationResult>(response);
  },

  /**
   * Get detailed information about a specific backup
   * GET /owner/database/backups/{filename}
   */
  async getBackupInfo(filename: string): Promise<BackupInfo> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/backups/${encodeURIComponent(filename)}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<BackupInfo>(response);
  },

  /**
   * Delete a backup file
   * DELETE /owner/database/backups/{filename}?confirmation=DELETE
   */
  async deleteBackup(filename: string): Promise<BackupOperationResult> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/backups/${encodeURIComponent(
        filename
      )}?confirmation=DELETE`,
      {
        method: 'DELETE',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<BackupOperationResult>(response);
  },

  /**
   * Get query performance statistics
   * GET /owner/database/query-performance
   */
  async getQueryPerformance(limit: number = 20, minCalls: number = 1): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/query-performance?limit=${limit}&min_calls=${minCalls}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Get slow queries exceeding threshold
   * GET /owner/database/slow-queries
   */
  async getSlowQueries(thresholdMs: number = 100, limit: number = 20): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/slow-queries?threshold_ms=${thresholdMs}&limit=${limit}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Get query statistics summary
   * GET /owner/database/query-stats-summary
   */
  async getQueryStatsSummary(): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/query-stats-summary`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Reset query statistics
   * POST /owner/database/reset-query-stats
   */
  async resetQueryStats(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/reset-query-stats`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Get VACUUM status and table health
   * GET /owner/database/vacuum-status
   */
  async getVacuumStatus(): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/vacuum-status`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Get autovacuum configuration
   * GET /owner/database/autovacuum-config
   */
  async getAutovacuumConfig(): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/autovacuum-config`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Manually trigger VACUUM on a table
   * POST /owner/database/vacuum-table
   */
  async manualVacuumTable(
    tableName: string,
    analyze: boolean = true,
    full: boolean = false
  ): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/vacuum-table?table_name=${encodeURIComponent(
        tableName
      )}&analyze=${analyze}&full=${full}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },

  /**
   * Get tables needing VACUUM attention
   * GET /owner/database/tables-needing-vacuum
   */
  async getTablesNeedingVacuum(
    deadPercentThreshold: number = 5,
    minDeadTuples: number = 100
  ): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/owner/database/tables-needing-vacuum?dead_percent_threshold=${deadPercentThreshold}&min_dead_tuples=${minDeadTuples}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );
    return handleResponse(response);
  },
};

export default ownerApi;
