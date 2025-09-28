/**
 * Service Factory
 * Provides proper service switching between real and mock implementations
 * for demo users while maintaining clean architecture
 */

// Check if user is in demo mode (runtime check)
export const isDemoUser = (requestData = null) => {
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
    get: async (url, config) => {
        if (isDemoUser()) {
            console.log('🎭 Using mock API client for demo user');
            const mockClient = await import('../__mocks__/services/mockApiClient.js');
            return mockClient.default.get(url, config);
        } else {
            console.log('🔗 Using real API client for production user');
            const realClient = await import('./apiClient.js');
            return realClient.default.get(url, config);
        }
    },
    
    post: async (url, data, config) => {
        // Check for demo user with request data (especially for auth endpoints)
        if (isDemoUser(data)) {
            console.log('🎭 Using mock API client for demo user:', url);
            const mockClient = await import('../__mocks__/services/mockApiClient.js');
            return mockClient.default.post(url, data, config);
        } else {
            console.log('🔗 Using real API client for production user');
            const realClient = await import('./apiClient.js');
            return realClient.default.post(url, data, config);
        }
    },
    
    put: async (url, data, config) => {
        if (isDemoUser()) {
            const mockClient = await import('../__mocks__/services/mockApiClient.js');
            return mockClient.default.put(url, data, config);
        } else {
            const realClient = await import('./apiClient.js');
            return realClient.default.put(url, data, config);
        }
    },
    
    delete: async (url, config) => {
        if (isDemoUser()) {
            const mockClient = await import('../__mocks__/services/mockApiClient.js');
            return mockClient.default.delete(url, config);
        } else {
            const realClient = await import('./apiClient.js');
            return realClient.default.delete(url, config);
        }
    },
    
    uploadFileDirect: async (file, onProgress) => {
        if (isDemoUser()) {
            const mockClient = await import('../__mocks__/services/mockApiClient.js');
            return mockClient.default.uploadFileDirect(file, onProgress);
        } else {
            const realClient = await import('./apiClient.js');
            return realClient.default.uploadFileDirect(file, onProgress);
        }
    }
};

// Service factory for other services
class ServiceFactory {
    static async getChurnPredictorService() {
        if (isDemoUser()) {
            console.log('🎭 Loading mock ChurnPredictorService');
            const { default: MockChurnService } = await import('../__mocks__/services/ChurnPredictorService.jsx');
            return MockChurnService;
        } else {
            console.log('🔗 Loading real ChurnPredictorService');
            const { default: RealChurnService } = await import('./ChurnPredictorService.jsx');
            return RealChurnService;
        }
    }

    static async getPredictiveAnalyticsService() {
        if (isDemoUser()) {
            console.log('🎭 Loading mock PredictiveAnalyticsService');
            const { default: MockPredictiveService } = await import('../__mocks__/services/PredictiveAnalyticsService.jsx');
            return MockPredictiveService;
        } else {
            console.log('🔗 Loading real PredictiveAnalyticsService');
            const { default: RealPredictiveService } = await import('./PredictiveAnalyticsService.jsx');
            return RealPredictiveService;
        }
    }
}

export default ServiceFactory;