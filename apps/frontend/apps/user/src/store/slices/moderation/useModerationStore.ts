/**
 * User Bot Moderation Zustand Store
 * State management for moderation features
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  ChatSettings,
  ChatSettingsUpdate,
  BannedWord,
  BannedWordCreate,
  WelcomeMessage,
  WelcomeMessageUpsert,
  InviteStats,
  ModerationLogResponse,
  ModerationChatItem,
} from '@/types';
import { userBotServiceApi } from '@/services/userBotServiceApi';

/**
 * Moderation Store State
 */
interface ModerationState {
  // Current chat
  selectedChatId: number | null;
  
  // Configured chats list
  configuredChats: ModerationChatItem[];
  
  // Current chat settings
  settings: ChatSettings | null;
  
  // Banned words for current chat
  bannedWords: BannedWord[];
  
  // Welcome messages
  welcomeMessage: WelcomeMessage | null;
  goodbyeMessage: WelcomeMessage | null;
  
  // Invite stats
  inviteStats: InviteStats | null;
  
  // Moderation log
  moderationLog: ModerationLogResponse | null;
  
  // Loading states
  isLoading: boolean;
  isLoadingChats: boolean;
  isLoadingSettings: boolean;
  isLoadingBannedWords: boolean;
  isLoadingWelcome: boolean;
  isLoadingInvites: boolean;
  isLoadingLog: boolean;
  isSaving: boolean;
  
  // Error state
  error: string | null;
  
  // Actions
  setSelectedChat: (chatId: number | null) => void;
  fetchConfiguredChats: () => Promise<void>;
  fetchSettings: (chatId: number) => Promise<void>;
  updateSettings: (chatId: number, settings: ChatSettingsUpdate) => Promise<void>;
  deleteSettings: (chatId: number) => Promise<void>;
  
  // Banned words actions
  fetchBannedWords: (chatId: number) => Promise<void>;
  addBannedWord: (chatId: number, word: BannedWordCreate) => Promise<void>;
  deleteBannedWord: (chatId: number, wordId: number) => Promise<void>;
  bulkAddBannedWords: (chatId: number, words: BannedWordCreate[]) => Promise<void>;
  
  // Welcome message actions
  fetchWelcomeMessage: (chatId: number, type: 'welcome' | 'goodbye') => Promise<void>;
  updateWelcomeMessage: (chatId: number, data: WelcomeMessageUpsert) => Promise<void>;
  deleteWelcomeMessage: (chatId: number, type: 'welcome' | 'goodbye') => Promise<void>;
  
  // Invite stats actions
  fetchInviteStats: (chatId: number) => Promise<void>;
  
  // Moderation log actions
  fetchModerationLog: (chatId: number, page?: number) => Promise<void>;
  
  // Utility actions
  clearError: () => void;
  reset: () => void;
}

/**
 * Initial state
 */
const initialState = {
  selectedChatId: null,
  configuredChats: [],
  settings: null,
  bannedWords: [],
  welcomeMessage: null,
  goodbyeMessage: null,
  inviteStats: null,
  moderationLog: null,
  isLoading: false,
  isLoadingChats: false,
  isLoadingSettings: false,
  isLoadingBannedWords: false,
  isLoadingWelcome: false,
  isLoadingInvites: false,
  isLoadingLog: false,
  isSaving: false,
  error: null,
};

/**
 * Moderation Store
 */
