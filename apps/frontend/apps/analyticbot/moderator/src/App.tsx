import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from './contexts/AuthContext';
import { ROUTES } from '@config/routes';
import ErrorBoundary from './components/ErrorBoundary';

// Layouts
import ModeratorLayout from './layouts/ModeratorLayout';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CatalogPage from './pages/CatalogPage';
import CategoriesPage from './pages/CategoriesPage';
import FeaturedPage from './pages/FeaturedPage';
import ReportsPage from './pages/ReportsPage';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Public Routes */}
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />

        {/* Protected Moderator Routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <ModeratorLayout>
                <ErrorBoundary>
                  <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/catalog" element={<CatalogPage />} />
                    <Route path="/categories" element={<CategoriesPage />} />
                    <Route path="/featured" element={<FeaturedPage />} />
                    <Route path="/reports" element={<ReportsPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </ModeratorLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
};

export default App;
