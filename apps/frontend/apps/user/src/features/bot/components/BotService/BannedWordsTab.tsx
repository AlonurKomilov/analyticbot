/**
 * Banned Words Tab Component
 * Manage banned words for content filtering
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  FormControlLabel,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';
import toast from 'react-hot-toast';

import { useModerationStore } from '@/store';
import type { BannedWordCreate, ModerationAction } from '@/types';

interface BannedWordsTabProps {
  chatId: number;
}

export const BannedWordsTab: React.FC<BannedWordsTabProps> = ({ chatId }) => {
  const {
    bannedWords,
    settings,
    isLoadingBannedWords,
    isSaving,
    addBannedWord,
    deleteBannedWord,
    bulkAddBannedWords,
  } = useModerationStore();

  const [newWord, setNewWord] = useState('');
  const [isRegex, setIsRegex] = useState(false);
  const [action, setAction] = useState<ModerationAction>('delete');
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [bulkWords, setBulkWords] = useState('');

  const handleAddWord = async () => {
    if (!newWord.trim()) {
      toast.error('Please enter a word');
      return;
    }

    // Validate regex if regex mode is enabled
    if (isRegex) {
      try {
        new RegExp(newWord);
      } catch (e) {
        toast.error('Invalid regex pattern');
        return;
      }
    }

    try {
      await addBannedWord(chatId, {
        word: newWord.trim(),
        is_regex: isRegex,
        action: action,
      });
      setNewWord('');
      toast.success('Word added to ban list');
    } catch (err) {
      toast.error('Failed to add word');
    }
  };

  const handleDeleteWord = async (wordId: number) => {
    try {
      await deleteBannedWord(chatId, wordId);
      toast.success('Word removed from ban list');
    } catch (err) {
      toast.error('Failed to remove word');
    }
  };

  const handleBulkAdd = async () => {
    const words = bulkWords
      .split('\n')
      .map((w) => w.trim())
      .filter((w) => w.length > 0);

    if (words.length === 0) {
      toast.error('Please enter at least one word');
      return;
    }

    const wordObjects: BannedWordCreate[] = words.map((word) => ({
      word,
      is_regex: false,
      action: 'delete' as ModerationAction,
    }));

    try {
      await bulkAddBannedWords(chatId, wordObjects);
      setBulkWords('');
      setBulkDialogOpen(false);
      toast.success(`Added ${words.length} words to ban list`);
    } catch (err) {
      toast.error('Failed to add words');
    }
  };

  if (!settings?.banned_words_enabled) {
    return (
      <Alert severity="warning">
        <Typography variant="body1">
          <strong>Banned Words Filter is disabled.</strong>
        </Typography>
        <Typography variant="body2">
          Enable "Banned Words Filter" in the Settings tab to use this feature.
        </Typography>
      </Alert>
    );
  }

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        Messages containing these words will be automatically deleted or actioned.
        Use regex for advanced pattern matching.
      </Alert>

      {/* Add New Word */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Add Banned Word
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Box display="flex" gap={2} flexWrap="wrap" alignItems="flex-start">
          <TextField
            label="Word or Pattern"
            value={newWord}
            onChange={(e) => setNewWord(e.target.value)}
            placeholder={isRegex ? '\\b(spam|ad)\\b' : 'spam'}
            size="small"
            sx={{ minWidth: 200, flexGrow: 1 }}
            onKeyPress={(e) => e.key === 'Enter' && handleAddWord()}
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={isRegex}
                onChange={(e) => setIsRegex(e.target.checked)}
                size="small"
              />
            }
            label="Regex"
          />

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Action</InputLabel>
            <Select
              value={action}
              label="Action"
              onChange={(e) => setAction(e.target.value as ModerationAction)}
            >
              <MenuItem value="delete">Delete</MenuItem>
              <MenuItem value="warn">Warn</MenuItem>
              <MenuItem value="mute">Mute</MenuItem>
              <MenuItem value="kick">Kick</MenuItem>
              <MenuItem value="ban">Ban</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={isSaving ? <CircularProgress size={16} /> : <AddIcon />}
            onClick={handleAddWord}
            disabled={!newWord.trim() || isSaving}
          >
            Add
          </Button>

          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={() => setBulkDialogOpen(true)}
          >
            Bulk Add
          </Button>
        </Box>
      </Paper>

      {/* Banned Words List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Banned Words ({bannedWords.length})
        </Typography>
        <Divider sx={{ mb: 2 }} />

        {isLoadingBannedWords ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : bannedWords.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
            No banned words configured. Add some words above.
          </Typography>
        ) : (
          <List>
            {bannedWords.map((word) => (
              <ListItem
                key={word.id}
                sx={{
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                  '&:last-child': { borderBottom: 'none' },
                }}
              >
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography
                        variant="body1"
                        sx={{
                          fontFamily: word.is_regex ? 'monospace' : 'inherit',
                          backgroundColor: word.is_regex ? 'action.hover' : 'transparent',
                          px: word.is_regex ? 1 : 0,
                          borderRadius: 1,
                        }}
                      >
                        {word.word}
                      </Typography>
                      {word.is_regex && (
                        <Chip label="Regex" size="small" color="secondary" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box display="flex" gap={1} mt={0.5}>
                      <Chip
                        label={word.action}
                        size="small"
                        color={
                          word.action === 'ban'
                            ? 'error'
                            : word.action === 'kick'
                            ? 'warning'
                            : 'default'
                        }
                      />
                      <Typography variant="caption" color="text.secondary">
                        Added: {new Date(word.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => handleDeleteWord(word.id)}
                    disabled={isSaving}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>

      {/* Bulk Add Dialog */}
      <Dialog
        open={bulkDialogOpen}
        onClose={() => setBulkDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Bulk Add Banned Words</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter one word per line. All words will be added with "delete" action.
          </Typography>
          <TextField
            multiline
            rows={10}
            fullWidth
            value={bulkWords}
            onChange={(e) => setBulkWords(e.target.value)}
            placeholder="spam&#10;advertisement&#10;buy now&#10;click here"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleBulkAdd}
            disabled={!bulkWords.trim() || isSaving}
          >
            {isSaving ? <CircularProgress size={20} /> : 'Add All'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BannedWordsTab;
