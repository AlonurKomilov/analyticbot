/**
 * AI Chat Interface Component
 * 
 * Conversational analytics interface for natural language queries.
 * Integrates with ai/chatService.ts
 */

import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Card,
    CardContent,
    TextField,
    IconButton,
    Typography,
    Avatar,
    Chip,
    CircularProgress,
    Alert,
    Divider,
    Paper,
    Tooltip
} from '@mui/material';
import {
    Send as SendIcon,
    SmartToy as AIIcon,
    Person as UserIcon,
    Refresh as RefreshIcon,
    Download as DownloadIcon,
    Lightbulb as LightbulbIcon,
    Info as InfoIcon
} from '@mui/icons-material';
import {
    aiChatService,
    type ChatQuestionResponse,
    type ChatMessage,
    type SuggestedQuestionsResponse
} from '@/services/ai/chatService';

export interface AIChatInterfaceProps {
    channelId?: number;
    onInsightGenerated?: (insight: any) => void;
}

const AIChatInterface: React.FC<AIChatInterfaceProps> = ({ 
    channelId,
    onInsightGenerated 
}) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Load suggested questions on mount
    useEffect(() => {
        loadSuggestedQuestions();
    }, [channelId]);

    const loadSuggestedQuestions = async () => {
        if (!channelId) return;
        
        try {
            const response: SuggestedQuestionsResponse = await aiChatService.getSuggestedQuestions(channelId);
            setSuggestedQuestions(response.popular_questions);
        } catch (err) {
            console.error('Failed to load suggested questions:', err);
        }
    };

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || isLoading || !channelId) return;

        const userMessage = inputMessage.trim();
        setInputMessage('');
        setError(null);

        // Add user message to chat
        const newUserMessage: ChatMessage = {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, newUserMessage]);

        setIsLoading(true);
        try {
            const response: ChatQuestionResponse = await aiChatService.askQuestion(
                channelId,
                userMessage
            );

            // Add AI response to chat
            const aiMessage: ChatMessage = {
                role: 'assistant',
                content: response.ai_response,
                timestamp: response.timestamp,
                metadata: {
                    intent: response.intent_detected,
                    confidence: response.confidence,
                    visualizations: response.visualization_suggestions,
                    follow_ups: response.follow_up_suggestions
                }
            };
            setMessages(prev => [...prev, aiMessage]);

            // Update suggested questions with follow-ups
            if (response.follow_up_suggestions && response.follow_up_suggestions.length > 0) {
                setSuggestedQuestions(response.follow_up_suggestions);
            }

            // Notify parent component if insight was generated
            if (onInsightGenerated) {
                onInsightGenerated(response);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to get AI response');
            console.error('AI chat error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestedQuestion = (question: string) => {
        setInputMessage(question);
    };

    const handleClearHistory = async () => {
        if (!channelId) return;

        try {
            await aiChatService.clearHistory(channelId);
            setMessages([]);
            setSuggestedQuestions([]);
            loadSuggestedQuestions();
        } catch (err) {
            console.error('Failed to clear history:', err);
        }
    };

    const handleExportConversation = async () => {
        if (!channelId) return;

        try {
            const blob = await aiChatService.exportConversation(channelId.toString(), 'json');
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ai-chat-${channelId}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to export conversation:', err);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AIIcon color="primary" />
                        <Typography variant="h6">AI Analytics Assistant</Typography>
                    </Box>
                    <Box>
                        <Tooltip title="Export conversation">
                            <IconButton 
                                size="small" 
                                onClick={handleExportConversation}
                                disabled={!channelId || messages.length === 0}
                            >
                                <DownloadIcon fontSize="small" />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Clear history">
                            <IconButton 
                                size="small" 
                                onClick={handleClearHistory}
                                disabled={!channelId || messages.length === 0}
                            >
                                <RefreshIcon fontSize="small" />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>

                <Divider sx={{ mb: 2 }} />

                {/* Messages Area */}
                <Box 
                    sx={{ 
                        flexGrow: 1, 
                        overflowY: 'auto', 
                        mb: 2,
                        minHeight: 300,
                        maxHeight: 500
                    }}
                >
                    {messages.length === 0 ? (
                        <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                            <AIIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
                            <Typography variant="body1" gutterBottom>
                                Ask me anything about your analytics!
                            </Typography>
                            <Typography variant="body2">
                                I can help you understand trends, performance, and insights.
                            </Typography>
                        </Box>
                    ) : (
                        messages.map((message, index) => (
                            <Box
                                key={index}
                                sx={{
                                    display: 'flex',
                                    gap: 1,
                                    mb: 2,
                                    alignItems: 'flex-start',
                                    flexDirection: message.role === 'user' ? 'row-reverse' : 'row'
                                }}
                            >
                                <Avatar 
                                    sx={{ 
                                        width: 32, 
                                        height: 32,
                                        bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main'
                                    }}
                                >
                                    {message.role === 'user' ? <UserIcon /> : <AIIcon />}
                                </Avatar>
                                
                                <Paper
                                    elevation={1}
                                    sx={{
                                        p: 1.5,
                                        maxWidth: '70%',
                                        bgcolor: message.role === 'user' ? 'primary.light' : 'grey.100',
                                        color: message.role === 'user' ? 'primary.contrastText' : 'text.primary'
                                    }}
                                >
                                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                        {message.content}
                                    </Typography>
                                    
                                    {/* Show metadata for AI responses */}
                                    {message.role === 'assistant' && message.metadata && (
                                        <Box sx={{ mt: 1 }}>
                                            {message.metadata.intent && (
                                                <Chip 
                                                    label={message.metadata.intent}
                                                    size="small"
                                                    icon={<InfoIcon />}
                                                    sx={{ mr: 0.5, mt: 0.5 }}
                                                />
                                            )}
                                            {message.metadata.confidence && (
                                                <Chip 
                                                    label={`${(message.metadata.confidence * 100).toFixed(0)}% confident`}
                                                    size="small"
                                                    color={message.metadata.confidence > 0.7 ? 'success' : 'warning'}
                                                    sx={{ mr: 0.5, mt: 0.5 }}
                                                />
                                            )}
                                        </Box>
                                    )}
                                </Paper>
                            </Box>
                        ))
                    )}
                    
                    {isLoading && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                                <AIIcon />
                            </Avatar>
                            <CircularProgress size={20} />
                            <Typography variant="body2" color="text.secondary">
                                Thinking...
                            </Typography>
                        </Box>
                    )}
                    
                    <div ref={messagesEndRef} />
                </Box>

                {/* Error Display */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {/* Suggested Questions */}
                {suggestedQuestions.length > 0 && messages.length < 3 && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                            <LightbulbIcon fontSize="small" />
                            Suggested questions:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {suggestedQuestions.slice(0, 3).map((question, index) => (
                                <Chip
                                    key={index}
                                    label={question}
                                    size="small"
                                    onClick={() => handleSuggestedQuestion(question)}
                                    clickable
                                    variant="outlined"
                                />
                            ))}
                        </Box>
                    </Box>
                )}

                {/* Input Area */}
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                        fullWidth
                        multiline
                        maxRows={3}
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about your analytics..."
                        disabled={isLoading}
                        size="small"
                        variant="outlined"
                    />
                    <IconButton
                        color="primary"
                        onClick={handleSendMessage}
                        disabled={!inputMessage.trim() || isLoading}
                        sx={{ alignSelf: 'flex-end' }}
                    >
                        <SendIcon />
                    </IconButton>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AIChatInterface;
