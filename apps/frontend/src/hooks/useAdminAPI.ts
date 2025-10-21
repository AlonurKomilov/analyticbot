import { useState, useCallback } from 'react';

/**
 * Admin stats interface
 */
export interface AdminStats {
    totalUsers?: number;
    activeUsers?: number;
    systemHealth?: any;
    [key: string]: any;
}

/**
 * Admin user interface
 */
export interface AdminUser {
    id: number | string;
    username: string;
    email?: string;
    status?: string | 'active' | 'suspended';
    role?: string;
    // Component-expected properties
    subscription?: string;
    joinedDate?: string;
    [key: string]: any;
}

/**
 * Audit log interface
 */
export interface AuditLog {
    id: number | string;
    action: string;
    userId?: number | string;
    timestamp: string;
    details?: any;
    // Component-expected properties
    created_at?: string | Date;
    admin_username?: string;
    resource_type?: string;
    ip_address?: string;
    success?: boolean;
    [key: string]: any;
}

/**
 * API call options interface
 */
export interface APICallOptions extends RequestInit {
    headers?: Record<string, string>;
}

/**
 * Admin API return type
 */
export interface UseAdminAPIReturn {
    isLoading: boolean;
    error: string | null;
    setError: (error: string | null) => void;
    fetchStats: () => Promise<AdminStats>;
    fetchUsers: (limit?: number) => Promise<AdminUser[]>;
    fetchAuditLogs: (limit?: number) => Promise<AuditLog[]>;
    suspendUser: (userId: number | string, reason: string) => Promise<any>;
    reactivateUser: (userId: number | string) => Promise<any>;
}

/**
 * Admin API Hook
 * Unified data layer for admin operations
 */
export const useAdminAPI = (): UseAdminAPIReturn => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Generic API call wrapper with admin authentication
    const apiCall = useCallback(async (endpoint: string, options: APICallOptions = {}): Promise<any> => {
        setIsLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem('adminToken');
            const response = await fetch(`/api/v1/superadmin/${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API Error: ${response.status}`);
            }

            return await response.json();
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'API request failed';
            setError(errorMessage);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Specific admin operations
    const fetchStats = useCallback(async (): Promise<AdminStats> => {
        return (await apiCall('stats')) as AdminStats;
    }, [apiCall]);

    const fetchUsers = useCallback(async (limit: number = 100): Promise<AdminUser[]> => {
        return (await apiCall(`users?limit=${limit}`)) as AdminUser[];
    }, [apiCall]);

    const fetchAuditLogs = useCallback(async (limit: number = 50): Promise<AuditLog[]> => {
        return (await apiCall(`audit-logs?limit=${limit}`)) as AuditLog[];
    }, [apiCall]);

    const suspendUser = useCallback(async (userId: number | string, reason: string): Promise<any> => {
        return await apiCall(`users/${userId}/suspend`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }, [apiCall]);

    const reactivateUser = useCallback(async (userId: number | string): Promise<any> => {
        return await apiCall(`users/${userId}/reactivate`, {
            method: 'POST'
        });
    }, [apiCall]);

    return {
        isLoading,
        error,
        setError,
        fetchStats,
        fetchUsers,
        fetchAuditLogs,
        suspendUser,
        reactivateUser
    };
};

/**
 * Admin dashboard return type
 */
export interface UseAdminDashboardReturn {
    stats: AdminStats | null;
    users: AdminUser[];
    auditLogs: AuditLog[];
    isLoading: boolean;
    error: string | null;
    setError: (error: string | null) => void;
    fetchDashboardData: () => Promise<void>;
    suspendUser: (userId: number | string, reason: string) => Promise<any>;
    reactivateUser: (userId: number | string) => Promise<any>;
    refreshStats: () => Promise<void>;
    refreshUsers: () => Promise<void>;
    refreshAuditLogs: () => Promise<void>;
}

/**
 * Admin Dashboard Hook
 * Complete data management for admin dashboard
 */
export const useAdminDashboard = (): UseAdminDashboardReturn => {
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);

    const adminAPI = useAdminAPI();

    const fetchDashboardData = useCallback(async (): Promise<void> => {
        try {
            const [statsData, usersData, auditData] = await Promise.all([
                adminAPI.fetchStats(),
                adminAPI.fetchUsers(),
                adminAPI.fetchAuditLogs()
            ]);

            setStats(statsData);
            setUsers(usersData);
            setAuditLogs(auditData);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        }
    }, [adminAPI]);

    return {
        // Data
        stats,
        users,
        auditLogs,

        // Loading states
        isLoading: adminAPI.isLoading,
        error: adminAPI.error,
        setError: adminAPI.setError,

        // Actions
        fetchDashboardData,
        suspendUser: adminAPI.suspendUser,
        reactivateUser: adminAPI.reactivateUser,

        // Individual fetchers for refresh
        refreshStats: async () => {
            const data = await adminAPI.fetchStats();
            setStats(data);
        },
        refreshUsers: async () => {
            const data = await adminAPI.fetchUsers();
            setUsers(data);
        },
        refreshAuditLogs: async () => {
            const data = await adminAPI.fetchAuditLogs();
            setAuditLogs(data);
        }
    };
};
