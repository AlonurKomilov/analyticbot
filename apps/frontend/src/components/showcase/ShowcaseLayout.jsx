/**
 * ShowcaseLayout Component
 *
 * Provides shared layout structure for the tables showcase
 * including the header, navigation, and feature summary
 */

import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const ShowcaseLayout = ({ children }) => {
    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            {/* Header Section */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h3" gutterBottom align="center">
                    Enhanced Data Tables Showcase
                </Typography>
                <Typography variant="h6" color="text.secondary" align="center" paragraph>
                    Professional data table components with enterprise-grade features
                </Typography>
            </Box>

            {/* Main Content */}
            {children}

            {/* Feature Summary */}
            <Paper sx={{ p: 3, mt: 4, bgcolor: 'grey.50' }}>
                <Typography variant="h6" gutterBottom>
                    🎯 Enhanced Data Table Features
                </Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
                    <Box>
                        <Typography variant="subtitle2" color="primary" gutterBottom>
                            Data Management
                        </Typography>
                        <Typography variant="body2" component="ul" sx={{ pl: 2, mb: 0 }}>
                            <li>Advanced pagination with customizable page sizes</li>
                            <li>Multi-column sorting with visual indicators</li>
                            <li>Global search and column-specific filtering</li>
                            <li>Real-time data refresh capabilities</li>
                        </Typography>
                    </Box>

                    <Box>
                        <Typography variant="subtitle2" color="primary" gutterBottom>
                            User Interface
                        </Typography>
                        <Typography variant="body2" component="ul" sx={{ pl: 2, mb: 0 }}>
                            <li>Column visibility management and reordering</li>
                            <li>Responsive design with density controls</li>
                            <li>Professional loading and error states</li>
                            <li>Full accessibility compliance (WCAG 2.1)</li>
                        </Typography>
                    </Box>

                    <Box>
                        <Typography variant="subtitle2" color="primary" gutterBottom>
                            Actions & Export
                        </Typography>
                        <Typography variant="body2" component="ul" sx={{ pl: 2, mb: 0 }}>
                            <li>Bulk selection and batch operations</li>
                            <li>Export functionality (CSV, Excel, PDF)</li>
                            <li>Row-level action menus</li>
                            <li>Customizable action workflows</li>
                        </Typography>
                    </Box>
                </Box>
            </Paper>
        </Container>
    );
};

export default ShowcaseLayout;
