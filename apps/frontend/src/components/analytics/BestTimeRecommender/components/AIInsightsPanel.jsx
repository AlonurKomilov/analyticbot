import React from 'react';
import {
    Box,
    Typography,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Avatar
} from '@mui/material';
import { Psychology as AIIcon } from '@mui/icons-material';
import { getAIInsightIcon } from '../utils/timeUtils.js';

const AIInsightsPanel = ({ aiInsights }) => {
    if (!aiInsights || aiInsights.length === 0) {
        return (
            <Box sx={{ 
                textAlign: 'center', 
                p: 4,
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: 300,
                color: 'text.secondary'
            }}>
                <AIIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                    Tavsiyalar mavjud emas
                </Typography>
                <Typography variant="body2">
                    AI tavsiyalarini olish uchun ma'lumotlar yetarli emas
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
                🧠 AI Tavsiyalari va Ko'rsatmalar
            </Typography>
            <List>
                {aiInsights.map((insight, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'primary.light', width: 32, height: 32 }}>
                                <span aria-hidden="true">{getAIInsightIcon(insight)}</span>
                            </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                            primary={insight.title}
                            secondary={insight.description}
                            primaryTypographyProps={{ fontWeight: 'medium' }}
                        />
                    </ListItem>
                ))}
            </List>
        </Box>
    );
};

export default AIInsightsPanel;