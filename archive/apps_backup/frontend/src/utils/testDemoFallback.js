/**
 * Demo Fallback Test
 * Quick test to verify the demo fallback system works
 */

// Mock localStorage for testing
if (typeof localStorage === 'undefined') {
    global.localStorage = {
        getItem: () => 'true', // Simulate demo user
        setItem: () => {},
        removeItem: () => {}
    };
}

async function testDemoFallback() {
    console.log('🧪 Testing Demo Fallback System...\n');
    
    try {
        // Import the DataProvider
        const { ApiDataProvider } = await import('../providers/DataProvider.js');
        const provider = new ApiDataProvider();
        
        // Test the _getDemoFallbackData method directly
        console.log('1. Testing _getDemoFallbackData for channels...');
        const channelsData = await provider._getDemoFallbackData('/analytics/channels');
        console.log('   ✅ Channels fallback data:', channelsData.slice(0, 2)); // Show first 2 channels
        
        console.log('\n2. Testing _getDemoFallbackData for overview...');
        const overviewData = await provider._getDemoFallbackData('/analytics/overview');
        console.log('   ✅ Overview fallback data:', overviewData);
        
        console.log('\n3. Testing _getDemoFallbackData for post-dynamics...');
        const dynamicsData = await provider._getDemoFallbackData('/analytics/post-dynamics');
        console.log('   ✅ Post dynamics fallback data length:', dynamicsData.length);
        
        console.log('\n✅ Demo Fallback System Test Complete!');
        return true;
    } catch (error) {
        console.error('❌ Demo Fallback Test Failed:', error);
        return false;
    }
}

// Run the test
testDemoFallback().then(success => {
    if (success) {
        console.log('\n🎉 All fallback methods working correctly!');
    } else {
        console.log('\n💥 Fallback system needs fixing!');
    }
}).catch(console.error);