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
import { uiLogger } from '@/utils/logger';

// Mock data - replace with real API call when backend is ready
const mockInvoices = [
  { id: 'INV-001', date: '2025-10-01', amount: '$29.99', status: 'Paid' },
  { id: 'INV-002', date: '2025-09-01', amount: '$29.99', status: 'Paid' },
  { id: 'INV-003', date: '2025-08-01', amount: '$19.99', status: 'Paid' },
];

const InvoicesPage: React.FC = () => {
  const handleDownload = (invoiceId: string) => {
    uiLogger.debug('Invoice download requested', { invoiceId });
    
    // Generate a simple PDF-like invoice (mock implementation)
    const invoice = mockInvoices.find(inv => inv.id === invoiceId);
    if (!invoice) return;

    const invoiceText = `
INVOICE ${invoice.id}
Date: ${invoice.date}
Amount: ${invoice.amount}
Status: ${invoice.status}

Thank you for your business!
    `.trim();

    // Create a downloadable text file (in production, this would be a PDF from backend)
    const blob = new Blob([invoiceText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${invoiceId}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
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
