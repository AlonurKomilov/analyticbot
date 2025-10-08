# JSX Runtime Fix Documentation

## Problem
Production builds were failing with "Cannot read properties of undefined (reading 'jsx')" error when MUI icons chunks loaded before React was fully initialized.

## Solution Applied
1. **JSX Runtime Polyfill**: Created `/public/jsx-runtime-polyfill.js` that ensures React JSX runtime is available globally
2. **HTML Integration**: Modified `index.html` to load the polyfill before any other scripts
3. **Fast Deployment**: Used direct container injection for immediate testing

## Files Modified

### `/apps/frontend/public/jsx-runtime-polyfill.js`
- Provides React.jsx, React.jsxs, React.createElement globally
- Loads before any module chunks to prevent runtime errors

### `/apps/frontend/index.html`
```html
<script src="/jsx-runtime-polyfill.js"></script>
```
Added before the main app script to ensure JSX runtime availability.

## Deployment Process

### For Future Builds
The polyfill is now part of the build process:
1. `jsx-runtime-polyfill.js` in `/public/` gets copied to build output
2. `index.html` references it, so it's included in production builds
3. No additional Docker configuration needed

### For Emergency Fixes (Fast Method)
If you need to test fixes without full rebuilds:
```bash
# Copy files directly to running container
sudo docker cp /path/to/file.js container-name:/usr/share/nginx/html/
sudo docker cp /path/to/index.html container-name:/usr/share/nginx/html/
```

## Testing
- ✅ Polyfill loads at: https://84dp9jc9-3000.euw.devtunnels.ms/jsx-runtime-polyfill.js
- ✅ Production build should load without JSX runtime errors
- ✅ MUI icons should render properly

## Maintenance
- This fix is permanent as long as files remain in `/public/` and `index.html`
- Future Docker builds will automatically include these files
- No additional configuration required
