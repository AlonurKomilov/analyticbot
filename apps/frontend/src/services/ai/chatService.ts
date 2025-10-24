/**
 * AI Chat Service
 * 
 * Conversational analytics interface with natural language processing.
 * Integrates with backend /ai/chat/* endpoints.
 * 
 * Features:
 * - Natural language question processing
 * - Intent recognition
 * - Contextual analytics responses
 * - Interactive analytics exploration
 * - Conversation history
 */

import apiClient from '../apiClient';

export interface ChatQuestionRequest {
    channel_id: number;
    question: string;
    context?: Record<string, any>;
    include_follow_ups?: boolean;
}

export interface IntentDetection {
    intent_type: string;
    confidence: number;
    entities: Record<string, any>;
    parameters: Record<string, any>;
}

export interface VisualizationSuggestion {
    chart_type: string;
    data_points: string[];
    title: string;
    description: string;
}

export interface ChatQuestionResponse {
    user_question: string;
    ai_response: string;
    intent_detected: IntentDetection;
    data_sources: string[];
    confidence: number;
    follow_up_suggestions?: string[];
    response_type: string;
    timestamp: string;
    visualization_suggestions?: VisualizationSuggestion[];
}

export interface ChatConversation {
    conversation_id: string;
    channel_id: number;
    messages: ChatMessage[];
    created_at: string;
    updated_at: string;
}

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

export interface ChatHistoryResponse {
    channel_id: number;
    conversations: ChatConversation[];
    total_questions: number;
    date_range: {
        start: string;
        end: string;
    };
}

export interface QuickInsightRequest {
    channel_id: number;
    insight_type?: 'summary' | 'performance' | 'trending' | 'comparison';
}

export interface QuickInsightResponse {
    channel_id: number;
    insight_type: string;
    insight_text: string;
    key_metrics: Record<string, any>;
    recommendations: string[];
    timestamp: string;
}

export interface SuggestedQuestionsResponse {
    channel_id: number;
    categories: Record<string, string[]>;
    popular_questions: string[];
    personalized_suggestions: string[];
}

export interface ServiceHealthResponse {
    service_name: string;
    status: 'healthy' | 'degraded' | 'down';
    version: string;
    uptime: number;
    last_check: string;
}

/**
 * AI Chat Service Class
 */
class AIChatService {
    private baseURL = '/ai/chat';

    /**
     * Ask a natural language question about analytics
     * 
     * @param channelId - Channel ID for context
     * @param question - User's natural language question
     * @param context - Optional context from previous questions
     * @param includeFollowUps - Whether to include follow-up suggestions
     * @returns AI response with intent detection and suggestions
     */
    async askQuestion(
        channelId: number,
        question: string,
        context?: Record<string, any>,
        includeFollowUps: boolean = true
    ): Promise<ChatQuestionResponse> {
        try {
            const response = await apiClient.post<ChatQuestionResponse>(
                `${this.baseURL}/ask`,
                {
                    channel_id: channelId,
                    question,
                    context,
                    include_follow_ups: includeFollowUps
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to process chat question:', error);
            throw error;
        }
    }

    /**
     * Get chat history for a channel
     * 
     * @param channelId - Channel ID
     * @param limit - Maximum number of conversations to return
     * @returns Chat history with conversations
     */
    async getChatHistory(
        channelId: number,
        limit: number = 50
    ): Promise<ChatHistoryResponse> {
        try {
            const response = await apiClient.get<ChatHistoryResponse>(
                `${this.baseURL}/history/${channelId}`,
                { params: { limit } }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get chat history:', error);
            throw error;
        }
    }

    /**
     * Get quick insight about channel performance
     * 
     * @param channelId - Channel ID
     * @param insightType - Type of insight to generate
     * @returns Quick insight with key metrics
     */
    async getQuickInsight(
        channelId: number,
        insightType: 'summary' | 'performance' | 'trending' | 'comparison' = 'summary'
    ): Promise<QuickInsightResponse> {
        try {
            const response = await apiClient.post<QuickInsightResponse>(
                `${this.baseURL}/quick-insight`,
                {
                    channel_id: channelId,
                    insight_type: insightType
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get quick insight:', error);
            throw error;
        }
    }

    /**
     * Get suggested questions for user
     * 
     * @param channelId - Channel ID
     * @returns Categorized question suggestions
     */
    async getSuggestedQuestions(channelId: number): Promise<SuggestedQuestionsResponse> {
        try {
            const response = await apiClient.get<SuggestedQuestionsResponse>(
                `${this.baseURL}/suggested-questions/${channelId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get suggested questions:', error);
            throw error;
        }
    }

    /**
     * Clear chat history for a channel
     * 
     * @param channelId - Channel ID
     * @returns Success message
     */
    async clearHistory(channelId: number): Promise<{ message: string }> {
        try {
            const response = await apiClient.delete<{ message: string }>(
                `${this.baseURL}/history/${channelId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to clear chat history:', error);
            throw error;
        }
    }

    /**
     * Get AI chat service health status
     * 
     * @returns Service health information
     */
    async getServiceHealth(): Promise<ServiceHealthResponse> {
        try {
            const response = await apiClient.get<ServiceHealthResponse>(
                `${this.baseURL}/health`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get service health:', error);
            throw error;
        }
    }

    /**
     * Export chat conversation
     * 
     * @param conversationId - Conversation ID to export
     * @param format - Export format (json or txt)
     * @returns Exported conversation data
     */
    async exportConversation(
        conversationId: string,
        format: 'json' | 'txt' = 'json'
    ): Promise<Blob> {
        try {
            const response = await apiClient.get(
                `${this.baseURL}/export/${conversationId}`,
                {
                    params: { format },
                    responseType: 'blob'
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to export conversation:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const aiChatService = new AIChatService();
export default aiChatService;
