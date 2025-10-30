/**
 * Admin Bot Management Page
 * Page wrapper for Admin Bot Panel
 */

import React from 'react';
import { Container } from '@mui/material';
import { AdminBotPanel } from '@/components/bot';

export const AdminBotManagementPage: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <AdminBotPanel />
    </Container>
  );
};

export default AdminBotManagementPage;
