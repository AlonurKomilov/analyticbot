/**
 * Bot Moderation Dashboard
 * Main component for managing moderation features
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Block as BlockIcon,
  Message as MessageIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Campaign as CampaignIcon,
  Group as GroupIcon,
} from '@mui/icons-material';

import { useModerationStore } from '@/store';
import { SettingsTab } from './SettingsTab';
import { BannedWordsTab } from './BannedWordsTab';
import { WelcomeMessagesTab } from './WelcomeMessagesTab';
import { InviteTrackingTab } from './InviteTrackingTab';
import { ModerationLogTab } from './ModerationLogTab';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`moderation-tabpanel-${index}`}
      aria-labelledby={`moderation-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const BotModerationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const {
    selectedChatId,
    configuredChats,
    error,
    isLoadingChats,
    isLoadingSettings,
    setSelectedChat,
    fetchConfiguredChats,
    clearError,
  } = useModerationStore();

  useEffect(() => {
    fetchConfiguredChats();
  }, []);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleChatSelect = (chatId: number) => {
    setSelectedChat(chatId);
  };

  if (isLoadingChats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Bot Bot Services
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
          {error}
        </Alert>
      )}

      {/* Chat Selector */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <FormControl sx={{ minWidth: 300, flexGrow: 1 }}>
            <InputLabel>Select Channel/Group</InputLabel>
            <Select
              value={selectedChatId || ''}
              label="Select Channel/Group"
              onChange={(e) => handleChatSelect(Number(e.target.value))}
            >
              {configuredChats.length === 0 && (
                <MenuItem disabled>
                  <em>No channels available. Add channels first.</em>
                </MenuItem>
              )}
              {configuredChats.map((chat) => (
                <MenuItem key={chat.chat_id} value={chat.chat_id}>
                  <Box display="flex" alignItems="center" gap={1} width="100%">
                    {chat.chat_type === 'channel' ? (
                      <CampaignIcon fontSize="small" color="primary" />
                    ) : (
                      <GroupIcon fontSize="small" color="secondary" />
                    )}
                    <Typography sx={{ flexGrow: 1 }}>
                      {chat.chat_title}
                    </Typography>
                    <Chip
                      label={chat.chat_type === 'channel' ? 'Channel' : 'Group'}
                      size="small"
                      color={chat.chat_type === 'channel' ? 'primary' : 'secondary'}
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                    {chat.settings_configured && (
                      <Chip label="✓" size="small" color="success" />
                    )}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {!selectedChatId && configuredChats.length > 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Select a channel or group to configure moderation settings.
          </Typography>
        )}
        
        {configuredChats.length === 0 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              You need to add channels to your account first. Go to the Channels page to add your Telegram channels.
            </Typography>
          </Alert>
        )}
      </Paper>

      {/* Tabs - only show when chat is selected */}
      {selectedChatId && (
        <>
          <Paper sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab icon={<SettingsIcon />} label="Settings" />
              <Tab icon={<BlockIcon />} label="Banned Words" />
              <Tab icon={<MessageIcon />} label="Welcome Messages" />
              <Tab icon={<PeopleIcon />} label="Invite Tracking" />
              <Tab icon={<HistoryIcon />} label="Moderation Log" />
            </Tabs>
          </Paper>

          {isLoadingSettings ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TabPanel value={activeTab} index={0}>
                <SettingsTab chatId={selectedChatId} />
              </TabPanel>
              <TabPanel value={activeTab} index={1}>
                <BannedWordsTab chatId={selectedChatId} />
              </TabPanel>
              <TabPanel value={activeTab} index={2}>
                <WelcomeMessagesTab chatId={selectedChatId} />
              </TabPanel>
              <TabPanel value={activeTab} index={3}>
                <InviteTrackingTab chatId={selectedChatId} />
              </TabPanel>
              <TabPanel value={activeTab} index={4}>
                <ModerationLogTab chatId={selectedChatId} />
              </TabPanel>
            </>
          )}
        </>
      )}
    </Box>
  );
};

export default BotModerationDashboard;
