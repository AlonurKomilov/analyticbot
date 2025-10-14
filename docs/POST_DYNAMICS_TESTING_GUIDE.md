# Post Dynamics - Testing Guide

## Quick Test Checklist

### ✅ API Endpoint Tests

```bash
# Test 1: Basic endpoint (24 hours)
curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=24h

# Test 2: Different time periods
curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=1h
curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=7d
curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=30d

# Test 3: Top posts endpoint
curl http://localhost:11400/analytics/top-posts/demo_channel?period=week&sortBy=views

# Test 4: Cache verification (should be faster on second call)
time curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=24h
time curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=24h

# Test 5: API documentation
open http://localhost:11400/docs#/analytics-post-dynamics
```

### ✅ Frontend UI Tests

#### Test Scenario 1: Normal Operation (With Channels)
1. Open http://localhost:11300
2. Login with credentials
3. Navigate to Dashboard
4. **Expected:**
   - ✅ Chart displays with data
   - ✅ Summary stats show metrics
   - ✅ "🔄 Avtomatik yangilash" chip visible
   - ✅ Data updates every 30 seconds

#### Test Scenario 2: No Channels Available
1. Clear all channels from database/store
2. Reload dashboard
3. **Expected:**
   - ✅ Warning message: "📺 No Channels Found"
   - ✅ Guidance text about adding channels
   - ✅ "⏸️ Auto-refresh disabled" chip visible
   - ✅ No API calls in network tab
   - ✅ No console errors

#### Test Scenario 3: Empty Data
1. Have channels but no data in time range
2. Load dashboard
3. **Expected:**
   - ✅ Empty state message: "No Data Available"
   - ✅ Helpful suggestion to try different time range
   - ✅ No errors or crashes

#### Test Scenario 4: Auto-Refresh Behavior
1. Open browser DevTools → Console
2. Watch for refresh messages
3. **Expected:**
   - ✅ "Setting up auto-refresh every 30000 ms"
   - ✅ "Auto-refresh triggered" every 30 seconds
   - ✅ No refresh when no channels available

#### Test Scenario 5: Demo Mode
1. Access without authenticated channels
2. **Expected:**
   - ✅ Info alert: "You are in demo mode"
   - ✅ Chart shows mock data
   - ✅ All features work normally

### ✅ Performance Tests

```bash
# Monitor API response time
watch -n 1 'curl -s -w "\nTime: %{time_total}s\n" http://localhost:11400/analytics/post-dynamics/demo_channel?period=24h -o /dev/null'

# Monitor memory usage
# Open browser DevTools → Performance → Record for 1 minute

# Check auto-refresh impact
# Open Network tab → Watch requests over 5 minutes
# Should see request every 30 seconds (or configured interval)
```

### ✅ Error Handling Tests

#### Test 1: API Server Down
```bash
# Stop API
make dev-stop

# Open frontend - Expected:
# ✅ Graceful fallback to demo data
# ✅ No crashes or blank screens
```

#### Test 2: Invalid Time Period
```bash
curl http://localhost:11400/analytics/post-dynamics/demo_channel?period=invalid
# Expected: 422 Validation Error
```

#### Test 3: Network Timeout
```bash
# Throttle network in DevTools → Slow 3G
# Expected: Loading state → Eventually shows data or error
```

## Expected Console Output

### ✅ Successful Load (With Channels)
```
PostViewDynamicsChart: Setting up auto-refresh every 30000 ms
✅ Post dynamics loaded from real API
PostViewDynamicsChart: Auto-refresh triggered
```

### ✅ No Channels Available
```
PostViewDynamicsChart: No channels available, skipping data fetch
PostViewDynamicsChart: Auto-refresh disabled - no channels available
```

### ✅ API Fallback
```
⚠️ API unavailable for post dynamics, using demo data
📊 Loading post dynamics demo data
```

## Network Tab Verification

### Expected Requests (With Channels)
```
GET /analytics/post-dynamics/demo_channel?period=24h
Status: 200 OK
Size: ~5KB
Time: 50-100ms (first), ~5ms (cached)
```

### Expected Requests (No Channels)
```
(No requests to post-dynamics endpoint)
```

## Browser DevTools Checklist

### ✅ Console
- [ ] No red errors
- [ ] Appropriate log messages
- [ ] Auto-refresh messages appear

### ✅ Network
- [ ] Requests return 200 OK
- [ ] Proper caching headers
- [ ] Reasonable response times

### ✅ Performance
- [ ] No memory leaks
- [ ] Smooth animations
- [ ] No layout thrashing

### ✅ React DevTools
- [ ] Proper component hierarchy
- [ ] State updates correctly
- [ ] No unnecessary re-renders

## Common Issues & Solutions

### Issue: Chart is blank
**Check:**
- [ ] API endpoint is responding (test with curl)
- [ ] Channels exist in store
- [ ] No console errors
- [ ] Network requests succeed

### Issue: Auto-refresh not working
**Check:**
- [ ] Channels are available
- [ ] refreshInterval is not 'disabled'
- [ ] Tab is visible (hidden tabs pause refresh)
- [ ] Console shows refresh messages

### Issue: Data not updating
**Check:**
- [ ] Cache TTL (5 minutes default)
- [ ] Redis is running
- [ ] No API errors in logs

### Issue: Performance slow
**Check:**
- [ ] Redis cache is enabled
- [ ] Not too many simultaneous requests
- [ ] Proper memoization in components
- [ ] No dependency loops in useEffect

## API Logs to Monitor

```bash
# Watch API logs in real-time
tail -f logs/dev_api.log | grep -E "(post-dynamics|ERROR|WARNING)"

# Look for:
✅ "GET /analytics/post-dynamics/demo_channel?period=24h HTTP/1.1" 200 OK
✅ "Fetching post dynamics for channel demo_channel, period 24h"
✅ "Generated 24 post dynamics points for channel demo_channel"

# Watch for errors:
❌ 403 Forbidden (auth issue)
❌ 500 Internal Server Error (backend issue)
❌ 422 Validation Error (invalid parameters)
```

## Automated Test Commands

```bash
# Run all tests
npm test -- PostViewDynamicsChart

# Run with coverage
npm test -- --coverage PostViewDynamicsChart

# Run in watch mode
npm test -- --watch PostViewDynamicsChart

# E2E test (if configured)
npm run test:e2e -- post-dynamics
```

## Success Criteria

### ✅ All Green
- API returns 200 OK
- Chart displays data
- Auto-refresh works
- No console errors
- Proper warnings when needed
- Performance is acceptable
- Memory doesn't leak
- State updates correctly

### ✅ User Experience
- Clear messaging
- Intuitive behavior
- Fast load times
- Smooth interactions
- Helpful error messages
- Appropriate loading states

---

**Last Updated:** October 14, 2025
**Test Status:** All Passed ✅
