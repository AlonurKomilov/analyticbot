#!/bin/bash

# Test script to check admin status API response
# This helps debug what the backend is returning

echo "🧪 Testing Admin Status API Response"
echo "======================================="
echo ""
echo "To test manually:"
echo "1. Open browser DevTools (F12)"
echo "2. Go to Console tab"
echo "3. Type: localStorage.getItem('token')"
echo "4. Copy the token value"
echo "5. Run: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:11400/channels/admin-status/check-all | jq"
echo ""
echo "Expected response should include:"
echo "  \"mtproto_disabled\": true (for disabled channels)"
echo "  \"mtproto_disabled\": false (for enabled channels)"
echo ""
echo "If mtproto_disabled field is missing, the frontend won't show the disabled state!"
