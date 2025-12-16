/**
 * Welcome Messages Tab Component
 * Configure welcome and goodbye messages
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import toast from 'react-hot-toast';

import { useModerationStore } from '@/store';
import type { MessageButton } from '@/types';

interface WelcomeMessagesTabProps {
  chatId: number;
}

const PLACEHOLDER_HELP = `Available placeholders:
• {name} - User's full name
• {username} - User's @username
• {user_id} - User's Telegram ID
• {chat_title} - Chat/group name
• {member_count} - Current member count
• {mention} - Mention the user`;

export const WelcomeMessagesTab: React.FC<WelcomeMessagesTabProps> = ({ chatId }) => {
  const {
    settings,
    welcomeMessage,
    goodbyeMessage,
    isLoadingWelcome,
    isSaving,
    updateWelcomeMessage,
    deleteWelcomeMessage,
  } = useModerationStore();

  // Welcome message state
  const [welcomeTemplate, setWelcomeTemplate] = useState('');
  const [welcomeEnabled, setWelcomeEnabled] = useState(true);
  const [welcomeParseMode, setWelcomeParseMode] = useState('HTML');
  const [welcomeDeleteAfter, setWelcomeDeleteAfter] = useState<number | null>(null);
  const [welcomeButtons, setWelcomeButtons] = useState<MessageButton[]>([]);

  // Goodbye message state
  const [goodbyeTemplate, setGoodbyeTemplate] = useState('');
  const [goodbyeEnabled, setGoodbyeEnabled] = useState(true);
  const [goodbyeParseMode, setGoodbyeParseMode] = useState('HTML');
  const [goodbyeDeleteAfter, setGoodbyeDeleteAfter] = useState<number | null>(null);

  useEffect(() => {
    if (welcomeMessage) {
      setWelcomeTemplate(welcomeMessage.message_template);
      setWelcomeEnabled(welcomeMessage.is_enabled);
      setWelcomeParseMode(welcomeMessage.parse_mode);
      setWelcomeDeleteAfter(welcomeMessage.delete_after_seconds);
      setWelcomeButtons(welcomeMessage.buttons || []);
    } else {
      setWelcomeTemplate('👋 Welcome {name} to {chat_title}!\n\nWe now have {member_count} members! 🎉');
      setWelcomeEnabled(true);
      setWelcomeParseMode('HTML');
      setWelcomeDeleteAfter(null);
      setWelcomeButtons([]);
    }
  }, [welcomeMessage]);

  useEffect(() => {
    if (goodbyeMessage) {
      setGoodbyeTemplate(goodbyeMessage.message_template);
      setGoodbyeEnabled(goodbyeMessage.is_enabled);
      setGoodbyeParseMode(goodbyeMessage.parse_mode);
      setGoodbyeDeleteAfter(goodbyeMessage.delete_after_seconds);
    } else {
      setGoodbyeTemplate('👋 {name} has left the chat. We\'ll miss you!');
      setGoodbyeEnabled(true);
      setGoodbyeParseMode('HTML');
      setGoodbyeDeleteAfter(null);
    }
  }, [goodbyeMessage]);

  const handleSaveWelcome = async () => {
    if (!welcomeTemplate.trim()) {
      toast.error('Please enter a welcome message');
      return;
    }

    try {
      await updateWelcomeMessage(chatId, {
        message_type: 'welcome',
        message_template: welcomeTemplate,
        parse_mode: welcomeParseMode,
        is_enabled: welcomeEnabled,
        delete_after_seconds: welcomeDeleteAfter || undefined,
        buttons: welcomeButtons.length > 0 ? welcomeButtons : undefined,
      });
      toast.success('Welcome message saved!');
    } catch (err) {
      toast.error('Failed to save welcome message');
    }
  };

  const handleSaveGoodbye = async () => {
    if (!goodbyeTemplate.trim()) {
      toast.error('Please enter a goodbye message');
      return;
    }

    try {
      await updateWelcomeMessage(chatId, {
        message_type: 'goodbye',
        message_template: goodbyeTemplate,
        parse_mode: goodbyeParseMode,
        is_enabled: goodbyeEnabled,
        delete_after_seconds: goodbyeDeleteAfter || undefined,
      });
      toast.success('Goodbye message saved!');
    } catch (err) {
      toast.error('Failed to save goodbye message');
    }
  };

  const handleDeleteWelcome = async () => {
    if (window.confirm('Delete welcome message?')) {
      try {
        await deleteWelcomeMessage(chatId, 'welcome');
        toast.success('Welcome message deleted');
      } catch (err) {
        toast.error('Failed to delete');
      }
    }
  };

  const handleDeleteGoodbye = async () => {
    if (window.confirm('Delete goodbye message?')) {
      try {
        await deleteWelcomeMessage(chatId, 'goodbye');
        toast.success('Goodbye message deleted');
      } catch (err) {
        toast.error('Failed to delete');
      }
    }
  };

  const handleAddButton = () => {
    setWelcomeButtons([...welcomeButtons, { text: 'Button', url: '' }]);
  };

  const handleRemoveButton = (index: number) => {
    setWelcomeButtons(welcomeButtons.filter((_, i) => i !== index));
  };

  const handleButtonChange = (index: number, field: 'text' | 'url', value: string) => {
    const updated = [...welcomeButtons];
    updated[index] = { ...updated[index], [field]: value };
    setWelcomeButtons(updated);
  };

  if (!settings?.welcome_enabled) {
    return (
      <Alert severity="warning">
        <Typography variant="body1">
          <strong>Welcome Messages feature is disabled.</strong>
        </Typography>
        <Typography variant="body2">
          Enable "Welcome Messages" in the Settings tab to use this feature.
        </Typography>
      </Alert>
    );
  }

  if (isLoadingWelcome) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Box display="flex" alignItems="flex-start" gap={1}>
          <Box>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
              {PLACEHOLDER_HELP}
            </Typography>
          </Box>
        </Box>
      </Alert>

      <Grid container spacing={3}>
        {/* Welcome Message */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Welcome Message</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={welcomeEnabled}
                    onChange={(e) => setWelcomeEnabled(e.target.checked)}
                  />
                }
                label="Enabled"
              />
            </Box>
            <Divider sx={{ mb: 2 }} />

            <TextField
              fullWidth
              multiline
              rows={6}
              label="Message Template"
              value={welcomeTemplate}
              onChange={(e) => setWelcomeTemplate(e.target.value)}
              placeholder="Welcome {name}!"
              sx={{ mb: 2 }}
            />

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Parse Mode</InputLabel>
                  <Select
                    value={welcomeParseMode}
                    label="Parse Mode"
                    onChange={(e) => setWelcomeParseMode(e.target.value)}
                  >
                    <MenuItem value="HTML">HTML</MenuItem>
                    <MenuItem value="Markdown">Markdown</MenuItem>
                    <MenuItem value="MarkdownV2">MarkdownV2</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="Delete After (seconds)"
                  value={welcomeDeleteAfter || ''}
                  onChange={(e) =>
                    setWelcomeDeleteAfter(e.target.value ? parseInt(e.target.value) : null)
                  }
                  placeholder="Never"
                />
              </Grid>
            </Grid>

            {/* Inline Buttons */}
            <Box sx={{ mb: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2">Inline Buttons</Typography>
                <Button size="small" startIcon={<AddIcon />} onClick={handleAddButton}>
                  Add Button
                </Button>
              </Box>
              {welcomeButtons.map((button, index) => (
                <Box key={index} display="flex" gap={1} mb={1}>
                  <TextField
                    size="small"
                    label="Text"
                    value={button.text}
                    onChange={(e) => handleButtonChange(index, 'text', e.target.value)}
                    sx={{ flex: 1 }}
                  />
                  <TextField
                    size="small"
                    label="URL"
                    value={button.url || ''}
                    onChange={(e) => handleButtonChange(index, 'url', e.target.value)}
                    sx={{ flex: 2 }}
                  />
                  <IconButton onClick={() => handleRemoveButton(index)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
            </Box>

            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                startIcon={isSaving ? <CircularProgress size={16} /> : <SaveIcon />}
                onClick={handleSaveWelcome}
                disabled={isSaving}
              >
                Save
              </Button>
              {welcomeMessage && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleDeleteWelcome}
                  disabled={isSaving}
                >
                  Delete
                </Button>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Goodbye Message */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Goodbye Message</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={goodbyeEnabled}
                    onChange={(e) => setGoodbyeEnabled(e.target.checked)}
                  />
                }
                label="Enabled"
              />
            </Box>
            <Divider sx={{ mb: 2 }} />

            <TextField
              fullWidth
              multiline
              rows={6}
              label="Message Template"
              value={goodbyeTemplate}
              onChange={(e) => setGoodbyeTemplate(e.target.value)}
              placeholder="Goodbye {name}!"
              sx={{ mb: 2 }}
            />

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Parse Mode</InputLabel>
                  <Select
                    value={goodbyeParseMode}
                    label="Parse Mode"
                    onChange={(e) => setGoodbyeParseMode(e.target.value)}
                  >
                    <MenuItem value="HTML">HTML</MenuItem>
                    <MenuItem value="Markdown">Markdown</MenuItem>
                    <MenuItem value="MarkdownV2">MarkdownV2</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="Delete After (seconds)"
                  value={goodbyeDeleteAfter || ''}
                  onChange={(e) =>
                    setGoodbyeDeleteAfter(e.target.value ? parseInt(e.target.value) : null)
                  }
                  placeholder="Never"
                />
              </Grid>
            </Grid>

            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                startIcon={isSaving ? <CircularProgress size={16} /> : <SaveIcon />}
                onClick={handleSaveGoodbye}
                disabled={isSaving}
              >
                Save
              </Button>
              {goodbyeMessage && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleDeleteGoodbye}
                  disabled={isSaving}
                >
                  Delete
                </Button>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WelcomeMessagesTab;
