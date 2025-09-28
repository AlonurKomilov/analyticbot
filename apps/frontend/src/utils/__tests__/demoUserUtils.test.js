import { describe, it, expect, beforeEach, vi } from 'vitest';
import { isDemoUser, getDemoAwareDataProvider, markUserAsDemo, clearDemoStatus } from '../demoUserUtils.js';

// Mock localStorage
const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
};
global.localStorage = localStorageMock;

describe('Demo User Utils', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorageMock.getItem.mockReturnValue(null);
    });

    describe('isDemoUser', () => {
        it('should return false when no demo flag is set', () => {
            localStorageMock.getItem.mockReturnValue(null);
            expect(isDemoUser()).toBe(false);
        });

        it('should return true when demo flag is set to "true"', () => {
            localStorageMock.getItem.mockReturnValue('true');
            expect(isDemoUser()).toBe(true);
        });

        it('should return false when demo flag is set to "false"', () => {
            localStorageMock.getItem.mockReturnValue('false');
            expect(isDemoUser()).toBe(false);
        });
    });

    describe('markUserAsDemo', () => {
        it('should set localStorage demo flag to "true"', () => {
            markUserAsDemo();
            expect(localStorageMock.setItem).toHaveBeenCalledWith('is_demo_user', 'true');
        });
    });

    describe('clearDemoStatus', () => {
        it('should remove demo flag from localStorage', () => {
            clearDemoStatus();
            expect(localStorageMock.removeItem).toHaveBeenCalledWith('is_demo_user');
        });
    });

    describe('getDemoAwareDataProvider', () => {
        it('should return a provider for regular users', async () => {
            localStorageMock.getItem.mockReturnValue(null);
            const provider = await getDemoAwareDataProvider();
            expect(provider).toBeDefined();
            expect(typeof provider.getAnalyticsOverview).toBe('function');
        });

        it('should return a provider for demo users', async () => {
            localStorageMock.getItem.mockReturnValue('true');
            const provider = await getDemoAwareDataProvider();
            expect(provider).toBeDefined();
            expect(typeof provider.getAnalyticsOverview).toBe('function');
        });
    });
});