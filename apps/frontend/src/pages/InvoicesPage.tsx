/**
 * Invoices Page
 * Download and manage invoices
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
  IconButton,
} from '@mui/material';
import { Download } from '@mui/icons-material';

// Mock data - replace with real API call
const mockInvoices = [
  { id: 'INV-001', date: '2025-10-01', amount: '$29.99', status: 'Paid' },
  { id: 'INV-002', date: '2025-09-01', amount: '$29.99', status: 'Paid' },
  { id: 'INV-003', date: '2025-08-01', amount: '$19.99', status: 'Paid' },
];

const InvoicesPage: React.FC = () => {
  const handleDownload = (invoiceId: string) => {
    console.log('Downloading invoice:', invoiceId);
    // TODO: Implement invoice download
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Invoices
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Download and manage your billing invoices
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Invoice ID</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockInvoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell>{invoice.id}</TableCell>
                <TableCell>{invoice.date}</TableCell>
                <TableCell>{invoice.amount}</TableCell>
                <TableCell>{invoice.status}</TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleDownload(invoice.id)}
                    aria-label="download invoice"
                  >
                    <Download />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default InvoicesPage;
