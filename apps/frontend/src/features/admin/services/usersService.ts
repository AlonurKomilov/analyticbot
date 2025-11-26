/**
 * Admin Users Service
 *
 * User administration and management for admins.
 * Integrates with backend /admin/users/* endpoints.
 *
 * Features:
 * - User oversight and monitoring
 * - Suspend/unsuspend users
 * - View user analytics
 * - Manage user permissions
 * - Audit user activity
 */

import { apiClient } from '@/api/client';

export type UserRole = 'user' | 'admin' | 'superadmin' | 'moderator';

export interface AdminUserInfo {
    user_id: number;
    email: string;
    username?: string;  // Display username
    full_name?: string;
    telegram_username?: string;
    telegram_id?: string;
    role: UserRole;
    status: 'active' | 'suspended' | 'deleted';
    created_at: string;
    last_login: string;
    last_activity?: string;
    total_channels: number;
    channel_count?: number;  // Alias for total_channels
    is_suspended?: boolean;
    subscription_tier?: string;
    suspension_reason?: string;
}

export interface UserSuspendRequest {
    reason: string;
    duration_days?: number;
    notify_user?: boolean;
}

export interface UserAuditLog {
    action: string;
    admin_id: number;
    admin_email: string;
    admin_username?: string;
    timestamp: string;
    ip_address?: string;
    details: Record<string, any>;
}

export interface UserStatistics {
    total_users: number;
    active_users: number;
    suspended_users: number;
    new_today: number;
    new_this_week: number;
    total_logins_today: number;
    premium_users: number;
    total_channels?: number;
    total_posts?: number;
    total_views?: number;
    last_login?: string;
}

export interface UserActivitySummary {
    user_id: number;
    last_7_days: {
        logins: number;
        channels_accessed: number;
        reports_generated: number;
        api_calls: number;
    };
    lifetime: {
        total_logins: number;
        channels_created: number;
        total_api_calls: number;
    };
}

/**
 * Admin Users Service Class
 */
class AdminUsersService {
    private baseURL = '/admin/users';

    /**
     * Get all users (admin view)
     *
     * @param page - Page number
     * @param limit - Items per page
     * @param status - Filter by status
     * @param role - Filter by role
     * @returns Paginated user list
     */
    async getAllUsers(
        page: number = 1,
        limit: number = 50,
        status?: 'active' | 'suspended' | 'deleted',
        role?: 'user' | 'admin' | 'superadmin'
    ): Promise<{
        users: AdminUserInfo[];
        total: number;
        page: number;
        pages: number;
    }> {
        try {
            const response = await apiClient.get<{
                users: AdminUserInfo[];
                total: number;
                page: number;
                pages: number;
            }>(
                `${this.baseURL}/list`,
                {
                    params: { page, limit, status, role }
                }
            );
            return response;
        } catch (error) {
            console.error('Failed to get users:', error);
            throw error;
        }
    }

    /**
     * Get specific user details (admin view)
     *
     * @param userId - User ID
     * @returns Detailed user information
     */
    async getUserDetails(userId: number): Promise<AdminUserInfo> {
        try {
            const response = await apiClient.get<AdminUserInfo>(
                `${this.baseURL}/${userId}`
            );
            return response;
        } catch (error) {
            console.error('Failed to get user details:', error);
            throw error;
        }
    }

    /**
     * Suspend a user
     *
     * @param userId - User ID to suspend
     * @param reasonOrRequest - Suspension reason string or request object
     * @param days - Optional suspension duration in days
     * @returns Success message
     */
    async suspendUser(
        userId: number,
        reasonOrRequest: string | UserSuspendRequest,
        days?: number
    ): Promise<{ message: string; success: boolean }> {
        try {
            const request = typeof reasonOrRequest === 'string'
                ? { reason: reasonOrRequest, duration_days: days }
                : reasonOrRequest;

            const response = await apiClient.post<{ message: string; success: boolean }>(
                `${this.baseURL}/${userId}/suspend`,
                request
            );
            return response;
        } catch (error) {
            console.error('Failed to suspend user:', error);
            throw error;
        }
    }

