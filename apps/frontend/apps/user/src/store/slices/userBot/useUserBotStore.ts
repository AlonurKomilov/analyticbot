/**
 * User Bot Zustand Store
 * State management for user bot operations
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  BotStatusResponse,
  CreateBotRequest,
  VerifyBotRequest,
  UpdateRateLimitRequest,
  AdminBotListItem,
} from '@/types';
import { userBotApi } from '@/services/userBotApi';

/**
 * User Bot Store State
 */
interface UserBotState {
  // Current user's bot
  bot: BotStatusResponse | null;

  // Admin: All bots
  allBots: AdminBotListItem[];
  totalBots: number;

  // Loading states
  isLoading: boolean;
  isCreating: boolean;
  isVerifying: boolean;
  isUpdating: boolean;
  isRemoving: boolean;

  // Admin loading states
  isLoadingBots: boolean;
  isSuspending: boolean;
  isActivating: boolean;

  // Error state
  error: string | null;

  // Actions
  fetchBotStatus: () => Promise<BotStatusResponse | void | null>;
  createBot: (data: CreateBotRequest) => Promise<void>;
  verifyBot: (data?: VerifyBotRequest) => Promise<void>;
  removeBot: () => Promise<void>;
  updateRateLimits: (data: UpdateRateLimitRequest) => Promise<void>;

  // Admin actions
  fetchAllBots: (params?: { limit?: number; offset?: number; status?: string }) => Promise<void>;
  suspendUserBot: (userId: number, reason: string) => Promise<void>;
  activateUserBot: (userId: number) => Promise<void>;
  updateUserBotRateLimits: (userId: number, data: UpdateRateLimitRequest) => Promise<void>;
  accessUserBot: (userId: number) => Promise<void>;

  // Utility actions
  clearError: () => void;
  reset: () => void;
}

/**
 * Initial state
 */
const initialState = {
  bot: null,
  allBots: [],
  totalBots: 0,
  isLoading: false,
  isCreating: false,
  isVerifying: false,
  isUpdating: false,
  isRemoving: false,
  isLoadingBots: false,
  isSuspending: false,
  isActivating: false,
  error: null,
};

/**
 * User Bot Store
 */
export const useUserBotStore = create<UserBotState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // ==================== User Bot Actions ====================

      /**
       * Fetch current user's bot status
       */
      fetchBotStatus: async () => {
        // Prevent duplicate calls if already loading
        const currentState = get();
        if (currentState.isLoading) {
          console.warn('Bot status fetch already in progress, skipping duplicate request');
          return currentState.bot;
        }

        set({ isLoading: true, error: null });
        try {
          const bot = await userBotApi.getBotStatus();
          set({ bot, isLoading: false });
          return bot; // Return for success detection
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch bot status';
          set({ error: errorMessage, isLoading: false, bot: null });
          throw error;
        }
      },

      /**
       * Create a new bot
       */
      createBot: async (data: CreateBotRequest) => {
        set({ isCreating: true, error: null });
        try {
          await userBotApi.createBot(data);
          // Refresh bot status after creation
          await get().fetchBotStatus();
          set({ isCreating: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to create bot';
          set({ error: errorMessage, isCreating: false });
          throw error;
        }
      },

      /**
       * Verify bot credentials
       */
      verifyBot: async (data?: VerifyBotRequest) => {
        set({ isVerifying: true, error: null });
        try {
          await userBotApi.verifyBot(data);
          // Refresh bot status after verification
          await get().fetchBotStatus();
          set({ isVerifying: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to verify bot';
          set({ error: errorMessage, isVerifying: false });
          throw error;
        }
      },

      /**
       * Remove bot
       */
      removeBot: async () => {
        set({ isRemoving: true, error: null });
        try {
          await userBotApi.removeBot();
          set({ bot: null, isRemoving: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to remove bot';
          set({ error: errorMessage, isRemoving: false });
          throw error;
        }
      },

      /**
       * Update rate limits
       */
      updateRateLimits: async (data: UpdateRateLimitRequest) => {
        set({ isUpdating: true, error: null });
        try {
          await userBotApi.updateRateLimits(data);
          // Refresh bot status after update
          await get().fetchBotStatus();
          set({ isUpdating: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to update rate limits';
          set({ error: errorMessage, isUpdating: false });
          throw error;
        }
      },

      // ==================== Admin Actions ====================

      /**
       * Fetch all bots (admin)
       */
      fetchAllBots: async (params) => {
        set({ isLoadingBots: true, error: null });
        try {
          const response = await userBotApi.listAllBots(params);
          set({
            allBots: response.bots,
            totalBots: response.total,
            isLoadingBots: false,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch bots';
          set({ error: errorMessage, isLoadingBots: false });
        }
      },

      /**
       * Suspend user bot (admin)
       */
      suspendUserBot: async (userId: number, reason: string) => {
        set({ isSuspending: true, error: null });
        try {
          await userBotApi.suspendBot(userId, { reason });
          // Refresh bot list
          await get().fetchAllBots();
          set({ isSuspending: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to suspend bot';
          set({ error: errorMessage, isSuspending: false });
          throw error;
        }
      },

      /**
       * Activate user bot (admin)
       */
      activateUserBot: async (userId: number) => {
        set({ isActivating: true, error: null });
        try {
          await userBotApi.activateBot(userId);
          // Refresh bot list
          await get().fetchAllBots();
          set({ isActivating: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to activate bot';
          set({ error: errorMessage, isActivating: false });
          throw error;
        }
      },

      /**
       * Update user bot rate limits (admin)
       */
      updateUserBotRateLimits: async (userId: number, data: UpdateRateLimitRequest) => {
        set({ isUpdating: true, error: null });
        try {
          await userBotApi.updateUserBotRateLimits(userId, data);
          // Refresh bot list
          await get().fetchAllBots();
          set({ isUpdating: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to update rate limits';
          set({ error: errorMessage, isUpdating: false });
          throw error;
        }
      },

      /**
       * Access user bot (admin)
       */
      accessUserBot: async (userId: number) => {
        set({ isLoading: true, error: null });
        try {
          await userBotApi.accessUserBot(userId);
          set({ isLoading: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to access bot';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // ==================== Utility Actions ====================

      /**
       * Clear error
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * Reset store
       */
      reset: () => {
        set(initialState);
      },
    }),
    { name: 'UserBotStore' }
  )
);

// Export store hooks
export const useBot = () => useUserBotStore((state) => state.bot);
export const useAllBots = () => useUserBotStore((state) => state.allBots);
export const useBotLoading = () => useUserBotStore((state) => state.isLoading);
export const useBotError = () => useUserBotStore((state) => state.error);
