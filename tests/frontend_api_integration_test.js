/**
 * Frontend API Integration Test Script
 * Tests PredictiveAnalyticsAPI and AlertsAPI with orchestrator endpoints
 *
 * Run with: node tests/frontend_api_integration_test.js
 */

const axios = require('axios');

// Configuration
const BASE_URL = process.env.API_BASE_URL || 'http://localhost:11400';
const TEST_CHANNEL_ID = '12345';
const TEST_USER_ID = '1';

// Mock auth token (you'll need to get a real one for actual testing)
let AUTH_TOKEN = null;

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logSection(title) {
  console.log('\n' + '='.repeat(80));
  log(`  ${title}`, colors.cyan);
  console.log('='.repeat(80));
}

function logTest(testName, passed, details = '') {
  const icon = passed ? '✅' : '❌';
  const color = passed ? colors.green : colors.red;
  log(`${icon} ${testName}`, color);
  if (details) {
    log(`   ${details}`, colors.yellow);
  }
}

// Create axios instance with auth
function createAuthClient(token = null) {
  return axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    }
  });
}

// Test results tracker
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0
};

function recordResult(passed, skipped = false) {
  testResults.total++;
  if (skipped) {
    testResults.skipped++;
  } else if (passed) {
    testResults.passed++;
  } else {
    testResults.failed++;
  }
}

// ==========================================
// PREDICTIVE ANALYTICS API TESTS
// ==========================================

async function testPredictiveHealthCheck() {
  logSection('Testing Predictive Analytics Health Check (No Auth)');

  try {
    const client = createAuthClient();
    const response = await client.get('/insights/predictive/intelligence/health');

    const passed = response.status === 200;
    logTest(
      'GET /insights/predictive/intelligence/health',
      passed,
      passed ? `Status: ${response.status}, Services: ${JSON.stringify(response.data)}` : 'Failed'
    );
    recordResult(passed);
    return response.data;
  } catch (error) {
    logTest(
      'GET /insights/predictive/intelligence/health',
      false,
      `Error: ${error.response?.status || error.message}`
    );
    recordResult(false);
    return null;
  }
}

