#!/bin/bash
# Login Endpoint Diagnostic Script

echo "==================================="
echo "🔍 LOGIN ENDPOINT DIAGNOSTICS"
echo "==================================="
echo ""

# Test 1: Check if backend is running
echo "1️⃣ Checking if backend is running..."
if ps aux | grep -q "[u]vicorn.*11400"; then
    echo "✅ Backend is running on port 11400"
else
    echo "❌ Backend is NOT running"
    exit 1
fi
echo ""

# Test 2: Check if database is accessible
echo "2️⃣ Checking database connection..."
cd /home/abcdeveloper/projects/analyticbot
python3 << 'PYTHON'
import sys
sys.path.insert(0, '/home/abcdeveloper/projects/analyticbot')
try:
    from infra.database import SessionLocal
    db = SessionLocal()
    result = db.execute("SELECT 1").scalar()
    print("✅ Database connection successful")
    db.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
PYTHON
echo ""

# Test 3: Check if users exist
echo "3️⃣ Checking for existing users..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, '/home/abcdeveloper/projects/analyticbot')
try:
    from infra.database import SessionLocal
    from core.models import User
    db = SessionLocal()
    user_count = db.query(User).count()
    print(f"✅ Found {user_count} users in database")
    if user_count > 0:
        first_user = db.query(User).first()
        print(f"   Sample user: {first_user.email} (status: {first_user.status})")
    db.close()
except Exception as e:
    print(f"❌ Failed to query users: {e}")
    sys.exit(1)
PYTHON
echo ""

# Test 4: Test login endpoint with valid data
echo "4️⃣ Testing login endpoint..."
curl -s -X POST "http://localhost:11400/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin12345"}' \
  | python3 -m json.tool 2>&1 | head -20
echo ""

# Test 5: Check recent backend logs
echo "5️⃣ Checking recent backend logs..."
if [ -f "logs/api.log" ]; then
    echo "Last 10 lines of api.log:"
    tail -10 logs/api.log
else
    echo "⚠️  No api.log file found"
fi
echo ""

echo "==================================="
echo "✅ Diagnostics complete"
echo "==================================="
