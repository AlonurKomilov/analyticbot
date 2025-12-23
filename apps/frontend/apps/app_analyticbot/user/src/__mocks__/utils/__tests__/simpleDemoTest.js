/**
 * Simple Demo User System Test
 *
 * This script demonstrates the demo user functionality
 */

// Mock localStorage for Node.js environment
global.localStorage = {
    _storage: {},
    setItem(key, value) {
        this._storage[key] = value;
    },
    getItem(key) {
        return this._storage[key] || null;
    },
    removeItem(key) {
        delete this._storage[key];
    }
};

async function testDemoUserSystem() {
    console.log('🧪 Testing Demo User System...\n');

    // Import our functions
    const {
        isDemoUser,
        markUserAsDemo,
        clearDemoStatus,
        getDemoUserStatus,
        showDemoUserGuidance
    } = await import('../demoUserUtils.js');

    // Test 1: Initially not a demo user
    console.log('1. Initial state:');
    console.log('   isDemoUser():', isDemoUser());
    console.log('   Status:', getDemoUserStatus());

    // Test 2: Mark as demo user
    console.log('\n2. After marking as demo user:');
    markUserAsDemo();
    console.log('   isDemoUser():', isDemoUser());
    console.log('   Status:', getDemoUserStatus());
    console.log('   Guidance shown:', showDemoUserGuidance());

    // Test 3: Clear demo status
    console.log('\n3. After clearing demo status:');
    clearDemoStatus();
    console.log('   isDemoUser():', isDemoUser());
    console.log('   Status:', getDemoUserStatus());

    console.log('\n✅ Demo User System Test Complete!');
}

// Run the test
testDemoUserSystem().catch(console.error);
