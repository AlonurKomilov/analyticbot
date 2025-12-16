import React from 'react';
import { Box, Typography, Paper, Alert } from '@mui/material';
import { Category as CategoryIcon } from '@mui/icons-material';

const CategoriesPage: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        <CategoryIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
        Category Management
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Create and organize channel categories
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Category management coming in Phase 4. Categories are currently managed via the database.
      </Alert>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          This page will allow you to:
        </Typography>
        <ul>
          <li>Create new categories</li>
          <li>Edit category names, icons, and colors</li>
          <li>Set category display order</li>
          <li>Create sub-categories</li>
          <li>Merge or delete categories</li>
        </ul>
      </Paper>
    </Box>
  );
};

export default CategoriesPage;
