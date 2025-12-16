/**
 * Credits API
 * 
 * API client functions for credit balance and gifting.
 * 
 * @module features/marketplace/api/credits
 */

import { apiClient } from '@/api/client';

// =============================================================================
// TYPES
// =============================================================================

/** Credit balance data from API (named to avoid conflict with CreditBalance component) */
export interface CreditBalanceData {
  balance: number;
  pending: number;
  total_earned: number;
  total_spent: number;
}

export interface GiftCreditsRequest {
  recipient_user_id: number;
  amount: number;
  message?: string;
}

export interface CreditGift {
  id: number;
  sender_id: number;
  recipient_id: number;
  amount: number;
  message?: string;
  created_at: string;
}

// =============================================================================
// BALANCE API
// =============================================================================

/**
 * Get user's credit balance
 */
export async function getCreditBalance(): Promise<CreditBalanceData> {
  return apiClient.get<CreditBalanceData>('/marketplace/balance');
}

/**
 * Get balance as simple number (for quick display)
 */
export async function getBalanceSimple(): Promise<number> {
  const response = await apiClient.get<CreditBalanceData>('/marketplace/balance');
  return response.balance;
}

// =============================================================================
// GIFTING API
// =============================================================================

/**
 * Send credits as a gift
 */
export async function sendGift(request: GiftCreditsRequest): Promise<CreditGift> {
  return apiClient.post<CreditGift>('/marketplace/gift', request);
}

/**
 * Get gift history
 */
export async function getGiftHistory(type: 'sent' | 'received' | 'all' = 'all'): Promise<CreditGift[]> {
  const response = await apiClient.get<{ gifts: CreditGift[] }>('/marketplace/gifts', {
    params: { type },
  });
  return response.gifts;
}
