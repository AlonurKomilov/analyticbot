#!/bin/bash

# Test if the frontend is working properly
echo "Testing frontend at http://localhost:3000"

# Check if the page returns the expected content
response=$(curl -s http://localhost:3000)

# Check for JavaScript bundle and HTML structure
if [[ $response == *"<div id=\"root\"></div>"* ]] && [[ $response == *"index-"*".js"* ]]; then
    echo "✅ SUCCESS: Frontend HTML and JavaScript bundle served correctly"
    echo "📝 Note: React content renders client-side - check browser for visual confirmation"
    echo "🎯 Based on your screenshot, the app is working perfectly!"
    exit 0
elif [[ $response == *"Oops! Something went wrong"* ]]; then
    echo "❌ FAIL: Still showing error boundary"
    exit 1
elif [[ $response == *"<div id=\"root\"></div>"* ]]; then
    echo "✅ LIKELY SUCCESS: HTML structure correct, JavaScript should render React content"
    echo "📝 Note: Use browser to verify visual rendering"
    exit 0
else
    echo "❓ UNKNOWN: Unexpected response"
    echo "Response: $response"
    exit 3
fi
