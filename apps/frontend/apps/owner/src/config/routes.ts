export const ROUTES = {
  // Auth
  LOGIN: '/login',
  
  // Main
  DASHBOARD: '/',
  
  // Platform Management
  USERS: '/users',
  PROJECTS: '/projects',
  
  // System
  SYSTEM: '/system',
  SYSTEM_HEALTH: '/system/health',
  DATABASE: '/database',
  AUDIT: '/audit',
  
  // Infrastructure
  INFRASTRUCTURE: '/infrastructure',
  CLUSTERS: '/infrastructure/clusters',
  NODES: '/infrastructure/nodes',
  DEPLOYMENTS: '/infrastructure/deployments',
  PODS: '/infrastructure/pods',
  SERVICES: '/infrastructure/services',
  INGRESS: '/infrastructure/ingress',
  
  // Settings
  SETTINGS: '/settings',
} as const;

export const API_ROUTES = {
  // Auth
  LOGIN: '/owner/auth/login',
  LOGOUT: '/owner/auth/logout',
  ME: '/owner/auth/me',
  
  // Users
  USERS: '/owner/users',
  USER_SUSPEND: (id: number) => `/owner/users/${id}/suspend`,
  USER_REACTIVATE: (id: number) => `/owner/users/${id}/reactivate`,
  
  // System
  SYSTEM_STATS: '/owner/stats',
  SYSTEM_HEALTH: '/owner/system/health',
  SYSTEM_CONFIG: '/owner/config',
  
  // Database
  DATABASE_STATS: '/owner/database/stats',
  DATABASE_BACKUP: '/owner/database/backup',
  DATABASE_QUERY: '/owner/database/query',
  
  // Audit
  AUDIT_LOGS: '/owner/audit-logs',
  
  // Infrastructure / K8s
  K8S_CLUSTERS: '/owner/k8s/clusters',
  K8S_NODES: '/owner/k8s/nodes',
  K8S_DEPLOYMENTS: '/owner/k8s/deployments',
  K8S_PODS: '/owner/k8s/pods',
  K8S_SERVICES: '/owner/k8s/services',
  K8S_INGRESS: '/owner/k8s/ingress',
  K8S_METRICS: '/owner/k8s/metrics',
  K8S_LOGS: '/owner/k8s/logs',
} as const;
