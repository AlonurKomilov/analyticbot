import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from './contexts/AuthContext';
import { ROUTES } from '@config/routes';
import ErrorBoundary from './components/ErrorBoundary';

// Layouts
import AdminLayout from './layouts/AdminLayout';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import ChannelsPage from './pages/ChannelsPage';
import BotsPage from './pages/BotsPage';
import MTProtoPage from './pages/MTProtoPage';
import PlansPage from './pages/PlansPage';
import SystemHealthPage from './pages/SystemHealthPage';
import AuditLogPage from './pages/AuditLogPage';
import SettingsPage from './pages/SettingsPage';

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

        {/* Protected Admin Routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AdminLayout>
                <ErrorBoundary>
                  <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/users" element={<UsersPage />} />
                    <Route path="/channels" element={<ChannelsPage />} />
                    <Route path="/bots" element={<BotsPage />} />
                    <Route path="/mtproto" element={<MTProtoPage />} />
                    <Route path="/plans" element={<PlansPage />} />
                    <Route path="/system/health" element={<SystemHealthPage />} />
                    <Route path="/system/audit" element={<AuditLogPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </AdminLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
};

export default App;
