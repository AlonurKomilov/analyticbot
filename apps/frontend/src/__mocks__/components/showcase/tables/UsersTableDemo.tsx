/**
 * UsersTableDemo Component
 *
 * Extracted from DataTablesShowcase - showcases the Enhanced User Management Table
 * with user administration features and bulk operations
 */

import React, { useState, useMemo } from 'react';
import { Box, Typography } from '@mui/material';
import EnhancedUserManagementTable from '@/components/EnhancedUserManagementTable';

interface User {
    id: number;
    telegram_id: string;
    username: string | null;
    full_name: string;
    email?: string;
    phone?: string;
    status: 'active' | 'inactive' | 'suspended';
    subscription_tier: 'free' | 'premium';
    total_channels: number;
    total_posts: number;
    email_verified: boolean;
    phone_verified: boolean;
    is_premium: boolean;
    last_active: Date;
    created_at: Date;
    avatar_url?: string;
}

const UsersTableDemo: React.FC = () => {
    const [usersLoading, setUsersLoading] = useState<boolean>(false);

    // Mock user data for demonstration
    const mockUsers = useMemo<User[]>(() => [
        {
            id: 1,
            telegram_id: '12345678',
            username: 'john_doe',
            full_name: 'John Doe',
            email: 'john@example.com',
            phone: '+1234567890',
            status: 'active',
            subscription_tier: 'premium',
            total_channels: 5,
            total_posts: 142,
            email_verified: true,
            phone_verified: true,
            is_premium: true,
            last_active: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
            created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
            avatar_url: 'https://i.pravatar.cc/150?img=1'
        },
        {
            id: 2,
            telegram_id: '87654321',
            username: 'jane_smith',
            full_name: 'Jane Smith',
            email: 'jane@example.com',
            status: 'active',
            subscription_tier: 'free',
            total_channels: 2,
            total_posts: 58,
            email_verified: true,
            phone_verified: false,
            is_premium: false,
            last_active: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
            created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000), // 15 days ago
            avatar_url: 'https://i.pravatar.cc/150?img=2'
        },
        {
            id: 3,
            telegram_id: '11223344',
            username: 'mike_wilson',
            full_name: 'Mike Wilson',
            email: 'mike@example.com',
            status: 'suspended',
            subscription_tier: 'free',
            total_channels: 1,
            total_posts: 12,
            email_verified: false,
            phone_verified: false,
            is_premium: false,
            last_active: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 1 week ago
            created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000), // 60 days ago
            avatar_url: 'https://i.pravatar.cc/150?img=3'
        },
        {
            id: 4,
            telegram_id: '44556677',
            username: null,
            full_name: 'Sarah Johnson',
            email: 'sarah@example.com',
            phone: '+9876543210',
            status: 'active',
            subscription_tier: 'premium',
            total_channels: 8,
            total_posts: 287,
            email_verified: true,
            phone_verified: true,
            is_premium: true,
            last_active: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
            created_at: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // 90 days ago
            avatar_url: 'https://i.pravatar.cc/150?img=4'
        },
        {
            id: 5,
            telegram_id: '99887766',
            username: 'alex_brown',
            full_name: 'Alex Brown',
            status: 'inactive',
            subscription_tier: 'free',
            total_channels: 0,
            total_posts: 3,
            email_verified: false,
            phone_verified: false,
            is_premium: false,
            last_active: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
            created_at: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000), // 120 days ago
            avatar_url: 'https://i.pravatar.cc/150?img=5'
        }
    ], []);

    // Event handlers
    const handleRefreshUsers = (): void => {
        setUsersLoading(true);
        // Simulate API call
        setTimeout(() => {
            setUsersLoading(false);
            console.log('Users refreshed');
        }, 1000);
    };

    const handleUserUpdate = (userId: number, updates: Partial<User>): void => {
        console.log('Update user:', userId, updates);
    };

    const handleUserDelete = (userId: number): void => {
        console.log('Delete user:', userId);
    };

    const handleBulkAction = (action: string, userIds: number[]): void => {
        console.log('Bulk action:', action, userIds);
    };

    return (
        <>
            <Box sx={{ mb: 2 }}>
                <Typography variant="h5" gutterBottom>
                    Enhanced User Management Table
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Administrative interface for user management with bulk operations, role management,
                    and detailed user information. Includes suspension workflows and audit capabilities.
                </Typography>
            </Box>
            <EnhancedUserManagementTable
                users={mockUsers as any}
                loading={usersLoading}
                onRefresh={handleRefreshUsers}
                onUserUpdate={handleUserUpdate as any}
                onUserDelete={handleUserDelete as any}
                onBulkAction={handleBulkAction as any}
            />
        </>
    );
};

export default UsersTableDemo;
