#!/bin/bash
# Test script for Admin MTProto Pool Configuration API

API_URL="http://localhost:11400"
TOKEN="YOUR_ADMIN_TOKEN_HERE"

echo "=== Testing Admin MTProto Pool Configuration API ==="
echo ""

echo "1. Get Current Configuration"
echo "GET /admin/system/mtproto/pool/config"
curl -s -X GET "$API_URL/admin/system/mtproto/pool/config" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
echo ""
echo ""

echo "2. Get Current Pool Status"
echo "GET /admin/system/mtproto/pool/status"
curl -s -X GET "$API_URL/admin/system/mtproto/pool/status" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
echo ""
echo ""

echo "3. Update Configuration (Example: Set max_connections to 20)"
echo "PUT /admin/system/mtproto/pool/config"
curl -s -X PUT "$API_URL/admin/system/mtproto/pool/config" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent_users": 20,
    "max_connections_per_user": 1,
    "session_timeout": 600,
    "connection_timeout": 300,
    "idle_timeout": 180
  }' \
  | jq '.'
echo ""
echo ""

echo "4. Verify Configuration Updated"
echo "GET /admin/system/mtproto/pool/config"
curl -s -X GET "$API_URL/admin/system/mtproto/pool/config" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
echo ""
echo ""

echo "=== Test Complete ==="
echo "Note: Changes require MTProto worker restart to take effect"
echo "Run: make -f Makefile.dev dev-stop && make -f Makefile.dev dev-start"
