/**
 * Example Component with Design Tokens
 * 
 * This demonstrates the correct usage of design tokens in a component.
 * Use this as a reference when migrating other components.
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { spacing, colors, shadows, sizing, radius, animation, typography } from '@/theme/tokens';

interface User {
  id: number;
  name: string;
  email: string;
  status: 'active' | 'inactive' | 'pending';
}

/**
 * Example: User Management Component
 * Demonstrates design token usage for:
 * - Layout spacing
 * - Colors and backgrounds
 * - Shadows and elevation
 * - Sizing and touch targets
 * - Border radius
 * - Animations
 */
const ExampleComponent: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [users] = useState<User[]>([
    { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'inactive' },
    { id: 3, name: 'Bob Wilson', email: 'bob@example.com', status: 'pending' },
  ]);

  const getStatusColor = (status: User['status']) => {
    switch (status) {
      case 'active':
        return { bg: colors.success.bg, color: colors.success.main };
      case 'inactive':
        return { bg: colors.error.bg, color: colors.error.main };
      case 'pending':
        return { bg: colors.warning.bg, color: colors.warning.main };
    }
  };

  return (
    <Box
      sx={{
        // Container padding using section spacing
        padding: spacing.section,
        backgroundColor: colors.background.default,
        minHeight: '100vh',
      }}
    >
      {/* Header Section */}
      <Box
        sx={{
          marginBottom: spacing.section,
        }}
      >
        <Typography
          sx={{
            fontSize: typography.fontSize.xxxl,
            fontWeight: typography.fontWeight.semibold,
            color: colors.text.primary,
            marginBottom: spacing.xs,
          }}
        >
          User Management
        </Typography>
        <Typography
          sx={{
            fontSize: typography.fontSize.md,
            color: colors.text.secondary,
          }}
        >
          Manage your users with design tokens
        </Typography>
      </Box>

      {/* Action Bar with Search and Add Button */}
      <Paper
        sx={{
          padding: spacing.md,
          marginBottom: spacing.lg,
          backgroundColor: colors.background.paper,
          borderRadius: radius.card,
          boxShadow: shadows.card,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            gap: spacing.md,
            alignItems: 'center',
          }}
        >
          {/* Search Field - Using sizing tokens for proper touch targets */}
          <TextField
            fullWidth
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <SearchIcon
                  sx={{
                    marginRight: spacing.xs,
                    color: colors.text.secondary,
                    fontSize: sizing.icon.md,
                  }}
                />
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                height: sizing.input.medium,
                backgroundColor: colors.background.default,
                borderRadius: radius.input,
                transition: animation.transition.fast,
                '&:hover': {
                  borderColor: colors.border.focus,
                },
                '&.Mui-focused': {
                  borderColor: colors.border.focus,
                  boxShadow: shadows.focus,
                },
              },
            }}
          />

          {/* Add Button - Using proper sizing and spacing */}
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setDialogOpen(true)}
            sx={{
              minHeight: sizing.button.medium,
              padding: `${spacing.sm} ${spacing.md}`,
              borderRadius: radius.button,
              backgroundColor: colors.primary.main,
              color: colors.primary.contrast,
              transition: animation.transition.fast,
              whiteSpace: 'nowrap',
              '&:hover': {
                backgroundColor: colors.primary.dark,
                boxShadow: shadows.md,
              },
            }}
          >
            Add User
          </Button>
        </Box>
      </Paper>

      {/* Alert Example - Using semantic color backgrounds */}
      <Alert
        severity="info"
        sx={{
          marginBottom: spacing.lg,
          borderRadius: radius.md,
          backgroundColor: colors.info.bg,
          color: colors.info.main,
          border: `1px solid ${colors.border.default}`,
          '& .MuiAlert-icon': {
            color: colors.info.main,
          },
        }}
      >
        This component demonstrates proper design token usage. Notice the consistent spacing,
        colors, and sizing throughout.
      </Alert>

      {/* User Cards - Demonstrating card patterns */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: spacing.md,
        }}
      >
        {users.map((user) => (
          <Paper
            key={user.id}
            sx={{
              padding: spacing.lg,
              backgroundColor: colors.background.paper,
              borderRadius: radius.card,
              boxShadow: shadows.card,
              border: `1px solid ${colors.border.subtle}`,
              transition: animation.transition.normal,
              '&:hover': {
                boxShadow: shadows.md,
                borderColor: colors.border.default,
                transform: 'translateY(-2px)',
              },
            }}
          >
            {/* Card Header */}
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: spacing.md,
              }}
            >
              <Typography
                sx={{
                  fontSize: typography.fontSize.lg,
                  fontWeight: typography.fontWeight.semibold,
                  color: colors.text.primary,
                }}
              >
                {user.name}
              </Typography>

              {/* Status Badge - Using semantic colors */}
              <Chip
                label={user.status}
                size="small"
                sx={{
                  backgroundColor: getStatusColor(user.status).bg,
                  color: getStatusColor(user.status).color,
                  borderRadius: radius.badge,
                  height: '24px',
                  fontSize: typography.fontSize.xs,
                  fontWeight: typography.fontWeight.medium,
                  textTransform: 'capitalize',
                }}
              />
            </Box>

            {/* Card Content */}
            <Typography
              sx={{
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary,
                marginBottom: spacing.lg,
              }}
            >
              {user.email}
            </Typography>

            {/* Card Actions - Using proper touch targets */}
            <Box
              sx={{
                display: 'flex',
                gap: spacing.xs,
                justifyContent: 'flex-end',
              }}
            >
              <IconButton
                size="small"
                sx={{
                  minWidth: sizing.touchTarget.min,
                  minHeight: sizing.touchTarget.min,
                  color: colors.primary.main,
                  transition: animation.transition.fast,
                  '&:hover': {
                    backgroundColor: colors.state.hover,
                  },
                }}
              >
                <EditIcon sx={{ fontSize: sizing.icon.sm }} />
              </IconButton>
              <IconButton
                size="small"
                sx={{
                  minWidth: sizing.touchTarget.min,
                  minHeight: sizing.touchTarget.min,
                  color: colors.error.main,
                  transition: animation.transition.fast,
                  '&:hover': {
                    backgroundColor: colors.state.hover,
                  },
                }}
              >
                <DeleteIcon sx={{ fontSize: sizing.icon.sm }} />
              </IconButton>
            </Box>
          </Paper>
        ))}
      </Box>

      {/* Dialog Example - Using proper dialog sizing and spacing */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth={false}
        sx={{
          '& .MuiDialog-paper': {
            width: sizing.dialog.md,
            maxWidth: '90vw',
            borderRadius: radius.dialog,
            boxShadow: shadows.dialog,
            backgroundColor: colors.background.paper,
          },
        }}
      >
        {/* Dialog Header */}
        <DialogTitle
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: spacing.lg,
            borderBottom: `1px solid ${colors.border.default}`,
          }}
        >
          <Typography
            sx={{
              fontSize: typography.fontSize.xl,
              fontWeight: typography.fontWeight.semibold,
              color: colors.text.primary,
            }}
          >
            Add New User
          </Typography>
          <IconButton
            onClick={() => setDialogOpen(false)}
            sx={{
              minWidth: sizing.touchTarget.min,
              minHeight: sizing.touchTarget.min,
              color: colors.text.secondary,
              '&:hover': {
                backgroundColor: colors.state.hover,
              },
            }}
          >
            <CloseIcon sx={{ fontSize: sizing.icon.md }} />
          </IconButton>
        </DialogTitle>

        {/* Dialog Content */}
        <DialogContent
          sx={{
            padding: spacing.lg,
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: spacing.md,
            }}
          >
            <TextField
              fullWidth
              label="Name"
              placeholder="Enter user name"
              sx={{
                '& .MuiOutlinedInput-root': {
                  minHeight: sizing.input.medium,
                },
              }}
            />
            <TextField
              fullWidth
              label="Email"
              placeholder="Enter email address"
              type="email"
              sx={{
                '& .MuiOutlinedInput-root': {
                  minHeight: sizing.input.medium,
                },
              }}
            />
          </Box>
        </DialogContent>

        {/* Dialog Actions */}
        <DialogActions
          sx={{
            padding: spacing.lg,
            gap: spacing.sm,
            borderTop: `1px solid ${colors.border.default}`,
          }}
        >
          <Button
            onClick={() => setDialogOpen(false)}
            sx={{
              minHeight: sizing.button.medium,
              padding: `${spacing.sm} ${spacing.md}`,
              borderRadius: radius.button,
              color: colors.text.primary,
              '&:hover': {
                backgroundColor: colors.state.hover,
              },
            }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => setDialogOpen(false)}
            sx={{
              minHeight: sizing.button.medium,
              padding: `${spacing.sm} ${spacing.md}`,
              borderRadius: radius.button,
              backgroundColor: colors.primary.main,
              color: colors.primary.contrast,
              '&:hover': {
                backgroundColor: colors.primary.dark,
              },
            }}
          >
            Add User
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExampleComponent;
