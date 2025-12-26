import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '@contexts/AuthContext';
import { ROUTES } from '@config/routes';
import ErrorBoundary from '@components/ErrorBoundary';

// Layouts
import OwnerLayout from '@layouts/OwnerLayout';

// Pages
import LoginPage from '@pages/LoginPage';
import DashboardPage from '@pages/DashboardPage';
import UsersPage from '@pages/UsersPage';
import ProjectsPage from '@pages/ProjectsPage';
import SystemPage from '@pages/SystemPage';
import SystemHealthPage from '@pages/SystemHealthPage';
import DatabasePage from '@pages/DatabasePage';
import AuditLogPage from '@pages/AuditLogPage';
import SettingsPage from '@pages/SettingsPage';

// Infrastructure Pages
import InfrastructurePage from '@pages/infrastructure/InfrastructurePage';
import ClustersPage from '@pages/infrastructure/ClustersPage';
import NodesPage from '@pages/infrastructure/NodesPage';
import DeploymentsPage from '@pages/infrastructure/DeploymentsPage';
import PodsPage from '@pages/infrastructure/PodsPage';
import ServicesPage from '@pages/infrastructure/ServicesPage';
import IngressPage from '@pages/infrastructure/IngressPage';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', bgcolor: 'background.default' }}>
        <CircularProgress color="primary" />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  // Only owners can access this panel
  if (user?.role !== 'owner') {
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

        {/* Protected Owner Routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <OwnerLayout>
                <ErrorBoundary>
                  <Routes>
                    {/* Main Dashboard */}
                    <Route path="/" element={<DashboardPage />} />
                    
                    {/* Platform Management */}
                    <Route path="/users" element={<UsersPage />} />
                    <Route path="/projects" element={<ProjectsPage />} />
                    
                    {/* System Management */}
                    <Route path="/system" element={<SystemPage />} />
                    <Route path="/system/health" element={<SystemHealthPage />} />
                    <Route path="/database" element={<DatabasePage />} />
                    <Route path="/audit" element={<AuditLogPage />} />
                    
                    {/* Infrastructure / K8s Management */}
                    <Route path="/infrastructure" element={<InfrastructurePage />} />
                    <Route path="/infrastructure/clusters" element={<ClustersPage />} />
                    <Route path="/infrastructure/nodes" element={<NodesPage />} />
                    <Route path="/infrastructure/deployments" element={<DeploymentsPage />} />
                    <Route path="/infrastructure/pods" element={<PodsPage />} />
                    <Route path="/infrastructure/services" element={<ServicesPage />} />
                    <Route path="/infrastructure/ingress" element={<IngressPage />} />
                    
                    {/* Settings */}
                    <Route path="/settings" element={<SettingsPage />} />
                    
                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </OwnerLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
};

export default App;
