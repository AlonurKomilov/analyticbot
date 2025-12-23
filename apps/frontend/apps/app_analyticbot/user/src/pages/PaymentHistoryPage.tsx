/**
 * Payment History Page
 * View transaction history and past payments
 */

import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';

// Mock data - replace with real API call
const mockPayments = [
  { id: '1', date: '2025-10-01', amount: '$29.99', status: 'Completed', plan: 'Pro' },
  { id: '2', date: '2025-09-01', amount: '$29.99', status: 'Completed', plan: 'Pro' },
  { id: '3', date: '2025-08-01', amount: '$19.99', status: 'Completed', plan: 'Start' },
];

const PaymentHistoryPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Payment History
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review your past transactions and payment details
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockPayments.map((payment) => (
              <TableRow key={payment.id}>
                <TableCell>{payment.date}</TableCell>
                <TableCell>{payment.plan}</TableCell>
                <TableCell>{payment.amount}</TableCell>
                <TableCell>
                  <Chip
                    label={payment.status}
                    color={payment.status === 'Completed' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default PaymentHistoryPage;
