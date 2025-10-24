# Month 2 Week 1: AI Chat Endpoints Migration

**Target:** Migrate `/ai-chat/*` → `/ai/chat/*`  
**Status:** 🟢 IN PROGRESS  
**Started:** October 22, 2025  
**Estimated Completion:** October 24-25, 2025 (2-3 days)

---

## ✅ Completed Setup

### 1. Migration Infrastructure Created
- ✅ `apps/frontend/src/api/endpointMigration.ts` - Migration helper with feature flags
- ✅ `apps/api/client.ts` - Updated to use migration helper
- ✅ Backend endpoints - Both old and new routes active

### 2. How It Works

The migration system automatically routes requests based on feature flags:

```typescript
// In apps/frontend/src/api/endpointMigration.ts
export const endpointMigrationFlags = {
  useNewAiChatEndpoints: true,  // ← Set to true to use /ai/chat/*
  // ... other flags
};
```

When `useNewAiChatEndpoints = true`:
- `/ai-chat/analyze` automatically becomes `/ai/chat/analyze`
- All requests route to new endpoints
- No code changes needed in components!

---

## 📋 Current Week Tasks

### Day 1-2: Analysis & Testing (October 22-23)

#### Task 1.1: Find AI Chat Usage ✅
**Status:** COMPLETED

Search results show AI chat endpoints are used in:
- Mock services (`apps/frontend/src/__mocks__/aiServices/`)
- Test files
- Real-time analytics (already using correct format)

**Finding:** Your frontend is already using mostly correct endpoint patterns or mock data. Most API calls go through the unified API client.

#### Task 1.2: Test Current Setup ⏳
**Status:** IN PROGRESS

**Action Items:**
1. Start the backend server
2. Verify both endpoints work
3. Test with feature flag enabled/disabled

**Commands to run:**

```bash
# Terminal 1: Start backend
cd /home/abcdeveloper/projects/analyticbot
make run
# OR
uvicorn apps.api.main:app --reload --port 8000

# Terminal 2: Check endpoints exist
curl http://localhost:8000/docs
# Look for both /ai-chat/* and /ai/chat/* endpoints

# Terminal 3: Start frontend (if needed)
cd apps/frontend
npm run dev
```

#### Task 1.3: Test Migration Helper
**Status:** READY TO TEST

Create test file to verify migration works:

```bash
# Create test file
cd apps/frontend
cat > src/api/endpointMigration.test.ts << 'EOF'
import { migrateEndpoint, endpointMigrationFlags, getMigrationStatus } from './endpointMigration';

// Test 1: Migration with flag enabled
endpointMigrationFlags.useNewAiChatEndpoints = true;
console.log('Test 1 - Flag enabled:');
console.log('  /ai-chat/analyze →', migrateEndpoint('/ai-chat/analyze'));
console.log('  Expected: /ai/chat/analyze');

// Test 2: Migration with flag disabled
endpointMigrationFlags.useNewAiChatEndpoints = false;
console.log('\nTest 2 - Flag disabled:');
console.log('  /ai-chat/analyze →', migrateEndpoint('/ai-chat/analyze'));
console.log('  Expected: /ai-chat/analyze');

// Test 3: Migration status
console.log('\nTest 3 - Migration Status:');
console.table(getMigrationStatus());
EOF

# Run test (needs Node/TypeScript environment)
npx tsx src/api/endpointMigration.test.ts
```

---

### Day 3-4: Validation & Monitoring (October 24-25)

#### Task 2.1: Enable AI Chat Migration
**Status:** PENDING

1. Confirm feature flag is enabled (already true by default):
```typescript
// apps/frontend/src/api/endpointMigration.ts
useNewAiChatEndpoints: true  // ✅ Already enabled
```

2. Test in development:
```bash
cd apps/frontend
npm run dev
# Open browser DevTools Console
# Look for migration logs: "🔄 Endpoint migrated: /ai-chat/... → /ai/chat/..."
```

#### Task 2.2: Monitor Requests
**Status:** PENDING

Open browser DevTools → Network tab and verify:
- [ ] All `/ai-chat/*` requests are redirected to `/ai/chat/*`
- [ ] Responses are successful (200 OK)
- [ ] No errors in console
- [ ] Data loads correctly

