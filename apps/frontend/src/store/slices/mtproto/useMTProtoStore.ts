/**
 * MTProto Zustand Store
 * State management for MTProto setup operations
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import toast from 'react-hot-toast';
import {
  getMTProtoStatus,
  setupMTProto,
  verifyMTProto,
  disconnectMTProto,
  removeMTProto,
} from '@/features/mtproto-setup/api';
import type {
  MTProtoSetupRequest,
  MTProtoVerifyRequest,
  MTProtoStatusResponse,
} from '@/features/mtproto-setup/types';

/**
 * MTProto Store State
 */
interface MTProtoState {
  // Status data
  status: MTProtoStatusResponse | null;

  // Phone code hash from setup (needed for verification)
  phoneCodeHash: string | null;

  // Loading states
  isLoading: boolean;
  isSettingUp: boolean;
  isVerifying: boolean;
  isDisconnecting: boolean;
  isRemoving: boolean;

  // Error state
  error: string | null;

  // Actions
  fetchStatus: () => Promise<void>;
  setup: (data: MTProtoSetupRequest) => Promise<string | null>; // Returns phone_code_hash
  verify: (data: MTProtoVerifyRequest) => Promise<void>;
  disconnect: () => Promise<void>;
  remove: () => Promise<void>;

  // Utility actions
  clearError: () => void;
  reset: () => void;
}

/**
 * Initial state
 */
const initialState = {
  status: null,
  phoneCodeHash: null,
  isLoading: false,
  isSettingUp: false,
  isVerifying: false,
  isDisconnecting: false,
  isRemoving: false,
  error: null,
};

/**
 * MTProto Store
 */
export const useMTProtoStore = create<MTProtoState>()(
  devtools(
    (set) => ({
      ...initialState,

      /**
       * Fetch MTProto status
       */
      fetchStatus: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await getMTProtoStatus();
          set({ status: response, isLoading: false });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch MTProto status';
          set({ error: errorMessage, isLoading: false });
        }
      },

      /**
       * Setup MTProto (initiates verification flow)
       */
      setup: async (data: MTProtoSetupRequest) => {
        set({ isSettingUp: true, error: null });
        try {
          const response = await setupMTProto(data);
          set({
            phoneCodeHash: response.phone_code_hash,
            isSettingUp: false
          });
          toast.success('📱 Verification code sent to your phone!');
          return response.phone_code_hash;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to setup MTProto';
          set({ error: errorMessage, isSettingUp: false });
          toast.error(`❌ ${errorMessage}`);
          return null;
        }
      },

      /**
       * Verify MTProto with code
       */
      verify: async (data: MTProtoVerifyRequest) => {
        set({ isVerifying: true, error: null });
        try {
          await verifyMTProto(data);
          set({ isVerifying: false, phoneCodeHash: null });
          toast.success('✅ MTProto setup completed successfully!');

          // Refresh status
          const response = await getMTProtoStatus();
          set({ status: response });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to verify MTProto';
          set({ error: errorMessage, isVerifying: false });
          toast.error(`❌ ${errorMessage}`);
          throw error; // Re-throw for component handling (2FA detection)
        }
      },

      /**
       * Disconnect MTProto
       */
      disconnect: async () => {
        set({ isDisconnecting: true, error: null });
        try {
          await disconnectMTProto();
          set({ isDisconnecting: false });
          toast.success('✅ MTProto disconnected successfully');

          // Refresh status
          const response = await getMTProtoStatus();
          set({ status: response });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to disconnect MTProto';
          set({ error: errorMessage, isDisconnecting: false });
          toast.error(`❌ ${errorMessage}`);
        }
      },

      /**
       * Remove MTProto configuration
       */
      remove: async () => {
        set({ isRemoving: true, error: null });
        try {
          await removeMTProto();
          set({
            isRemoving: false,
            status: null,
            phoneCodeHash: null
          });
          toast.success('✅ MTProto configuration removed successfully');
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to remove MTProto';
          set({ error: errorMessage, isRemoving: false });
          toast.error(`❌ ${errorMessage}`);
        }
      },

      /**
       * Clear error
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * Reset store to initial state
       */
      reset: () => {
        set(initialState);
      },
    }),
    { name: 'MTProtoStore' }
  )
);

// Convenience hooks for specific state slices
export const useMTProtoStatus = () => useMTProtoStore((state) => state.status);
export const useMTProtoLoading = () => useMTProtoStore((state) => state.isLoading);
export const useMTProtoError = () => useMTProtoStore((state) => state.error);
