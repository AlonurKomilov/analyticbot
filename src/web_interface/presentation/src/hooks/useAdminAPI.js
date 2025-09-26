import { useState, useCallback } from 'react';

/**
 * Admin API Hook
 * Unified data layer for admin operations
 */
export const useAdminAPI = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Generic API call wrapper with admin authentication
    const apiCall = useCallback(async (endpoint, options = {}) => {
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
            setError(err.message);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Specific admin operations
    const fetchStats = useCallback(async () => {
        return await apiCall('stats');
    }, [apiCall]);

    const fetchUsers = useCallback(async (limit = 100) => {
        return await apiCall(`users?limit=${limit}`);
    }, [apiCall]);

    const fetchAuditLogs = useCallback(async (limit = 50) => {
        return await apiCall(`audit-logs?limit=${limit}`);
    }, [apiCall]);

    const suspendUser = useCallback(async (userId, reason) => {
        return await apiCall(`users/${userId}/suspend`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }, [apiCall]);

    const reactivateUser = useCallback(async (userId) => {
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
 * Admin Dashboard Hook
 * Complete data management for admin dashboard
 */
export const useAdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [auditLogs, setAuditLogs] = useState([]);
    
    const adminAPI = useAdminAPI();

    const fetchDashboardData = useCallback(async () => {
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