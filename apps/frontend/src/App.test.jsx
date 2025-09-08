import React from 'react';
import { Container, Box, Typography, Alert } from '@mui/material';

const App = () => {
    return (
        <Container maxWidth="sm" sx={{ py: 4 }}>
            <Box textAlign="center">
                <Typography variant="h3" component="h1" gutterBottom>
                    🚀 AnalyticBot
                </Typography>
                <Alert severity="success" sx={{ mt: 3 }}>
                    ✅ React app is working! The error was in one of the component imports.
                </Alert>
                <Typography variant="body1" sx={{ mt: 2 }}>
                    Basic app structure is functional. Now we need to identify which component import is causing the issue.
                </Typography>
            </Box>
        </Container>
    );
};

export default App;
