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
};

export default ownerApi;
