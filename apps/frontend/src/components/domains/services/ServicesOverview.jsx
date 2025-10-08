import React from 'react';
import { Box, Typography, Container, Paper } from '@mui/material';

/**
 * AI Services Overview Component
 * Landing page for AI services section
 */
const ServicesOverview = () => {
    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Paper variant="card">
                <Typography variant="h4" component="h1" gutterBottom>
                    AI Services Overview
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Select a service from the sidebar to get started with AI-powered analytics and automation.
                </Typography>

                {/* TODO: Add services grid/overview */}
                <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" color="text.secondary" fontStyle="italic">
                        Services overview dashboard coming soon...
                    </Typography>
                </Box>
            </Paper>
        </Container>
    );
};

export default ServicesOverview;
