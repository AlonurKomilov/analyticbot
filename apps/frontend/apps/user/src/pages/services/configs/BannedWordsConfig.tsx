/**
 * Banned Words Filter Configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
  TextField,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
} from '@mui/material';
import {
  Block as BlockIcon,
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  DeleteSweep as DeleteMsgIcon,
  Gavel as BanIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface BannedWordsSettings {
  banned_words_enabled: boolean;
  banned_words_action: string;
  case_sensitive: boolean;
}

interface BannedWord {
  id: number;
  word: string;
  is_regex: boolean;
  created_at: string;
}

interface Props {
  chatId: number;
}

export const BannedWordsConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<BannedWordsSettings>({
    banned_words_enabled: false,
    banned_words_action: 'delete',
    case_sensitive: false,
  });
  const [bannedWords, setBannedWords] = useState<BannedWord[]>([]);
  const [newWord, setNewWord] = useState('');
  const [isRegex, setIsRegex] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddingWord, setIsAddingWord] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Fetch settings
        const settingsResponse = await apiClient.get(`/bot/moderation/${chatId}/settings`) as BannedWordsSettings;
        if (settingsResponse) {
          setSettings(prev => ({
            ...prev,
            banned_words_enabled: settingsResponse.banned_words_enabled ?? false,
            banned_words_action: settingsResponse.banned_words_action ?? 'delete',
            case_sensitive: settingsResponse.case_sensitive ?? false,
          }));
        }

        // Fetch banned words list
        try {
          const wordsResponse = await apiClient.get(`/bot/moderation/${chatId}/banned-words`) as { words?: BannedWord[] };
          if (wordsResponse?.words) {
            setBannedWords(wordsResponse.words);
          }
        } catch {
          // May not exist yet
          setBannedWords([]);
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

  const handleAddWord = async () => {
    if (!newWord.trim()) return;
    
    setIsAddingWord(true);
    try {
      const response = await apiClient.post(`/bot/moderation/${chatId}/banned-words`, {
        word: newWord.trim(),
        is_regex: isRegex,
      }) as BannedWord;
      
      if (response) {
        setBannedWords(prev => [...prev, response]);
        setNewWord('');
        setIsRegex(false);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to add word');
    } finally {
      setIsAddingWord(false);
    }
  };

  const handleDeleteWord = async (wordId: number) => {
    try {
      await apiClient.delete(`/bot/moderation/${chatId}/banned-words/${wordId}`);
      setBannedWords(prev => prev.filter(w => w.id !== wordId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete word');
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Main Toggle */}
      <Card sx={{ mb: 3, bgcolor: alpha('#ef4444', 0.05), border: '1px solid', borderColor: alpha('#ef4444', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 50,
                  height: 50,
                  borderRadius: 2,
                  bgcolor: alpha('#ef4444', 0.2),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <BlockIcon sx={{ color: '#ef4444', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Banned Words Filter</Typography>
                <Typography variant="body2" color="text.secondary">
                  Automatically moderate messages containing banned words or phrases
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.banned_words_enabled}
              onChange={(e) => setSettings(prev => ({ ...prev, banned_words_enabled: e.target.checked }))}
              color="error"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {settings.banned_words_enabled && (
        <>
          {/* Action Selection */}
          <Box mb={3}>
            <FormControl fullWidth>
              <InputLabel>Action on Detection</InputLabel>
              <Select
                value={settings.banned_words_action}
                label="Action on Detection"
                onChange={(e) => setSettings(prev => ({ ...prev, banned_words_action: e.target.value }))}
              >
                <MenuItem value="delete">
                  <Box display="flex" alignItems="center" gap={1}>
                    <DeleteMsgIcon fontSize="small" />
                    Delete Message
                  </Box>
                </MenuItem>
                <MenuItem value="warn">
                  <Box display="flex" alignItems="center" gap={1}>
                    <WarningIcon fontSize="small" />
                    Warn User
                  </Box>
                </MenuItem>
                <MenuItem value="delete_warn">
                  <Box display="flex" alignItems="center" gap={1}>
                    <DeleteMsgIcon fontSize="small" />
                    <WarningIcon fontSize="small" />
                    Delete + Warn
                  </Box>
                </MenuItem>
                <MenuItem value="ban">
                  <Box display="flex" alignItems="center" gap={1}>
                    <BanIcon fontSize="small" />
                    Ban User (strict)
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Case Sensitivity */}
          <FormControlLabel
            control={
              <Switch
                checked={settings.case_sensitive}
                onChange={(e) => setSettings(prev => ({ ...prev, case_sensitive: e.target.checked }))}
              />
            }
            label="Case-sensitive matching"
            sx={{ mb: 3 }}
          />

          <Divider sx={{ my: 3 }} />

          {/* Add New Word */}
          <Typography variant="subtitle1" mb={2}>
            Banned Words List ({bannedWords.length} words)
          </Typography>
          
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Box display="flex" gap={2} alignItems="flex-end">
              <TextField
                fullWidth
                label="Add new word or phrase"
                placeholder="Enter word, phrase, or regex pattern..."
                value={newWord}
                onChange={(e) => setNewWord(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddWord()}
                size="small"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={isRegex}
                    onChange={(e) => setIsRegex(e.target.checked)}
                    size="small"
                  />
                }
                label="Regex"
                sx={{ whiteSpace: 'nowrap' }}
              />
              <Button
                variant="contained"
                startIcon={isAddingWord ? <CircularProgress size={16} /> : <AddIcon />}
                onClick={handleAddWord}
                disabled={isAddingWord || !newWord.trim()}
              >
                Add
              </Button>
            </Box>
          </Paper>

          {/* Words List */}
          {bannedWords.length === 0 ? (
            <Alert severity="info">
              No banned words added yet. Add your first word above.
            </Alert>
          ) : (
            <Paper variant="outlined">
              <List dense>
                {bannedWords.map((word, index) => (
                  <React.Fragment key={word.id}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography
                              component="span"
                              sx={{ fontFamily: 'monospace', bgcolor: 'action.hover', px: 1, py: 0.5, borderRadius: 1 }}
                            >
                              {word.word}
                            </Typography>
                            {word.is_regex && (
                              <Chip label="Regex" size="small" color="secondary" />
                            )}
                          </Box>
                        }
                        secondary={`Added ${new Date(word.created_at).toLocaleDateString()}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton edge="end" onClick={() => handleDeleteWord(word.id)} color="error">
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < bannedWords.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          )}
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
