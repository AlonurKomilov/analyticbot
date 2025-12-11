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
  setupMTProtoSimple,
  resendMTProto,
  verifyMTProto,
  disconnectMTProto,
  removeMTProto,
  requestQRLogin,
  checkQRLoginStatus,
  submitQR2FA,
} from '@/features/mtproto-setup/api';
import type {
  MTProtoSetupRequest,
  MTProtoVerifyRequest,
  MTProtoStatusResponse,
  MTProtoQRLoginResponse,
  MTProtoQRStatusResponse,
} from '@/features/mtproto-setup/types';

/**
 * MTProto Store State
 */
interface MTProtoState {
  // Status data
  status: MTProtoStatusResponse | null;

  // Phone code hash from setup (needed for verification)
  phoneCodeHash: string | null;
  // Last setup payload (so user can resend code without retyping credentials)
  lastSetupData: MTProtoSetupRequest | null;

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
  setupSimple: (phone: string) => Promise<string | null>; // Simple setup - phone only
  // Resend last setup request (re-send verification code using last entered credentials)
  resendSetup: () => Promise<string | null>;
  verify: (data: MTProtoVerifyRequest) => Promise<void>;
  disconnect: () => Promise<void>;
  remove: () => Promise<void>;
  
  // QR Code Login actions
  requestQRLogin: () => Promise<MTProtoQRLoginResponse | null>;
  checkQRStatus: () => Promise<MTProtoQRStatusResponse | null>;
  submitQR2FA: (password: string) => Promise<MTProtoQRStatusResponse | null>;

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
  lastSetupData: null,
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
          // store last setup payload so user can easily resend code
          set({ lastSetupData: data });
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
       * Simple MTProto setup - only requires phone number
       */
      setupSimple: async (phone: string) => {
        set({ isSettingUp: true, error: null });
        try {
          const response = await setupMTProtoSimple(phone);
          set({
            phoneCodeHash: response.phone_code_hash,
            isSettingUp: false
          });
          toast.success('📱 Verification code sent to your Telegram!');
          return response.phone_code_hash;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to setup MTProto';
          set({ error: errorMessage, isSettingUp: false });
          toast.error(`❌ ${errorMessage}`);
          return null;
        }
      },

      /**
       * Resend verification code using dedicated backend endpoint
       */
      resendSetup: async () => {
        set({ isSettingUp: true, error: null });
        try {
          const response = await resendMTProto();
          set({ phoneCodeHash: response.phone_code_hash, isSettingUp: false });
          toast.success('📱 Verification code re-sent to your phone!');
          return response.phone_code_hash;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to resend verification code';
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
          const errorLower = errorMessage.toLowerCase();
          
          // Check if this is a 2FA error - don't show toast for this, let component handle it
          const is2FAError = 
            errorLower.includes('2fa') || 
            errorLower.includes('password') ||
            errorLower.includes('two-factor');
          
          set({ error: is2FAError ? null : errorMessage, isVerifying: false });
          
          // Only show toast for non-2FA errors
          if (!is2FAError) {
            toast.error(`❌ ${errorMessage}`);
          }
          
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

      /**
       * Request QR code for login
       */
      requestQRLogin: async () => {
        set({ isSettingUp: true, error: null });
        try {
          const response = await requestQRLogin();
          set({ isSettingUp: false });
          return response;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate QR code';
          set({ error: errorMessage, isSettingUp: false });
          return null;
        }
      },

      /**
       * Check QR login status
       */
      checkQRStatus: async () => {
        try {
          const response = await checkQRLoginStatus();
          if (response.status === 'success') {
            // Refresh status after successful QR login
            const status = await getMTProtoStatus();
            set({ status });
            toast.success('✅ QR login successful!');
          }
          return response;
        } catch (error: any) {
          // Don't show error toast for polling - it's expected to have some failures
          return null;
        }
      },

      /**
       * Submit 2FA password for QR login
       */
      submitQR2FA: async (password: string) => {
        set({ isVerifying: true, error: null });
        try {
          const response = await submitQR2FA(password);
          set({ isVerifying: false });
          
          if (response.status === 'success') {
            // Refresh status after successful login
            const status = await getMTProtoStatus();
            set({ status });
            toast.success('✅ Login successful with 2FA!');
          } else if (response.status === '2fa_required' && response.message.includes('Invalid')) {
            toast.error('❌ Invalid password. Please try again.');
          }
          
          return response;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Failed to verify 2FA';
          set({ error: errorMessage, isVerifying: false });
          toast.error(`❌ ${errorMessage}`);
          return null;
        }
      },
    }),
    { name: 'MTProtoStore' }
  )
);

// Convenience hooks for specific state slices
export const useMTProtoStatus = () => useMTProtoStore((state) => state.status);
export const useMTProtoLoading = () => useMTProtoStore((state) => state.isLoading);
export const useMTProtoError = () => useMTProtoStore((state) => state.error);