export const useModerationStore = create<ModerationState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setSelectedChat: (chatId) => {
        set({ selectedChatId: chatId });
        if (chatId) {
          // Load all data for selected chat
          get().fetchSettings(chatId);
          get().fetchBannedWords(chatId);
          get().fetchWelcomeMessage(chatId, 'welcome');
          get().fetchWelcomeMessage(chatId, 'goodbye');
          get().fetchInviteStats(chatId);
          get().fetchModerationLog(chatId);
        }
      },

      fetchConfiguredChats: async () => {
        set({ isLoadingChats: true, error: null });
        try {
          const chats = await userBotServiceApi.getConfiguredChats();
          set({ configuredChats: chats, isLoadingChats: false });
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to fetch configured chats',
            isLoadingChats: false,
          });
        }
      },

      fetchSettings: async (chatId) => {
        set({ isLoadingSettings: true, error: null });
        try {
          const settings = await userBotServiceApi.getChatSettings(chatId);
          set({ settings, isLoadingSettings: false });
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to fetch settings',
            isLoadingSettings: false,
          });
        }
      },

      updateSettings: async (chatId, settingsUpdate) => {
        set({ isSaving: true, error: null });
        try {
          const settings = await userBotServiceApi.upsertChatSettings(
            chatId,
            settingsUpdate
          );
          set({ settings, isSaving: false });
          
          // Refresh configured chats list
          get().fetchConfiguredChats();
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to update settings',
            isSaving: false,
          });
          throw error;
        }
      },

      deleteSettings: async (chatId) => {
        set({ isSaving: true, error: null });
        try {
          await userBotServiceApi.deleteChatSettings(chatId);
          set({ settings: null, isSaving: false });
          
          // Refresh configured chats list
          get().fetchConfiguredChats();
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to delete settings',
            isSaving: false,
          });
          throw error;
        }
      },

      // Banned Words
      fetchBannedWords: async (chatId) => {
        set({ isLoadingBannedWords: true });
        try {
          const bannedWords = await userBotServiceApi.getBannedWords(chatId);
          set({ bannedWords, isLoadingBannedWords: false });
        } catch (error: any) {
          set({ bannedWords: [], isLoadingBannedWords: false });
        }
      },

      addBannedWord: async (chatId, word) => {
        set({ isSaving: true, error: null });
        try {
          const newWord = await userBotServiceApi.addBannedWord(chatId, word);
          set((state) => ({
            bannedWords: [...state.bannedWords, newWord],
            isSaving: false,
          }));
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to add banned word',
            isSaving: false,
          });
          throw error;
        }
      },

      deleteBannedWord: async (chatId, wordId) => {
        set({ isSaving: true, error: null });
        try {
          await userBotServiceApi.deleteBannedWord(chatId, wordId);
          set((state) => ({
            bannedWords: state.bannedWords.filter((w) => w.id !== wordId),
            isSaving: false,
          }));
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to delete banned word',
            isSaving: false,
          });
          throw error;
        }
      },

      bulkAddBannedWords: async (chatId, words) => {
        set({ isSaving: true, error: null });
        try {
          const newWords = await userBotServiceApi.bulkAddBannedWords(
            chatId,
            words
          );
          set((state) => ({
            bannedWords: [...state.bannedWords, ...newWords],
            isSaving: false,
          }));
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to add banned words',
            isSaving: false,
          });
          throw error;
        }
      },

      // Welcome Messages
      fetchWelcomeMessage: async (chatId, type) => {
        set({ isLoadingWelcome: true });
        try {
          const message = await userBotServiceApi.getWelcomeMessage(
            chatId,
            type
          );
          if (type === 'welcome') {
            set({ welcomeMessage: message, isLoadingWelcome: false });
          } else {
            set({ goodbyeMessage: message, isLoadingWelcome: false });
          }
        } catch (error: any) {
          set({ isLoadingWelcome: false });
        }
      },

      updateWelcomeMessage: async (chatId, data) => {
        set({ isSaving: true, error: null });
        try {
          const message = await userBotServiceApi.upsertWelcomeMessage(
            chatId,
            data
          );
          if (data.message_type === 'welcome') {
            set({ welcomeMessage: message, isSaving: false });
          } else {
            set({ goodbyeMessage: message, isSaving: false });
          }
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to update welcome message',
            isSaving: false,
          });
          throw error;
        }
      },

      deleteWelcomeMessage: async (chatId, type) => {
        set({ isSaving: true, error: null });
        try {
          await userBotServiceApi.deleteWelcomeMessage(chatId, type);
          if (type === 'welcome') {
            set({ welcomeMessage: null, isSaving: false });
          } else {
            set({ goodbyeMessage: null, isSaving: false });
          }
        } catch (error: any) {
          set({
            error: error?.message || 'Failed to delete welcome message',
            isSaving: false,
          });
          throw error;
        }
      },

      // Invite Stats
      fetchInviteStats: async (chatId) => {
        set({ isLoadingInvites: true });
        try {
          const stats = await userBotServiceApi.getInviteStats(chatId);
          set({ inviteStats: stats, isLoadingInvites: false });
        } catch (error: any) {
          set({ inviteStats: null, isLoadingInvites: false });
        }
      },

      // Moderation Log
      fetchModerationLog: async (chatId, page = 1) => {
        set({ isLoadingLog: true });
        try {
          const log = await userBotServiceApi.getModerationLog(chatId, page);
          set({ moderationLog: log, isLoadingLog: false });
        } catch (error: any) {
          set({ moderationLog: null, isLoadingLog: false });
        }
      },

      clearError: () => set({ error: null }),

      reset: () => set(initialState),
    }),
    { name: 'moderation-store' }
  )
);
