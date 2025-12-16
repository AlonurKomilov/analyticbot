# 🛒 Unified Purchase Flow

## Overview
We've unified the two purchase dialog designs into ONE adaptive component that handles both one-time purchases and subscriptions.

## User Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. User browses marketplace cards                          │
│     - Sees: Icon, Name, Description, Price, Badges          │
│     - Hover animation shows it's clickable                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Click on card → Opens ItemDetailModal                   │
│     - Full description                                      │
│     - All features listed                                   │
│     - Stats (rating, downloads, active users)               │
│     - Larger view of pricing                                │
│     - "Purchase Now" button                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Click "Purchase" → Opens PurchaseDialog                 │
│     ┌─────────────────────────────────────────────────┐     │
│     │  For ONE-TIME purchases (Items):                │     │
│     │  ✓ Item name & description                      │     │
│     │  ✓ Price breakdown                              │     │
│     │  ✓ Balance calculation                          │     │
│     │  ✓ Confirm button                               │     │
│     └─────────────────────────────────────────────────┘     │
│                                                             │
│     ┌─────────────────────────────────────────────────┐     │
│     │  For SUBSCRIPTIONS (Services):                  │     │
│     │  ✓ Service name & description                   │     │
│     │  ✓ Features list with green checkmarks          │     │
│     │  ✓ Billing toggle: MONTHLY / YEARLY             │     │
│     │    - Shows "SAVE 17%" badge for yearly          │     │
│     │  ✓ Price breakdown (per month/year)             │     │
│     │  ✓ Balance calculation                          │     │
│     │  ℹ️  Recurring subscription warning              │     │
│     │  ✓ Confirm button                               │     │
│     └─────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Unified Purchase Dialog Design

### Common Elements (Both Types)
- Dark theme background (#1a1d2e)
- Shopping cart icon in header
- Item name & description
- Price breakdown showing:
  - Price
  - Your Balance
  - After Purchase (in green/red)
- Cancel & Confirm buttons
- Blue "Confirm Purchase" button (#3b82f6)

### One-Time Purchase Specific
- Title: "Purchase Item"
- Simple price display: "500 Credits"
- Single payment, no warning

### Subscription Specific
- Title: "Subscribe to Service"  
- Features list with green checkmarks
- Billing toggle with 3 buttons:
  - MONTHLY (gray when not selected)
  - YEARLY (gray when not selected)
  - Green "SAVE 17%" badge on selected yearly
- Price display: "350 Credits / year"
- Blue info box: "This is a recurring subscription..."

## Visual Consistency

### Color Palette
- Background: #1a1d2e (dark blue-gray)
- Text: White / #9ca3af (gray)
- Primary button: #3b82f6 (blue)
- Success: #10b981 (green for checkmarks, savings)
- Checkmark: #4ade80 (lighter green)

### Typography
- Title: 1.25rem, font-weight 600
- Body: 0.875rem-1rem
- Features: 0.875rem with green checkmarks

### Spacing
- Dialog padding: 24px
- Section gaps: 24px (mb-3)
- Feature list spacing: 12px between items

## Code Structure

```typescript
// Single component adapts based on item type
<PurchaseDialog
  item={selectedItem}
  // Automatically shows/hides features
  // Automatically shows/hides billing toggle
  // Automatically adjusts title
  // Automatically shows/hides subscription warning
/>
```

## Benefits of Unified Design

1. **Consistency**: Same look & feel for all purchases
2. **Less Code**: One component handles all cases
3. **Better UX**: Predictable behavior
4. **Easier Maintenance**: Update once, affects all
5. **Scalable**: Easy to add new purchase types

## Testing Checklist

- [ ] Click card → Detail modal opens
- [ ] Click "Purchase Now" → Purchase dialog opens  
- [ ] One-time item shows simple price
- [ ] Subscription shows features list
- [ ] Subscription shows billing toggle
- [ ] Yearly billing shows "SAVE 17%" badge
- [ ] Price updates when toggling monthly/yearly
- [ ] "After Purchase" shows green if affordable, red if not
- [ ] Subscription shows recurring warning
- [ ] "Confirm Purchase" disabled if insufficient credits
- [ ] Purchase succeeds → Shows success snackbar
- [ ] Purchase fails → Shows error snackbar
