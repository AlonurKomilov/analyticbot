import axios, { AxiosInstance } from 'axios';
import { config } from '@config/index';
import { API_ROUTES } from '@config/routes';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('owner_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('owner_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const ownerApi = {
  // Auth
  login: (username: string, password: string) =>
    api.post(API_ROUTES.LOGIN, { username, password }),
  logout: () => api.post(API_ROUTES.LOGOUT),
  getMe: () => api.get(API_ROUTES.ME),

  // Users
  getUsers: (params?: { page?: number; limit?: number; search?: string }) =>
    api.get(API_ROUTES.USERS, { params }),
  suspendUser: (id: number) => api.post(API_ROUTES.USER_SUSPEND(id)),
  reactivateUser: (id: number) => api.post(API_ROUTES.USER_REACTIVATE(id)),

  // System
  getSystemStats: () => api.get(API_ROUTES.SYSTEM_STATS),
  getSystemHealth: () => api.get(API_ROUTES.SYSTEM_HEALTH),
  getConfig: () => api.get(API_ROUTES.SYSTEM_CONFIG),
  updateConfig: (key: string, value: any) =>
    api.put(API_ROUTES.SYSTEM_CONFIG, { key, value }),

  // Database
  getDatabaseStats: () => api.get(API_ROUTES.DATABASE_STATS),
  createBackup: (includeData: boolean = true) =>
    api.post(API_ROUTES.DATABASE_BACKUP, { include_data: includeData }),
  executeQuery: (query: string) =>
    api.post(API_ROUTES.DATABASE_QUERY, { query }),

  // Audit
  getAuditLogs: (params?: { page?: number; limit?: number; action?: string }) =>
    api.get(API_ROUTES.AUDIT_LOGS, { params }),

  // Infrastructure / K8s
  getClusters: () => api.get(API_ROUTES.K8S_CLUSTERS),
  getNodes: (clusterId?: string) =>
    api.get(API_ROUTES.K8S_NODES, { params: { cluster_id: clusterId } }),
  getDeployments: (namespace?: string) =>
    api.get(API_ROUTES.K8S_DEPLOYMENTS, { params: { namespace } }),
  getPods: (namespace?: string, deployment?: string) =>
    api.get(API_ROUTES.K8S_PODS, { params: { namespace, deployment } }),
  getServices: (namespace?: string) =>
    api.get(API_ROUTES.K8S_SERVICES, { params: { namespace } }),
  getIngress: (namespace?: string) =>
    api.get(API_ROUTES.K8S_INGRESS, { params: { namespace } }),
  getK8sMetrics: () => api.get(API_ROUTES.K8S_METRICS),
  getK8sLogs: (podName: string, namespace: string, container?: string) =>
    api.get(API_ROUTES.K8S_LOGS, { params: { pod: podName, namespace, container } }),

  // K8s Actions
  scaleDeployment: (namespace: string, name: string, replicas: number) =>
    api.post(`${API_ROUTES.K8S_DEPLOYMENTS}/${namespace}/${name}/scale`, { replicas }),
  restartDeployment: (namespace: string, name: string) =>
    api.post(`${API_ROUTES.K8S_DEPLOYMENTS}/${namespace}/${name}/restart`),
  deletePod: (namespace: string, name: string) =>
    api.delete(`${API_ROUTES.K8S_PODS}/${namespace}/${name}`),
};

export default api;