    /**
     * Unsuspend a user
     *
     * @param userId - User ID to unsuspend
     * @returns Success message
     */
    async unsuspendUser(
        userId: number
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.post<{ message: string; success: boolean }>(
                `${this.baseURL}/${userId}/unsuspend`
            );
            return response;
        } catch (error) {
            console.error('Failed to unsuspend user:', error);
            throw error;
        }
    }

    /**
     * Update user role
     *
     * @param userId - User ID
     * @param role - New role
     * @returns Success message
     */
    async updateUserRole(
        userId: number,
        role: UserRole
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.patch<{ message: string; success: boolean }>(
                `${this.baseURL}/${userId}/role`,
                { role }
            );
            return response;
        } catch (error) {
            console.error('Failed to update user role:', error);
            throw error;
        }
    }

    /**
     * Delete a user (admin only)
     *
     * @param userId - User ID to delete
     * @param reason - Deletion reason (optional)
     * @returns Success message
     */
    async deleteUser(
        userId: number,
        reason?: string
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.delete<{ message: string; success: boolean }>(
                `${this.baseURL}/${userId}`,
                {
                    data: { reason: reason || 'Admin deletion' }
                }
            );
            return response;
        } catch (error) {
            console.error('Failed to delete user:', error);
            throw error;
        }
    }

    /**
     * Get user audit log
     *
     * @param userId - User ID
     * @param limit - Number of entries
     * @returns Audit log entries
     */
    async getUserAuditLog(
        userId: number,
        limit: number = 100
    ): Promise<UserAuditLog[]> {
        try {
            const response = await apiClient.get<UserAuditLog[]>(
                `${this.baseURL}/${userId}/audit`,
                { params: { limit } }
            );
            return response;
        } catch (error) {
            console.error('Failed to get audit log:', error);
            throw error;
        }
    }

    /**
     * Get user statistics (admin overview)
     *
     * @param userId - Optional user ID for specific user stats
     * @returns User statistics
     */
    async getUserStatistics(userId?: number): Promise<UserStatistics> {
        try {
            const url = userId
                ? `${this.baseURL}/${userId}/statistics`
                : `${this.baseURL}/statistics`;
            const response = await apiClient.get<UserStatistics>(url);
            return response;
        } catch (error) {
            console.error('Failed to get user statistics:', error);
            throw error;
        }
    }

    /**
     * Get user activity summary
     *
     * @param userId - User ID
     * @returns Activity summary
     */
    async getUserActivity(userId: number): Promise<UserActivitySummary> {
        try {
            const response = await apiClient.get<UserActivitySummary>(
                `${this.baseURL}/${userId}/activity`
            );
            return response;
        } catch (error) {
            console.error('Failed to get user activity:', error);
            throw error;
        }
    }

    /**
     * Search users by keyword
     *
     * @param query - Search query (email, name, username)
     * @param limit - Max results
     * @returns Matching users
     */
    async searchUsers(
        query: string,
        limit: number = 20
    ): Promise<AdminUserInfo[]> {
        try {
            const response = await apiClient.get<AdminUserInfo[]>(
                `${this.baseURL}/search`,
                { params: { q: query, limit } }
            );
            return response;
        } catch (error) {
            console.error('Failed to search users:', error);
            throw error;
        }
    }

    /**
     * Send notification to user
     *
     * @param userId - User ID
     * @param message - Notification message
     * @param type - Notification type
     * @returns Success message
     */
    async sendNotification(
        userId: number,
        message: string,
        type: 'info' | 'warning' | 'alert' = 'info'
    ): Promise<{ message: string; success: boolean }> {
        try {
            const response = await apiClient.post<{ message: string; success: boolean }>(
                `${this.baseURL}/${userId}/notify`,
                { message, type }
            );
            return response;
        } catch (error) {
            console.error('Failed to send notification:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const adminUsersService = new AdminUsersService();
export default adminUsersService;
