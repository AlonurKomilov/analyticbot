/**
 * Unified Marketplace Card
 *
 * Single card component that adapts for all marketplace categories:
 * AI Models, Themes, Services, Widgets, Bundles.
 * 
 * @module features/marketplace/components/cards/MarketplaceCard
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Box,
  Typography,
  Button,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Rating,
  Tooltip,
} from '@mui/material';
import {
  Psychology as AIIcon,
  Palette as ThemeIcon,
  Bolt as ServiceIcon,
  Widgets as WidgetIcon,
  CardGiftcard as BundleIcon,
  CheckCircle,
  ShoppingCart,
  Download,
  Star,
  WorkspacePremium,
  Circle,
} from '@mui/icons-material';
// Use types from pages/marketplace since they're the ones used in the actual app
import type { MarketplaceItem, BillingCycle } from '@/pages/marketplace/types';
import { getCategoryConfig } from '@/pages/marketplace/utils/categoryConfig';
import { getPriceDisplay, getSavingsDisplay } from '@/pages/marketplace/utils/priceFormatter';

interface MarketplaceCardProps {
  item: MarketplaceItem;
  billingCycle: BillingCycle;
  onPurchase: (item: MarketplaceItem) => void;
  onViewDetails: (item: MarketplaceItem) => void;
}

// Icon mapping
const CATEGORY_ICONS: Record<string, React.ReactElement> = {
  ai_models: <AIIcon />,
  themes: <ThemeIcon />,
  services: <ServiceIcon />,
  widgets: <WidgetIcon />,
  bundles: <BundleIcon />,
};

export const MarketplaceCard: React.FC<MarketplaceCardProps> = ({
  item,
  billingCycle,
  onPurchase,
  onViewDetails,
}) => {
  const categoryConfig = getCategoryConfig(item.category);
  const icon = CATEGORY_ICONS[item.category] || <WidgetIcon />;
  const priceDisplay = getPriceDisplay(item, billingCycle);
  const savingsDisplay = getSavingsDisplay(item);

  const isOwned = item.user_owned || item.user_subscribed;
  const showFeatures = item.features && item.features.length > 0;
  const showRating = item.rating && item.rating > 0;

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        border: item.is_featured ? `2px solid ${categoryConfig.color}` : undefined,
        opacity: isOwned ? 0.85 : 1,
        transition: 'all 0.2s ease-in-out',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={() => onViewDetails(item)}
    >
      {/* Badges */}
      <Box sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {item.is_featured && (
          <Chip
            label="Featured"
            size="small"
            icon={<Star />}
            sx={{ bgcolor: '#FFD700', color: '#000', fontWeight: 600 }}
          />
        )}
        {item.is_premium && (
          <Chip label="Premium" size="small" icon={<WorkspacePremium />} color="secondary" />
        )}
        {item.is_new && (
          <Chip label="New" size="small" color="success" />
        )}
        {item.is_beta && (
          <Chip label="Beta" size="small" color="warning" />
        )}
      </Box>

      {/* Icon Header */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: `${categoryConfig.color}15`,
          position: 'relative',
        }}
      >
        <Box
          sx={{
            width: 64,
            height: 64,
            borderRadius: 2,
            bgcolor: categoryConfig.color,
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 32,
          }}
        >
          {icon}
        </Box>
      </Box>

      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        {/* Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Typography variant="h6" component="h3" noWrap sx={{ flexGrow: 1 }}>
            {item.name}
          </Typography>
          {isOwned && (
            <Tooltip title={item.pricing_model === 'subscription' ? 'Subscribed' : 'Owned'}>
              <CheckCircle color="success" fontSize="small" />
            </Tooltip>
          )}
        </Box>

        {/* Category Badge */}
        <Chip
          label={categoryConfig.label}
          size="small"
          sx={{
            mb: 2,
            bgcolor: `${categoryConfig.color}20`,
            color: categoryConfig.color,
            fontWeight: 500,
          }}
        />

        {/* Description */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 2, minHeight: 40, lineHeight: 1.5 }}
        >
          {item.short_description || item.description}
        </Typography>

        {/* Features List */}
        {showFeatures && (
          <List dense disablePadding sx={{ mb: 2 }}>
            {item.features!.slice(0, 3).map((feature, index) => (
              <ListItem key={index} disablePadding sx={{ py: 0.25 }}>
                <ListItemIcon sx={{ minWidth: 28 }}>
                  <Circle sx={{ fontSize: 8, color: categoryConfig.color }} />
                </ListItemIcon>
                <ListItemText
                  primary={feature}
                  primaryTypographyProps={{
                    variant: 'caption',
                    color: 'text.secondary',
                  }}
                />
              </ListItem>
            ))}
          </List>
        )}

        {/* Stats (ratings, downloads) */}
        {(showRating || item.download_count) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            {showRating && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Rating value={item.rating} precision={0.1} size="small" readOnly />
                <Typography variant="caption" color="text.secondary">
                  ({item.rating_count || 0})
                </Typography>
              </Box>
            )}
            {item.download_count && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Download fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {item.download_count.toLocaleString()}
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', p: 2, pt: 0 }}>
        {/* Price */}
        <Box>
          <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
            {priceDisplay}
          </Typography>
          {savingsDisplay && billingCycle === 'yearly' && (
            <Typography variant="caption" color="success.main" sx={{ fontWeight: 600 }}>
              {savingsDisplay}
            </Typography>
          )}
        </Box>

        {/* Purchase Button */}
        <Button
          variant={isOwned ? 'outlined' : 'contained'}
          color={isOwned ? 'success' : 'primary'}
          disabled={isOwned}
          startIcon={isOwned ? <CheckCircle /> : <ShoppingCart />}
          onClick={(e) => {
            e.stopPropagation();
            onPurchase(item);
          }}
          sx={{
            minWidth: 100,
            bgcolor: isOwned ? undefined : categoryConfig.color,
            '&:hover': {
              bgcolor: isOwned ? undefined : categoryConfig.color,
              opacity: 0.9,
            },
          }}
        >
          {isOwned ? (item.pricing_model === 'subscription' ? 'Subscribed' : 'Owned') : 'Purchase'}
        </Button>
      </CardActions>
    </Card>
  );
};
