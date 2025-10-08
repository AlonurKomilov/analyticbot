/**
 * Theme Variants Usage Guide
 *
 * This file demonstrates how to use the new theme variants instead of inline sx props.
 *
 * BEFORE (inline sx usage):
 * <Container maxWidth="xl" sx={{ py: 3, minHeight: '100vh' }}>
 * <Paper sx={{ p: 3, borderRadius: 2, mb: 4 }}>
 * <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
 * <Alert severity="error" sx={{ m: 2 }}>
 * <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
 *
 * AFTER (using theme variants):
 * <Container variant="dashboard">
 * <Paper variant="card">
 * <Box variant="headerControls">
 * <Alert variant="spaced" severity="error">
 * <Typography variant="pageTitle">
 *
 * Available Theme Variants:
 *
 * Container Variants:
 * - variant="dashboard" → maxWidth: 'xl', py: 3, minHeight: '100vh'
 * - variant="page" → maxWidth: 'sm', py: 4
 *
 * Paper Variants:
 * - variant="card" → padding: 24px, borderRadius: 8px, marginBottom: 32px
 * - variant="chart" → padding: 16px, background with border
 * - variant="legend" → padding: 16px, background with border and borderRadius
 *
 * Box Variants:
 * - variant="flexCenter" → display: flex, justifyContent: center, alignItems: center
 * - variant="flexBetween" → display: flex, justifyContent: space-between, alignItems: center
 * - variant="flexColumn" → display: flex, flexDirection: column
 * - variant="flexRow" → display: flex, alignItems: center, gap: 8px
 * - variant="chartContainer" → height: 400px, marginTop: 16px
 * - variant="emptyState" → centered flex container with column direction for empty states
 * - variant="headerControls" → flex between for header sections with controls
 * - variant="actionControls" → flex with gap for action buttons
 *
 * CardContent Variants:
 * - variant="metric" → padding: 16px with proper last-child handling
 * - variant="service" → padding: 24px for service cards
 *
 * FormControl Variants:
 * - variant="compact" → minWidth: 120px for form controls
 *
 * Alert Variants:
 * - variant="spaced" → margin: 16px
 * - variant="topSpaced" → marginTop: 24px
 * - variant="bottomSpaced" → marginBottom: 16px
 *
 * Typography Variants:
 * - variant="pageTitle" → marginBottom: 16px, fontWeight: 600
 * - variant="sectionTitle" → marginBottom: 8px
 * - variant="withIcon" → marginLeft: 16px
 *
 * Grid Variants:
 * - variant="metricsGrid" → marginBottom: 24px
 *
 * Skeleton Variants:
 * - variant="centered" → marginLeft/Right: auto
 * - variant="centeredWithMargin" → centered with marginTop: 8px
 *
 * Stack Variants:
 * - variant="page" → spacing: 3, marginTop: 16px
 *
 * Benefits:
 * 1. Consistency across components
 * 2. Reduced bundle size (no repeated inline styles)
 * 3. Easier theming and design system maintenance
 * 4. Better performance (styles are cached)
 * 5. Easier refactoring and updates
 *
 * Migration Status:
 * ✅ MainDashboard.jsx - Partially converted (major patterns)
 * ✅ PostViewDynamicsChart.jsx - Partially converted (tooltip, loading states)
 * ✅ App.test.jsx - Fully converted
 * ✅ ButtonConstructor.jsx - Partially converted
 * ⏳ Remaining components with high sx usage to be migrated
 *
 * Next Steps:
 * 1. Complete migration of remaining components
 * 2. Add more variants as common patterns emerge
 * 3. Consider creating compound components for complex patterns
 * 4. Remove unused sx props after full migration
 */

export const THEME_VARIANTS_GUIDE = {
  // This is a documentation file - no actual exports needed
  // Use this as reference when migrating components
};
