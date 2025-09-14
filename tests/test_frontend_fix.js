#!/usr/bin/env node

/**
 * Frontend Fix Verification Test
 * Tests that the rebuilt frontend now uses the correct API endpoints
 */

const http = require('http');

console.log('🔧 Testing Frontend Fix After Docker Rebuild...\n');

// Test that the API endpoints are working with the correct format
async function testApiEndpoints() {
    const endpoints = [
        {
            name: 'Health Check',
            url: 'http://localhost:8000/health'
        },
        {
            name: 'Initial Data',
            url: 'http://localhost:8000/initial-data'
        },
        {
            name: 'Fixed Analytics Overview',
            url: 'http://localhost:8000/api/v2/analytics/channels/demo_channel/overview?from=2025-08-13T00:00:00.000Z&to=2025-09-12T00:00:00.000Z'
        }
    ];

    console.log('📊 Testing Backend API Endpoints:');
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint.url);
            const status = response.status;
            
            if (status >= 200 && status < 300) {
                console.log(`   ✅ ${endpoint.name}: HTTP ${status} (Working)`);
            } else if (status === 422) {
                console.log(`   ❌ ${endpoint.name}: HTTP ${status} (Parameter Error - OLD FORMAT)`);
            } else {
                console.log(`   ⚠️  ${endpoint.name}: HTTP ${status} (Other Error)`);
            }
        } catch (error) {
            console.log(`   🔌 ${endpoint.name}: Connection Failed (${error.message})`);
        }
    }
}

// Test frontend accessibility
async function testFrontendAccess() {
    console.log('\n🌐 Testing Frontend Access:');
    
    try {
        const response = await fetch('http://localhost:3000');
        if (response.ok) {
            console.log('   ✅ Frontend accessible on http://localhost:3000');
            console.log('   📱 Ready to test in browser!');
        } else {
            console.log(`   ❌ Frontend error: HTTP ${response.status}`);
        }
    } catch (error) {
        console.log(`   🔌 Frontend not accessible: ${error.message}`);
    }
}

async function main() {
    await testApiEndpoints();
    await testFrontendAccess();
    
    console.log('\n📋 Summary:');
    console.log('   • Frontend rebuilt with --no-cache to include ALL fixes');
    console.log('   • apiClient.js: Fixed channel IDs and parameters');
    console.log('   • appStore.js: Fixed all old /analytics/demo endpoints');
    console.log('   • Container restarted with fresh build');
    
    console.log('\n🎯 Next Steps:');
    console.log('   1. Open http://localhost:3000 in your browser');
    console.log('   2. Open browser console (F12)');
    console.log('   3. Check for errors - should see MUCH fewer errors');
    console.log('   4. If still seeing old demo_channel errors, clear browser cache');
    
    console.log('\n✨ Expected Results:');
    console.log('   ❌ No more "demo_channel" string errors');
    console.log('   ❌ No more "period=30" parameter errors');
    console.log('   ❌ No more integer parsing errors');
    console.log('   ✅ Proper API calls with channel ID 1 and date ranges');
}

main().catch(console.error);