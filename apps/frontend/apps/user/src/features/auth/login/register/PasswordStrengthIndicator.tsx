/**
 * Password Strength Indicator Component
 * Visual password strength feedback with requirements checklist
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    Box,
    Typography,
    LinearProgress,
    Button,
    Collapse,
    List,
    ListItem,
    ListItemIcon,
    ListItemText
} from '@mui/material';
import {
    Check as CheckIcon,
    Close as CloseIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import type { PasswordStrength, PasswordRequirements } from './types';
import { getPasswordStrengthColor } from './passwordUtils';

interface PasswordStrengthIndicatorProps {
    password: string;
    passwordStrength: PasswordStrength;
    showRequirements: boolean;
    onToggleRequirements: () => void;
}

export const PasswordStrengthIndicator: React.FC<PasswordStrengthIndicatorProps> = ({
    password,
    passwordStrength,
    showRequirements,
    onToggleRequirements
}) => {
    const { t } = useTranslation('auth');

    if (!password) {
        return null;
    }

    const { score, requirements } = passwordStrength;

    // Map score to translation key
    const getStrengthLabel = (score: number): string => {
        if (score < 40) return t('register.passwordStrength.weak');
        if (score < 80) return t('register.passwordStrength.good');
        return t('register.passwordStrength.strong');
    };

    // Map requirement keys to translation keys
    const requirementTranslations: Record<keyof PasswordRequirements, string> = {
        length: t('register.passwordRequirements.length'),
        lowercase: t('register.passwordRequirements.lowercase'),
        uppercase: t('register.passwordRequirements.uppercase'),
        number: t('register.passwordRequirements.number'),
        special: t('register.passwordRequirements.special')
    };

    return (
        <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="caption" sx={{ mr: 1 }}>
                    {t('register.passwordStrength.label')}
                </Typography>
                <Typography variant="caption" color={`${getPasswordStrengthColor(score)}.main`}>
                    {getStrengthLabel(score)}
                </Typography>
            </Box>
            <LinearProgress
                variant="determinate"
                value={score}
                color={getPasswordStrengthColor(score)}
                sx={{ height: 4, borderRadius: 2 }}
            />

            {/* Password Requirements */}
            <Box sx={{ mt: 1 }}>
                <Button
                    size="small"
                    startIcon={showRequirements ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    onClick={onToggleRequirements}
                    sx={{ textTransform: 'none', fontSize: '0.75rem' }}
                >
                    {t('register.passwordRequirements.title')}
                </Button>
                <Collapse in={showRequirements}>
                    <List dense sx={{ py: 0 }}>
                        {(Object.entries(requirementTranslations) as [keyof PasswordRequirements, string][]).map(
                            ([key, text]) => (
                                <ListItem key={key} sx={{ py: 0, px: 1 }}>
                                    <ListItemIcon sx={{ minWidth: 20 }}>
                                        {requirements[key] ? (
                                            <CheckIcon sx={{ fontSize: 16, color: 'success.main' }} />
                                        ) : (
                                            <CloseIcon sx={{ fontSize: 16, color: 'error.main' }} />
                                        )}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={text}
                                        primaryTypographyProps={{
                                            variant: 'caption',
                                            color: requirements[key] ? 'success.main' : 'text.secondary'
                                        }}
                                    />
                                </ListItem>
                            )
                        )}
                    </List>
                </Collapse>
            </Box>
        </Box>
    );
};
