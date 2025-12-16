/**
 * 🏷️ Service Subcategory Filter Component
 * 
 * Secondary filter for Services category - shows Bot, MTProto, Analytics, AI
 * Technical grouping for easier navigation
 */

import React from 'react';
import { Box, Chip, Fade } from '@mui/material';
import * as Icons from '@mui/icons-material';
import { ServiceSubcategory } from '../types';
import { getServiceSubcategoryConfig } from '../utils/categoryConfig';

interface ServiceSubcategoryFilterProps {
    selectedSubcategory: ServiceSubcategory;
    onSubcategoryChange: (subcategory: ServiceSubcategory) => void;
    itemCounts?: Record<ServiceSubcategory, number>; // Optional item counts
}

export const ServiceSubcategoryFilter: React.FC<ServiceSubcategoryFilterProps> = ({
    selectedSubcategory,
    onSubcategoryChange,
    itemCounts = {},
}) => {
    const subcategories: ServiceSubcategory[] = ['all', 'bot', 'mtproto', 'ai'];

    const getIcon = (iconName: string) => {
        const IconComponent = (Icons as any)[iconName];
        return IconComponent ? <IconComponent sx={{ fontSize: 18 }} /> : null;
    };

    return (
        <Fade in={true}>
            <Box
                sx={{
                    display: 'flex',
                    gap: 1,
                    flexWrap: 'wrap',
                    mb: 3,
                    p: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 2,
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                }}
            >
                {subcategories.map((subcategory) => {
                    const config = getServiceSubcategoryConfig(subcategory);
                    const count = itemCounts[subcategory];
                    const isSelected = selectedSubcategory === subcategory;
                    const isDisabled = subcategory === 'ai' && count === 0;
                    const icon = getIcon(config.icon);

                    return (
                        <Chip
                            key={subcategory}
                            icon={icon || undefined}
                            label={
                                count !== undefined && count > 0
                                    ? `${config.label} (${count})`
                                    : config.label
                            }
                            onClick={() => !isDisabled && onSubcategoryChange(subcategory)}
                            disabled={isDisabled}
                            sx={{
                                height: 36,
                                fontSize: '0.875rem',
                                fontWeight: isSelected ? 600 : 400,
                                backgroundColor: isSelected
                                    ? `${config.color}20`
                                    : 'rgba(255, 255, 255, 0.05)',
                                color: isSelected ? config.color : 'text.secondary',
                                border: isSelected
                                    ? `2px solid ${config.color}`
                                    : '1px solid rgba(255, 255, 255, 0.1)',
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    backgroundColor: isDisabled
                                        ? 'rgba(255, 255, 255, 0.02)'
                                        : `${config.color}30`,
                                    borderColor: config.color,
                                    transform: isDisabled ? 'none' : 'translateY(-2px)',
                                    boxShadow: isDisabled
                                        ? 'none'
                                        : `0 4px 12px ${config.color}40`,
                                },
                                '& .MuiChip-icon': {
                                    color: isSelected ? config.color : 'text.secondary',
                                },
                                cursor: isDisabled ? 'not-allowed' : 'pointer',
                                opacity: isDisabled ? 0.5 : 1,
                            }}
                        />
                    );
                })}
            </Box>
        </Fade>
    );
};
