/**
 * Welcome Messages Configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  EmojiPeople as WaveIcon,
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Image as ImageIcon,
  Keyboard as ButtonIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface WelcomeSettings {
  welcome_enabled: boolean;
  welcome_delete_after: number;
}

interface WelcomeMessage {
  id: number;
  message_text: string;
  media_url: string | null;
  buttons: any[];
  is_active: boolean;
  created_at: string;
}

interface Props {
  chatId: number;
}

export const WelcomeMessagesConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<WelcomeSettings>({
    welcome_enabled: false,
    welcome_delete_after: 0,
  });
  const [messages, setMessages] = useState<WelcomeMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddingMessage, setIsAddingMessage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Fetch settings
        const settingsResponse = await apiClient.get(`/bot/moderation/${chatId}/settings`) as WelcomeSettings;
        if (settingsResponse) {
          setSettings(prev => ({
            ...prev,
            welcome_enabled: settingsResponse.welcome_enabled ?? false,
            welcome_delete_after: settingsResponse.welcome_delete_after ?? 0,
          }));
        }

        // Fetch welcome messages
        try {
          const messagesResponse = await apiClient.get(`/bot/moderation/${chatId}/welcome-messages`) as { messages?: WelcomeMessage[] };
          if (messagesResponse?.messages) {
            setMessages(messagesResponse.messages);
          }
        } catch {
          setMessages([]);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    if (chatId) {
      fetchData();
    }
  }, [chatId]);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiClient.patch(`/bot/moderation/${chatId}/settings`, settings);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddMessage = async () => {
    if (!newMessage.trim()) return;
    
    setIsAddingMessage(true);
    try {
      const response = await apiClient.post(`/bot/moderation/${chatId}/welcome-messages`, {
        message_text: newMessage.trim(),
        is_active: true,
      }) as WelcomeMessage;
      
      if (response) {
        setMessages(prev => [...prev, response]);
        setNewMessage('');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to add message');
    } finally {
      setIsAddingMessage(false);
    }
  };

  const handleDeleteMessage = async (messageId: number) => {
    try {
      await apiClient.delete(`/bot/moderation/${chatId}/welcome-messages/${messageId}`);
      setMessages(prev => prev.filter(m => m.id !== messageId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete message');
    }
  };

  const handleToggleMessage = async (messageId: number, isActive: boolean) => {
    try {
      await apiClient.patch(`/bot/moderation/${chatId}/welcome-messages/${messageId}`, {
        is_active: isActive,
      });
      setMessages(prev => prev.map(m => m.id === messageId ? { ...m, is_active: isActive } : m));
    } catch (err: any) {
      setError(err.message || 'Failed to update message');
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  // Variables that can be used in messages
  const variables = [
    { name: '{username}', desc: "User's username" },
    { name: '{first_name}', desc: "User's first name" },
    { name: '{chat_name}', desc: 'Name of the chat' },
    { name: '{member_count}', desc: 'Total members count' },
    { name: '{mention}', desc: "Clickable mention of user" },
  ];

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Main Toggle */}
      <Card sx={{ mb: 3, bgcolor: alpha('#8b5cf6', 0.05), border: '1px solid', borderColor: alpha('#8b5cf6', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 50,
                  height: 50,
                  borderRadius: 2,
                  bgcolor: alpha('#8b5cf6', 0.2),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <WaveIcon sx={{ color: '#8b5cf6', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Welcome Messages</Typography>
                <Typography variant="body2" color="text.secondary">
                  Send personalized greetings when new members join your chat
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.welcome_enabled}
              onChange={(e) => setSettings(prev => ({ ...prev, welcome_enabled: e.target.checked }))}
              color="secondary"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {settings.welcome_enabled && (
        <>
          {/* Available Variables */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
            <Typography variant="subtitle2" color="text.secondary" mb={1}>
              Available Variables (click to copy):
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {variables.map((v) => (
                <Tooltip key={v.name} title={v.desc}>
                  <Chip
                    label={v.name}
                    size="small"
                    onClick={() => {
                      navigator.clipboard.writeText(v.name);
                      setNewMessage(prev => prev + v.name);
                    }}
                    sx={{ cursor: 'pointer', fontFamily: 'monospace' }}
                  />
                </Tooltip>
              ))}
            </Box>
          </Paper>

          {/* Add New Message */}
          <Typography variant="subtitle1" mb={2}>
            Welcome Messages ({messages.length} messages)
          </Typography>
          
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="New welcome message"
              placeholder="Hello {first_name}! 👋 Welcome to {chat_name}! We now have {member_count} members."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box display="flex" gap={1}>
                <Button variant="outlined" size="small" startIcon={<ImageIcon />} disabled>
                  Add Image
                </Button>
                <Button variant="outlined" size="small" startIcon={<ButtonIcon />} disabled>
                  Add Button
                </Button>
              </Box>
              <Button
                variant="contained"
                startIcon={isAddingMessage ? <CircularProgress size={16} /> : <AddIcon />}
                onClick={handleAddMessage}
                disabled={isAddingMessage || !newMessage.trim()}
              >
                Add Message
              </Button>
            </Box>
          </Paper>

          {/* Messages List */}
          {messages.length === 0 ? (
            <Alert severity="info">
              No welcome messages added yet. Create your first welcome message above.
            </Alert>
          ) : (
            <Paper variant="outlined">
              <List>
                {messages.map((msg, index) => (
                  <React.Fragment key={msg.id}>
                    <ListItem
                      sx={{
                        bgcolor: msg.is_active ? 'transparent' : alpha('#000', 0.02),
                        opacity: msg.is_active ? 1 : 0.6,
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <Typography variant="subtitle2">
                              Message #{index + 1}
                            </Typography>
                            {!msg.is_active && (
                              <Chip label="Disabled" size="small" color="default" />
                            )}
                            {msg.media_url && (
                              <Chip label="Has Media" size="small" color="info" icon={<ImageIcon />} />
                            )}
                            {msg.buttons && msg.buttons.length > 0 && (
                              <Chip label={`${msg.buttons.length} Buttons`} size="small" color="secondary" icon={<ButtonIcon />} />
                            )}
                          </Box>
                        }
                        secondary={
                          <Typography
                            variant="body2"
                            sx={{
                              whiteSpace: 'pre-wrap',
                              bgcolor: alpha('#8b5cf6', 0.05),
                              p: 1.5,
                              borderRadius: 1,
                              border: '1px solid',
                              borderColor: 'divider',
                            }}
                          >
                            {msg.message_text}
                          </Typography>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Box display="flex" flexDirection="column" gap={1}>
                          <Tooltip title={msg.is_active ? 'Disable' : 'Enable'}>
                            <Switch
                              checked={msg.is_active}
                              onChange={(e) => handleToggleMessage(msg.id, e.target.checked)}
                              size="small"
                            />
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton onClick={() => handleDeleteMessage(msg.id)} color="error" size="small">
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < messages.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          )}

          <Divider sx={{ my: 3 }} />

          {/* Auto-delete setting */}
          <Box mb={3}>
            <Typography variant="subtitle1" mb={1}>
              Auto-Delete Welcome Messages
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Automatically remove welcome messages after some time to keep chat clean
            </Typography>
            <TextField
              type="number"
              label="Delete after (seconds)"
              value={settings.welcome_delete_after}
              onChange={(e) => setSettings(prev => ({ ...prev, welcome_delete_after: parseInt(e.target.value) || 0 }))}
              helperText="Set to 0 to never auto-delete"
              InputProps={{ inputProps: { min: 0 } }}
              sx={{ width: 200 }}
            />
          </Box>
        </>
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};
