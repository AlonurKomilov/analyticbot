import React from 'react';
import {
    Box,
    Typography,
    Container,
    Paper,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Link,
    List,
    ListItem,
    ListItemText,
    Divider,
} from '@mui/material';
import {
    ExpandMore,
    Help,
    Dashboard,
    PostAdd,
    BarChart,
    Settings,
} from '@mui/icons-material';

/**
 * Help & Support Page Component
 * Documentation, FAQ, and support resources
 */
const HelpPage: React.FC = () => {
    const faqs = [
        {
            question: 'How do I add a new Telegram channel?',
            answer: 'Go to Channels page and click "Add Channel". You\'ll need your channel ID or username and appropriate permissions.',
            icon: <Dashboard />
        },
        {
            question: 'How do I create and schedule posts?',
            answer: 'Navigate to Posts > Create Post. Fill in your content, select a channel, and choose a schedule time. You can also send posts immediately.',
            icon: <PostAdd />
        },
        {
            question: 'What analytics are available?',
            answer: 'The Analytics page provides engagement metrics, view statistics, growth trends, and best posting time recommendations using AI.',
            icon: <BarChart />
        },
        {
            question: 'How do I configure MTProto for channel history?',
            answer: 'Go to Settings > MTProto Setup. You\'ll need your Telegram API ID, API Hash, and phone number to enable reading channel post history.',
            icon: <Settings />
        },
        {
            question: 'What is the difference between Bot API and MTProto?',
            answer: 'Bot API is for basic posting. MTProto allows reading historical channel data for better analytics and insights.',
            icon: <Help />
        },
    ];

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Help & Support
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                    Find answers to frequently asked questions and learn how to use the platform effectively.
                </Typography>

                <Divider sx={{ my: 3 }} />

                {/* Quick Links Section */}
                <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                        Quick Links
                    </Typography>
                    <List>
                        <ListItem>
                            <ListItemText
                                primary={<Link href="/channels" underline="hover">Channel Management</Link>}
                                secondary="Add, configure, and manage your Telegram channels"
                            />
                        </ListItem>
                        <ListItem>
                            <ListItemText
                                primary={<Link href="/posts/create" underline="hover">Create Posts</Link>}
                                secondary="Compose and schedule posts to your channels"
                            />
                        </ListItem>
                        <ListItem>
                            <ListItemText
                                primary={<Link href="/analytics" underline="hover">Analytics Dashboard</Link>}
                                secondary="View engagement metrics and performance insights"
                            />
                        </ListItem>
                        <ListItem>
                            <ListItemText
                                primary={<Link href="/settings/mtproto-setup" underline="hover">MTProto Setup</Link>}
                                secondary="Configure MTProto for advanced channel analytics"
                            />
                        </ListItem>
                    </List>
                </Box>

                <Divider sx={{ my: 3 }} />

                {/* FAQ Section */}
                <Box>
                    <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                        Frequently Asked Questions
                    </Typography>
                    {faqs.map((faq, index) => (
                        <Accordion key={index}>
                            <AccordionSummary expandIcon={<ExpandMore />}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    {faq.icon}
                                    <Typography>{faq.question}</Typography>
                                </Box>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Typography color="text.secondary">
                                    {faq.answer}
                                </Typography>
                            </AccordionDetails>
                        </Accordion>
                    ))}
                </Box>

                <Divider sx={{ my: 3 }} />

                {/* Support Contact */}
                <Box sx={{ mt: 4, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                    <Typography variant="h6" gutterBottom>
                        Need More Help?
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        If you can't find the answer you're looking for, please contact our support team.
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                        Email: <Link href="mailto:support@analyticbot.com">support@analyticbot.com</Link>
                    </Typography>
                </Box>
            </Paper>
        </Container>
    );
};

export default HelpPage;
