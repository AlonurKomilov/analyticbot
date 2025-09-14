import React, { useState } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText,
    Badge,
    Tooltip,
    Typography,
    Box
} from '@mui/material';
import {
    Notifications as NotificationsIcon,
    Circle as CircleIcon
} from '@mui/icons-material';
import { useNavigation } from '../../../../components/common/NavigationProvider';

/**
 * NotificationMenu Component
 * 
 * Handles notifications dropdown including:
 * - Notification badge with count
 * - Notification list display
 * - Priority-based styling
 * - Mark as read functionality
 * - Empty state handling
 */
const NotificationMenu = ({ className, ...props }) => {
    const { notifications = [], unreadCount = 0, markAsRead } = useNavigation();
    
    // Menu anchor state
    const [notificationsAnchor, setNotificationsAnchor] = useState(null);
    
    // Menu open/close handlers
    const handleMenuOpen = (event) => {
        setNotificationsAnchor(event.currentTarget);
    };
    
    const handleMenuClose = () => {
        setNotificationsAnchor(null);
    };
    
    // Notification click handler
    const handleNotificationClick = (notification, index) => {
        // Mark as read if not already read
        if (markAsRead && !notification.read) {
            markAsRead(index);
        }
        
        // Navigate to notification target if available
        if (notification.action && notification.action.type === 'navigate') {
            // TODO: Implement navigation logic
            console.log('Navigate to:', notification.action.target);
        }
        
        // Keep menu open for now - could close based on UX preference
    };
    
    // Get priority color for notification
    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'high':
                return 'error';
            case 'medium':
                return 'warning';
            case 'low':
                return 'info';
            default:
                return 'default';
        }
    };

    return (
        <>
            {/* Notifications Button */}
            <Tooltip title={`${unreadCount} notifications`} placement="bottom">
                <IconButton
                    onClick={handleMenuOpen}
                    className={className}
                    aria-label={`${unreadCount} notifications`}
                    {...props}
                >
                    <Badge badgeContent={unreadCount} color="error">
                        <NotificationsIcon />
                    </Badge>
                </IconButton>
            </Tooltip>

            {/* Notifications Menu */}
            <Menu
                anchorEl={notificationsAnchor}
                open={Boolean(notificationsAnchor)}
                onClose={handleMenuClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                PaperProps={{ 
                    sx: { 
                        minWidth: 320, 
                        maxWidth: 400,
                        maxHeight: 400,
                        mt: 1
                    } 
                }}
            >
                {/* Empty State */}
                {notifications.length === 0 ? (
                    <MenuItem disabled>
                        <Box sx={{ textAlign: 'center', py: 2, width: '100%' }}>
                            <NotificationsIcon 
                                sx={{ 
                                    fontSize: 48, 
                                    color: 'text.disabled',
                                    mb: 1 
                                }} 
                            />
                            <Typography variant="body2" color="text.secondary">
                                No notifications
                            </Typography>
                            <Typography variant="caption" color="text.disabled">
                                You're all caught up!
                            </Typography>
                        </Box>
                    </MenuItem>
                ) : (
                    /* Notification List */
                    notifications.map((notification, index) => (
                        <MenuItem 
                            key={notification.id || index}
                            onClick={() => handleNotificationClick(notification, index)}
                            sx={{
                                alignItems: 'flex-start',
                                py: 2,
                                borderBottom: index < notifications.length - 1 ? '1px solid' : 'none',
                                borderColor: 'divider',
                                backgroundColor: notification.read ? 'transparent' : 'action.hover'
                            }}
                        >
                            <ListItemIcon sx={{ mt: 0.5 }}>
                                <Badge 
                                    variant="dot" 
                                    color={getPriorityColor(notification.priority)}
                                    invisible={notification.read}
                                >
                                    <CircleIcon 
                                        sx={{ 
                                            fontSize: 12,
                                            color: notification.read ? 'text.disabled' : 'primary.main'
                                        }} 
                                    />
                                </Badge>
                            </ListItemIcon>
                            <ListItemText
                                primary={
                                    <Typography 
                                        variant="subtitle2" 
                                        sx={{ 
                                            fontWeight: notification.read ? 400 : 600,
                                            mb: 0.5 
                                        }}
                                    >
                                        {notification.title}
                                    </Typography>
                                }
                                secondary={
                                    <Box>
                                        <Typography 
                                            variant="body2" 
                                            color="text.secondary"
                                            sx={{ mb: 0.5 }}
                                        >
                                            {notification.message}
                                        </Typography>
                                        {notification.timestamp && (
                                            <Typography 
                                                variant="caption" 
                                                color="text.disabled"
                                            >
                                                {new Date(notification.timestamp).toLocaleTimeString()}
                                            </Typography>
                                        )}
                                    </Box>
                                }
                            />
                        </MenuItem>
                    ))
                )}
            </Menu>
        </>
    );
};

export default NotificationMenu;