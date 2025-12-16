/**
 * 🏷️ Category Filter Component
 *
 * Pills/chips for filtering marketplace by category
 */

import React from 'react';
import { Box, Chip } from '@mui/material';
import {
    Psychology as AIIcon,
    Palette as ThemeIcon,
    Bolt as ServiceIcon,
    Widgets as WidgetIcon,
    CardGiftcard as BundleIcon,
    Inventory as AllIcon,
} from '@mui/icons-material';
import { MarketplaceCategory } from '../types';
import { CATEGORY_CONFIGS } from '../utils/categoryConfig';

interface CategoryFilterProps {
    selectedCategory: MarketplaceCategory;
    onCategoryChange: (category: MarketplaceCategory) => void;
}

const ICON_MAP: Record<string, React.ReactElement> = {
    Inventory: <AllIcon />,
    Psychology: <AIIcon />,
    Palette: <ThemeIcon />,
    Bolt: <ServiceIcon />,
    Widgets: <WidgetIcon />,
    CardGiftcard: <BundleIcon />,
};

export const CategoryFilter: React.FC<CategoryFilterProps> = ({
    selectedCategory,
    onCategoryChange,
}) => {
    // Services shown first (it has real data)
    const categories: MarketplaceCategory[] = ['services', 'themes', 'widgets', 'bundles'];

    return (
        <Box
            sx={{
                display: 'flex',
                gap: 1,
                flexWrap: 'wrap',
                mb: 3,
                pb: 2,
                borderBottom: '1px solid',
                borderColor: 'divider',
            }}
        >
            {categories.map((category) => {
                const config = CATEGORY_CONFIGS[category];
                const isSelected = selectedCategory === category;
                const icon = ICON_MAP[config.icon];

                return (
                    <Chip
                        key={category}
                        label={config.label}
                        icon={icon}
                        onClick={() => onCategoryChange(category)}
                        variant={isSelected ? 'filled' : 'outlined'}
                        color={isSelected ? 'primary' : 'default'}
                        sx={{
                            fontWeight: isSelected ? 600 : 400,
                            bgcolor: isSelected ? config.color : undefined,
                            borderColor: config.color,
                            color: isSelected ? 'white' : config.color,
                            '&:hover': {
                                bgcolor: isSelected ? config.color : `${config.color}15`,
                                opacity: isSelected ? 0.9 : 1,
                            },
                            '& .MuiChip-icon': {
                                color: isSelected ? 'white' : config.color,
                            },
                        }}
                    />
                );
            })}
        </Box>
    );
};
