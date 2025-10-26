/**
 * Service Factory
 * Provides proper service switching between real and mock implementations
 * for demo users while maintaining clean architecture
 */

interface RequestData {
    email?: string;
    username?: string;
    [key: string]: any;
}

// Check if user is in demo mode (runtime check)
export const isDemoUser = (requestData: RequestData | null = null): boolean => {
    // Check localStorage and URL for existing demo status
    const existingDemo = localStorage.getItem('is_demo_user') === 'true' ||
                        window.location.search.includes('demo=true') ||
                        window.location.hostname.includes('demo');

    // For authentication requests, also check the email in request data
    if (requestData && typeof requestData === 'object') {
        const email = requestData.email || requestData.username;
        if (email && typeof email === 'string') {
            // Only specific demo email patterns should trigger demo mode
            const validDemoPatterns = [
                'demo@analyticbot.com',
                'viewer@analyticbot.com',
                'guest@analyticbot.com',
                'admin@analyticbot.com'
            ];

            const isDemoEmail = validDemoPatterns.includes(email.toLowerCase()) ||
                               email.toLowerCase().startsWith('demo@') ||
                               email.toLowerCase().startsWith('viewer@') ||
                               email.toLowerCase().startsWith('guest@');

            if (isDemoEmail) {
                console.log('🎭 Demo email detected in request:', email);
                return true;
            } else {
                console.log('🔗 Real user email detected:', email);
                return false;
            }
        }
    }

    return existingDemo;
};

// Create a dynamic API client that checks demo status at runtime
export const apiClient = {
    get: async (url: string, config?: any) => {
        if (isDemoUser()) {
            console.log('🎭 Using mock API client for demo user');
            const mockClient = await import('@/__mocks__/services/mockApiClient');
            return mockClient.default.get(url);
        } else {
            console.log('🔗 Using real API client for production user');
            const realClient = await import('./api/apiClient');
            return realClient.apiClient.get(url, config ? config : undefined);
        }
    },

    post: async (url: string, data?: any) => {
        // Check for demo user with request data (especially for auth endpoints)
        if (isDemoUser(data)) {
            console.log('🎭 Using mock API client for demo user:', url);
            const mockClient = await import('@/__mocks__/services/mockApiClient');
            return mockClient.default.post(url, data);
        } else {
            console.log('🔗 Using real API client for production user');
            const realClient = await import('./api/apiClient');
            return realClient.apiClient.post(url, data);
        }
    },

    put: async (url: string, data?: any) => {
        if (isDemoUser()) {
            const mockClient = await import('@/__mocks__/services/mockApiClient');
            return mockClient.default.put(url, data);
        } else {
            const realClient = await import('./api/apiClient');
            return realClient.apiClient.put(url, data);
        }
    },

    delete: async (url: string) => {
        if (isDemoUser()) {
            const mockClient = await import('@/__mocks__/services/mockApiClient');
            return mockClient.default.delete(url);
        } else {
            const realClient = await import('./api/apiClient');
            return realClient.apiClient.delete(url);
        }
    },

    uploadFileDirect: async (file: File, onProgress?: ((percent: number) => void) | null) => {
        if (isDemoUser()) {
            const mockClient = await import('@/__mocks__/services/mockApiClient');
            return mockClient.default.uploadFileDirect(file, onProgress);
        } else {
            const realClient = await import('./api/apiClient');
            return (realClient.apiClient as any).uploadFileDirect(file, onProgress);
        }
    }
};

// Service factory for other services
class ServiceFactory {
    static async getChurnPredictorService() {
        if (isDemoUser()) {
            console.log('🎭 Loading mock ChurnPredictorService');
            const { default: MockChurnService } = await import('@/__mocks__/services/ChurnPredictorService');
            return MockChurnService;
        } else {
            console.log('🔗 Loading real ChurnPredictorService');
            const { default: RealChurnService } = await import('@/services/ChurnPredictorService');
            return RealChurnService;
        }
    }

    static async getPredictiveAnalyticsService() {
        if (isDemoUser()) {
            console.log('🎭 Loading mock PredictiveAnalyticsService');
            const { default: MockPredictiveService } = await import('@/__mocks__/services/PredictiveAnalyticsService');
            return MockPredictiveService;
        } else {
            console.log('🔗 Loading real PredictiveAnalyticsService');
            const { default: RealPredictiveService } = await import('@/services/PredictiveAnalyticsService');
            return RealPredictiveService;
        }
    }
}

export default ServiceFactory;
