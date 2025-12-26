import React from 'react';
import { Alert } from '@mui/material';

/**
 * Props for the ChartErrorBoundary component
 */
interface ChartErrorBoundaryProps {
    /** Child components to render */
    children: React.ReactNode;
}

/**
 * State for the ChartErrorBoundary component
 */
interface ChartErrorBoundaryState {
    /** Whether an error has occurred */
    hasError: boolean;
    /** The error that occurred */
    error: Error | null;
}

/**
 * ChartErrorBoundary - Error boundary component for chart rendering errors
 *
 * Catches and handles JavaScript errors in the chart component tree,
 * providing a fallback UI when chart rendering fails.
 */
class ChartErrorBoundary extends React.Component<ChartErrorBoundaryProps, ChartErrorBoundaryState> {
    constructor(props: ChartErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ChartErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
        console.error('Chart Error:', error, errorInfo);
    }

    render(): React.ReactNode {
        if (this.state.hasError) {
            return (
                <Alert severity="error">
                    An error occurred while displaying the chart. Please refresh the page.
                </Alert>
            );
        }

        return this.props.children;
    }
}

export default ChartErrorBoundary;
