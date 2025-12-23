#!/bin/bash
# Test MTProto endpoints

echo "========================================="
echo "Testing MTProto Backend Endpoints"
echo "========================================="
echo ""

# Get a test token (you'll need to replace this with a real token)
# For now, we'll just test that endpoints exist

echo "1. Testing /user-mtproto/status endpoint..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:11400/api/user-mtproto/status
echo ""

echo "2. Testing /user-mtproto/test-connection endpoint..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -X POST http://localhost:11400/api/user-mtproto/test-connection
echo ""

echo "3. Testing /user-mtproto/toggle endpoint..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -X POST http://localhost:11400/api/user-mtproto/toggle -H "Content-Type: application/json" -d '{"enabled": true}'
echo ""

echo "4. Checking API documentation for MTProto endpoints..."
curl -s http://localhost:11400/openapi.json | jq -r '.paths | keys[] | select(contains("mtproto"))' | head -15
echo ""

echo "========================================="
echo "Frontend Status"
echo "========================================="
echo "User Frontend: http://localhost:11300"
echo "MTProto Monitoring Page: http://localhost:11300/settings/mtproto-monitoring"
echo ""

echo "✅ Test complete!"
