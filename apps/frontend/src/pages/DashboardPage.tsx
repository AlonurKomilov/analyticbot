/**
 * DashboardPage Component
 *
 * Main dashboard/home page showing quick overview and navigation.
 * Different from AnalyticsPage which shows detailed analytics.
 *
 * Updated: December 2025
 * - Changed to HomeDashboard for quick overview
 * - Analytics moved to dedicated /analytics route
 */

import React from 'react';
import HomeDashboard from './HomeDashboard';

const DashboardPage: React.FC = () => {
    return <HomeDashboard />;
};

export default DashboardPage;
