/**
 * Error Boundary Component
 *
 * Catches React component errors and provides graceful error handling
 * with user-friendly fallback UI.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { errorLogger } from './errorLogger';

interface Props {
  children: ReactNode;
  /** Custom fallback UI */
  fallback?: (error: Error, reset: () => void) => ReactNode;
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error
    errorLogger.logReactError(error, {
      componentStack: errorInfo.componentStack || undefined,
    });

    // Store error info
    this.setState({ errorInfo });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.resetError);
      }

      // Default fallback UI
      return <DefaultErrorFallback error={this.state.error} reset={this.resetError} />;
    }

    return this.props.children;
  }
}

/**
 * Default Error Fallback UI
 */
interface DefaultErrorFallbackProps {
  error: Error;
  reset: () => void;
}

const DefaultErrorFallback: React.FC<DefaultErrorFallbackProps> = ({ error, reset }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '2rem',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: '4rem',
          marginBottom: '1rem',
        }}
      >
        😕
      </div>

      <h2
        style={{
          fontSize: '1.5rem',
          fontWeight: 600,
          marginBottom: '0.5rem',
          color: '#1f2937',
        }}
      >
        Oops! Something went wrong
      </h2>

      <p
        style={{
          color: '#6b7280',
          marginBottom: '1.5rem',
          maxWidth: '500px',
        }}
      >
        We're sorry, but something unexpected happened. Please try refreshing the page or contact support if the problem persists.
      </p>

      {import.meta.env.DEV === true && (
        <details
          style={{
            marginBottom: '1.5rem',
            padding: '1rem',
            backgroundColor: '#fee2e2',
            borderRadius: '0.5rem',
            textAlign: 'left',
            maxWidth: '600px',
            width: '100%',
          }}
        >
          <summary
            style={{
              cursor: 'pointer',
              fontWeight: 600,
              color: '#991b1b',
              marginBottom: '0.5rem',
            }}
          >
            Error Details (Development Only)
          </summary>
          <pre
            style={{
              fontSize: '0.875rem',
              color: '#7f1d1d',
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {error.message}
            {'\n\n'}
            {error.stack}
          </pre>
        </details>
      )}

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          onClick={reset}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            fontSize: '1rem',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#3b82f6';
          }}
        >
          Try Again
        </button>

        <button
          onClick={() => window.location.href = '/'}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#f3f4f6',
            color: '#374151',
            border: '1px solid #d1d5db',
            borderRadius: '0.5rem',
            fontSize: '1rem',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#e5e7eb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#f3f4f6';
          }}
        >
          Go Home
        </button>
      </div>
    </div>
  );
};
