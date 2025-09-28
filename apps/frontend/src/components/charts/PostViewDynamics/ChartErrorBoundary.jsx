import React from 'react';
import { Alert } from '@mui/material';

/**
 * ChartErrorBoundary - Error boundary component for chart rendering errors
 * 
 * Catches and handles JavaScript errors in the chart component tree,
 * providing a fallback UI when chart rendering fails.
 */
class ChartErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Chart Error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <Alert severity="error" variant="spaced">
                    Chart ma'lumotlarini ko'rsatishda xatolik yuz berdi. Sahifani yangilang.
                </Alert>
            );
        }

        return this.props.children;
    }
}

export default ChartErrorBoundary;