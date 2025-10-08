/**
 * Production Constants
 * Default values for production application
 */

// Default channel for new users or when no channel is selected
export const DEFAULT_CHANNEL_ID = 'default_channel';

// Default user settings
export const DEFAULT_USER_SETTINGS = {
    max_channels: 3,
    plan: 'free',
    username: 'user',
    first_name: 'User'
};

// Default fallback values
export const FALLBACK_VALUES = {
    CHANNEL_ID: DEFAULT_CHANNEL_ID,
    USER: DEFAULT_USER_SETTINGS
};

export default {
    DEFAULT_CHANNEL_ID,
    DEFAULT_USER_SETTINGS,
    FALLBACK_VALUES
};