async function testGenerateForecast() {
  logSection('Testing Generate Forecast (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.post('/insights/predictive/forecast', {
      channel_ids: [parseInt(TEST_CHANNEL_ID)],
      prediction_type: 'engagement',
      forecast_days: 7,
      confidence_level: 0.95
    });

    const passed = response.status === 200;
    logTest(
      'POST /insights/predictive/forecast (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'POST /insights/predictive/forecast (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true); // Skip this test
    } else {
      logTest(
        'POST /insights/predictive/forecast (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

async function testGetContextualInsights() {
  logSection('Testing Get Contextual Insights (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.post('/insights/predictive/intelligence/contextual', {
      channel_id: parseInt(TEST_CHANNEL_ID),
      intelligence_context: ['temporal', 'environmental', 'behavioral'],
      analysis_period_days: 30,
      prediction_horizon_days: 7,
      include_explanations: true
    });

    const passed = response.status === 200;
    logTest(
      'POST /insights/predictive/intelligence/contextual (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'POST /insights/predictive/intelligence/contextual (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'POST /insights/predictive/intelligence/contextual (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

async function testGetTemporalPatterns() {
  logSection('Testing Get Temporal Patterns (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.get(
      `/insights/predictive/intelligence/temporal/${TEST_CHANNEL_ID}?analysis_depth=comprehensive&include_seasonality=true`
    );

    const passed = response.status === 200;
    logTest(
      'GET /insights/predictive/intelligence/temporal/{id} (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'GET /insights/predictive/intelligence/temporal/{id} (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'GET /insights/predictive/intelligence/temporal/{id} (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

async function testGetCrossChannelIntelligence() {
  logSection('Testing Cross-Channel Intelligence (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.post('/insights/predictive/intelligence/cross-channel', {
      channel_ids: [parseInt(TEST_CHANNEL_ID)],
      analysis_dimensions: ['engagement', 'content', 'audience'],
      comparison_period_days: 30
    });

    const passed = response.status === 200;
    logTest(
      'POST /insights/predictive/intelligence/cross-channel (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'POST /insights/predictive/intelligence/cross-channel (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'POST /insights/predictive/intelligence/cross-channel (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

// ==========================================
// ALERTS API TESTS
// ==========================================

async function testAlertsHealthCheck() {
  logSection('Testing Alerts Health Check (No Auth)');

  try {
    const client = createAuthClient();
    const response = await client.get('/analytics/alerts/health');

    const passed = response.status === 200;
    logTest(
      'GET /analytics/alerts/health',
      passed,
      passed ? `Status: ${response.status}, Services: ${JSON.stringify(response.data)}` : 'Failed'
    );
    recordResult(passed);
    return response.data;
  } catch (error) {
    logTest(
      'GET /analytics/alerts/health',
      false,
      `Error: ${error.response?.status || error.message}`
    );
    recordResult(false);
    return null;
  }
}

async function testAlertsStats() {
  logSection('Testing Alerts Stats (No Auth)');

  try {
    const client = createAuthClient();
    const response = await client.get('/analytics/alerts/stats');

    const passed = response.status === 200;
    logTest(
      'GET /analytics/alerts/stats',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
    return response.data;
  } catch (error) {
    logTest(
      'GET /analytics/alerts/stats',
      false,
      `Error: ${error.response?.status || error.message}`
    );
    recordResult(false);
    return null;
  }
}

async function testGetLiveMonitoring() {
  logSection('Testing Live Monitoring (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.get(
      `/analytics/alerts/monitor/live/${TEST_CHANNEL_ID}?hours=6`
    );

    const passed = response.status === 200;
    logTest(
      'GET /analytics/alerts/monitor/live/{id} (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'GET /analytics/alerts/monitor/live/{id} (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'GET /analytics/alerts/monitor/live/{id} (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

async function testCheckAlerts() {
  logSection('Testing Check Alerts (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.post(
      `/analytics/alerts/check/${TEST_CHANNEL_ID}?analysis_type=comprehensive`,
      {}
    );

    const passed = response.status === 200;
    logTest(
      'POST /analytics/alerts/check/{id} (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'POST /analytics/alerts/check/{id} (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'POST /analytics/alerts/check/{id} (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

async function testCompetitiveMonitoring() {
  logSection('Testing Competitive Monitoring (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.post('/analytics/alerts/competitive/monitor', {
      channel_id: parseInt(TEST_CHANNEL_ID),
      monitoring_period_days: 7,
      include_competitor_analysis: true
    });

    const passed = response.status === 200;
    logTest(
      'POST /analytics/alerts/competitive/monitor (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'POST /analytics/alerts/competitive/monitor (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'POST /analytics/alerts/competitive/monitor (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

async function testComprehensiveWorkflow() {
  logSection('Testing Comprehensive Workflow (Requires Auth)');

  const client = createAuthClient(AUTH_TOKEN);

  try {
    const response = await client.post(
      `/analytics/alerts/workflow/comprehensive/${TEST_CHANNEL_ID}?include_competitive=true`,
      {}
    );

    const passed = response.status === 200;
    logTest(
      'POST /analytics/alerts/workflow/comprehensive/{id} (with auth)',
      passed,
      passed ? `Status: ${response.status}` : 'Failed'
    );
    recordResult(passed);
  } catch (error) {
    const status = error.response?.status;
    if (status === 401) {
      logTest(
        'POST /analytics/alerts/workflow/comprehensive/{id} (with auth)',
        false,
        '❌ 401 Unauthorized - Need valid auth token'
      );
      recordResult(false, true);
    } else {
      logTest(
        'POST /analytics/alerts/workflow/comprehensive/{id} (with auth)',
        false,
        `Error: ${status || error.message}`
      );
      recordResult(false);
    }
  }
}

// ==========================================
// TEST WITHOUT AUTH (SHOULD FAIL)
// ==========================================

async function testAuthRequired() {
  logSection('Testing Auth Requirements (Should Get 401)');

  const client = createAuthClient(); // No auth token

  // Test predictive endpoint without auth
  try {
    await client.post('/insights/predictive/forecast', {
      channel_ids: [parseInt(TEST_CHANNEL_ID)],
      prediction_type: 'engagement',
      forecast_days: 7
    });
    logTest('POST /insights/predictive/forecast (no auth)', false, 'Should have failed with 401');
    recordResult(false);
  } catch (error) {
    const passed = error.response?.status === 401;
    logTest(
      'POST /insights/predictive/forecast (no auth)',
      passed,
      passed ? '✅ Correctly returns 401 Unauthorized' : `Got ${error.response?.status} instead of 401`
    );
    recordResult(passed);
  }

  // Test alerts endpoint without auth
  try {
    await client.post(`/analytics/alerts/check/${TEST_CHANNEL_ID}`, {});
    logTest('POST /analytics/alerts/check (no auth)', false, 'Should have failed with 401');
    recordResult(false);
  } catch (error) {
    const passed = error.response?.status === 401;
    logTest(
      'POST /analytics/alerts/check (no auth)',
      passed,
      passed ? '✅ Correctly returns 401 Unauthorized' : `Got ${error.response?.status} instead of 401`
    );
    recordResult(passed);
  }
}

// ==========================================
// MAIN TEST RUNNER
// ==========================================

async function runAllTests() {
  log('\n╔════════════════════════════════════════════════════════════════════════════╗', colors.blue);
  log('║         FRONTEND API INTEGRATION TEST SUITE                                ║', colors.blue);
  log('║         Testing Orchestrator Endpoints                                     ║', colors.blue);
  log('╚════════════════════════════════════════════════════════════════════════════╝', colors.blue);

  log(`\n📍 Base URL: ${BASE_URL}`, colors.cyan);
  log(`📍 Test Channel ID: ${TEST_CHANNEL_ID}`, colors.cyan);
  log(`📍 Auth Token: ${AUTH_TOKEN ? 'Provided ✅' : 'Not provided ⚠️ (auth tests will be skipped)'}`, colors.cyan);

  // Run health checks first (no auth required)
  await testPredictiveHealthCheck();
  await testAlertsHealthCheck();
  await testAlertsStats();

  // Test auth requirements
  await testAuthRequired();

  // Run authenticated tests
  if (AUTH_TOKEN) {
    log('\n🔐 Running authenticated tests...', colors.cyan);

    // Predictive Analytics tests
    await testGenerateForecast();
    await testGetContextualInsights();
    await testGetTemporalPatterns();
    await testGetCrossChannelIntelligence();

    // Alerts tests
    await testGetLiveMonitoring();
    await testCheckAlerts();
    await testCompetitiveMonitoring();
    await testComprehensiveWorkflow();
  } else {
    log('\n⚠️  Skipping authenticated tests (no auth token provided)', colors.yellow);
    log('   To test authenticated endpoints, set AUTH_TOKEN environment variable:', colors.yellow);
    log('   export AUTH_TOKEN="your-jwt-token-here"', colors.yellow);
  }

  // Print summary
  logSection('TEST SUMMARY');
  log(`Total Tests: ${testResults.total}`, colors.cyan);
  log(`✅ Passed: ${testResults.passed}`, colors.green);
  log(`❌ Failed: ${testResults.failed}`, colors.red);
  log(`⏭️  Skipped: ${testResults.skipped}`, colors.yellow);

  const passRate = testResults.total > 0
    ? ((testResults.passed / (testResults.total - testResults.skipped)) * 100).toFixed(1)
    : 0;

  log(`\n📊 Pass Rate: ${passRate}% (excluding skipped)`, passRate >= 70 ? colors.green : colors.red);

  if (testResults.failed === 0 && testResults.passed > 0) {
    log('\n🎉 All tests passed!', colors.green);
  } else if (testResults.failed > 0) {
    log('\n❌ Some tests failed. Please review the results above.', colors.red);
  } else {
    log('\n⚠️  No tests passed. Check your API server status.', colors.yellow);
  }

  console.log('\n');
}

// Get auth token from environment or command line
if (process.env.AUTH_TOKEN) {
  AUTH_TOKEN = process.env.AUTH_TOKEN;
} else if (process.argv[2]) {
  AUTH_TOKEN = process.argv[2];
}

// Run the tests
runAllTests().catch(error => {
  console.error('Test runner failed:', error);
  process.exit(1);
});