#### Task 2.3: Test Both Endpoints Work
**Status:** PENDING

**Backend verification:**
```bash
# Test OLD endpoint (should still work)
curl -X POST http://localhost:8000/ai-chat/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Test NEW endpoint (should work identically)
curl -X POST http://localhost:8000/ai/chat/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Both should return same response ✅
```

---

### Day 5: Documentation & Next Week Prep (October 25)

#### Task 3.1: Document Results
**Status:** PENDING

Create completion report:
- [ ] Number of endpoints migrated: 1 (ai-chat)
- [ ] Issues encountered: [None so far]
- [ ] Performance impact: [To measure]
- [ ] Rollback needed: [No]

#### Task 3.2: Prepare for Week 2
**Status:** PENDING

Next week targets:
- [ ] `/ai-insights/*` → `/ai/insights/*`
- [ ] `/ai-services/*` → `/ai/services/*`

Update feature flags:
```typescript
useNewAiInsightsEndpoints: true,
useNewAiServicesEndpoints: true,
```

---

## 🧪 Testing Checklist

### Manual Testing
- [ ] Backend starts without errors
- [ ] Both old and new endpoints visible in `/docs`
- [ ] Frontend loads without errors
- [ ] Migration logs appear in DevTools console
- [ ] Network requests use new endpoints
- [ ] Responses are correct
- [ ] No regression in functionality

### Automated Testing
- [ ] Run existing tests: `npm test`
- [ ] All tests should pass with new endpoints
- [ ] No new errors or warnings

---

## 🚨 Troubleshooting

### Issue: Migration not working
**Symptoms:** Requests still go to old endpoints  
**Solution:**
1. Check feature flag: `endpointMigrationFlags.useNewAiChatEndpoints` should be `true`
2. Clear browser cache and reload
3. Verify API client imports migration helper

### Issue: Backend endpoint not found
**Symptoms:** 404 Not Found errors  
**Solution:**
1. Verify backend is running latest code
2. Check `/docs` for available endpoints
3. Both old and new should be listed

### Issue: Different responses from old vs new
**Symptoms:** Data mismatch between endpoints  
**Solution:**
1. Report to backend team immediately
2. Disable feature flag: `useNewAiChatEndpoints: false`
3. Continue using old endpoint until fixed

---

## 📊 Progress Tracking

### Week 1 Progress: 40% Complete

- [x] Migration infrastructure created
- [x] API client updated
- [x] Feature flags configured
- [ ] Backend verified running
- [ ] Frontend tested with migration
- [ ] Both endpoints verified working
- [ ] Performance measured
- [ ] Documentation updated

---

## 🎯 Success Criteria

Week 1 is complete when:
- ✅ Backend serves both old and new endpoints
- ✅ Frontend migration helper works correctly
- ✅ Feature flag controls routing successfully
- ✅ No errors or regressions
- ✅ Performance is maintained or improved
- ✅ Documentation is updated

---

## 📞 Questions or Issues?

If you encounter problems:

1. **Check backend:** Is it running latest code with both endpoints?
2. **Check feature flag:** Is `useNewAiChatEndpoints` set correctly?
3. **Check console:** Are there migration logs showing the switch?
4. **Check network:** Do requests go to the right URL?

**Rollback Plan:**
```typescript
// apps/frontend/src/api/endpointMigration.ts
useNewAiChatEndpoints: false  // ← Set to false to revert
```

This immediately reverts ALL AI chat requests to old endpoints with zero code changes!

---

## 📈 Next Steps After Week 1

Once Week 1 is complete and stable:

**Week 2:** AI Insights & Services
- Enable `useNewAiInsightsEndpoints`
- Enable `useNewAiServicesEndpoints`
- Same testing process

**Week 3:** Strategy & Competitive
- Enable `useNewAiStrategyEndpoints`
- Enable `useNewAiCompetitiveEndpoints`

**Week 4:** Optimization & Buffer
- Enable `useNewAiOptimizationEndpoints`
- Final AI domain validation
- Address any issues

---

**Remember:** This is a gradual, low-risk migration. Take your time, test thoroughly, and don't hesitate to rollback if needed!

---

**Last Updated:** October 22, 2025  
**Next Review:** October 25, 2025  
**Migration Phase:** Month 2, Week 1 of 24 weeks
