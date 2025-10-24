# 🧪 Testing Telegram Login Widget

## Quick Test Checklist

### ✅ Backend Tests

```bash
# 1. Start your backend
cd /home/abcdeveloper/projects/analyticbot
python -m uvicorn apps.api.main:app --reload --port 8000

# 2. Check new endpoints are registered
curl http://localhost:8000/docs

# Should see:
# - POST /api/auth/telegram/login
# - GET /api/auth/telegram/callback
# - POST /api/auth/telegram/link
```

### ✅ Manual Testing Steps

#### Test 1: Validate Telegram Auth (Unit Test)

```python
# test_telegram_auth.py
import os
from apps.api.routers.auth.telegram_login import validate_telegram_auth

def test_validate_telegram_auth():
    """Test Telegram authentication validation"""

    # Get your bot token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Sample Telegram data (THIS WILL FAIL - it's just for testing structure)
    auth_data = {
        "id": 123456789,
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "photo_url": "https://t.me/i/userpic/320/johndoe.jpg",
        "auth_date": 1698765432,
        "hash": "abc123def456"  # This will be invalid
    }

    # This should return False (invalid hash)
    result = validate_telegram_auth(auth_data, bot_token)
    print(f"Validation result (should be False): {result}")

    # To get REAL test data, you need to actually trigger Telegram widget
    # and capture the data it sends

if __name__ == "__main__":
    test_validate_telegram_auth()
```

Run: `python test_telegram_auth.py`

#### Test 2: Test with Real Telegram Data

**Step 1: Create Test HTML Page**

```html
<!-- test_telegram_login.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Test Telegram Login</title>
</head>
<body>
    <h1>Test Telegram Login Widget</h1>

    <div id="result"></div>

    <script>
        function onTelegramAuth(user) {
            // Display received data
            document.getElementById('result').innerHTML =
                '<h2>Received Data:</h2>' +
                '<pre>' + JSON.stringify(user, null, 2) + '</pre>';

            // Send to your backend
            fetch('http://localhost:8000/api/auth/telegram/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(user)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML +=
                    '<h2>Backend Response:</h2>' +
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(error => {
                document.getElementById('result').innerHTML +=
                    '<h2>Error:</h2>' +
                    '<pre>' + error.toString() + '</pre>';
            });
        }
    </script>

    <!-- Replace YOUR_BOT_USERNAME with your actual bot username -->
    <script
        async
        src="https://telegram.org/js/telegram-widget.js?22"
        data-telegram-login="YOUR_BOT_USERNAME"
        data-size="large"
        data-onauth="onTelegramAuth(user)"
        data-request-access="write">
    </script>
</body>
</html>
```

**Step 2: Serve HTML File**

```bash
# Simple HTTP server
python -m http.server 8080

# Open in browser
open http://localhost:8080/test_telegram_login.html
```

**Step 3: Click "Sign in with Telegram"**
- Opens Telegram app
- Confirms your identity
- Sends data to callback
- You'll see the data on screen

#### Test 3: Test Database Integration

```python
# test_telegram_db.py
import asyncio
from apps.api.middleware.auth import get_user_repository
from core.repositories.user_repository import UserRepository

async def test_telegram_user_creation():
    """Test creating and finding users by Telegram ID"""

    # Get repository
    user_repo = UserRepository()

    # Test data
    telegram_id = 123456789

    # Create user with Telegram ID
    new_user = await user_repo.create_user(
        email=f"telegram_{telegram_id}@telegram.local",
        username=f"tg_user_{telegram_id}",
        password=None,  # No password for Telegram auth
        full_name="Test Telegram User",
        telegram_id=telegram_id,
        telegram_username="testuser",
        telegram_verified=True,
        status="active",
    )

    print(f"✅ Created user: {new_user}")

    # Find by Telegram ID
    found_user = await user_repo.get_user_by_telegram_id(telegram_id)

    if found_user:
        print(f"✅ Found user by Telegram ID: {found_user['username']}")
    else:
        print("❌ Could not find user by Telegram ID")

    # Cleanup
    await user_repo.delete_user(new_user['id'])
    print("✅ Cleanup complete")

if __name__ == "__main__":
    asyncio.run(test_telegram_user_creation())
```

Run: `python test_telegram_db.py`

### ✅ Integration Tests

#### Test 4: Full Authentication Flow

```python
# test_telegram_flow.py
import requests
import os

BASE_URL = "http://localhost:8000/api"

def test_full_telegram_login_flow():
    """Test complete login flow"""

    # Step 1: Simulate Telegram widget data
    # (In reality, this comes from Telegram - this is just structure)
    telegram_data = {
        "id": 987654321,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "photo_url": "https://t.me/i/userpic/320/test.jpg",
        "auth_date": 1698765432,
        "hash": "calculated_by_telegram"
    }

    # Step 2: Send to login endpoint
    print("📤 Sending Telegram data to backend...")
    response = requests.post(
        f"{BASE_URL}/auth/telegram/login",
        json=telegram_data
    )

    print(f"📥 Response status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   Access Token: {data['access_token'][:20]}...")
        print(f"   User: {data['user']['username']}")

        # Step 3: Test authenticated request
        access_token = data['access_token']

        profile_response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if profile_response.status_code == 200:
            print("✅ Authenticated request successful!")
            profile = profile_response.json()
            print(f"   Profile: {profile['username']}")
        else:
            print("❌ Authenticated request failed")

    elif response.status_code == 401:
        print("❌ Authentication failed (expected with fake hash)")
        print(f"   Error: {response.json()}")
    else:
        print(f"❌ Unexpected error: {response.json()}")

if __name__ == "__main__":
    test_full_telegram_login_flow()
```

Run: `python test_telegram_flow.py`

#### Test 5: Link Telegram to Existing Account

```python
# test_telegram_link.py
import requests

BASE_URL = "http://localhost:8000/api"

def test_link_telegram_account():
    """Test linking Telegram to existing account"""

    # Step 1: Login with email/password
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "existing@user.com",
            "password": "yourpassword123"
        }
    )

    if login_response.status_code != 200:
        print("❌ Failed to login with email/password")
        return

    access_token = login_response.json()['access_token']
    print("✅ Logged in with email/password")

    # Step 2: Link Telegram account
    telegram_data = {
        "id": 111222333,
        "first_name": "John",
        "username": "johndoe",
        "auth_date": 1698765432,
        "hash": "calculated_by_telegram"
    }

    link_response = requests.post(
        f"{BASE_URL}/auth/telegram/link",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"telegram_data": telegram_data}
    )

    if link_response.status_code == 200:
        print("✅ Telegram account linked successfully!")
        print(f"   {link_response.json()}")
    else:
        print(f"❌ Failed to link: {link_response.json()}")

if __name__ == "__main__":
    test_link_telegram_account()
```

### ✅ Security Tests

#### Test 6: Hash Validation

```python
# test_hash_validation.py
from apps.api.routers.auth.telegram_login import validate_telegram_auth
import os

def test_invalid_hash():
    """Test that invalid hashes are rejected"""

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Data with tampered hash
    invalid_data = {
        "id": 123456,
        "first_name": "Hacker",
        "auth_date": 1698765432,
        "hash": "definitely_fake_hash_123"
    }

    result = validate_telegram_auth(invalid_data, bot_token)

    if result == False:
        print("✅ Invalid hash correctly rejected")
    else:
        print("❌ Security issue: Invalid hash accepted!")

def test_missing_hash():
    """Test that missing hash is rejected"""

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    data_without_hash = {
        "id": 123456,
        "first_name": "Test"
    }

    result = validate_telegram_auth(data_without_hash, bot_token)

    if result == False:
        print("✅ Missing hash correctly rejected")
    else:
        print("❌ Security issue: Missing hash accepted!")

if __name__ == "__main__":
    test_invalid_hash()
    test_missing_hash()
```

#### Test 7: Expiry Check

```python
# test_auth_expiry.py
from apps.api.routers.auth.telegram_login import is_auth_recent
import time

def test_auth_expiry():
    """Test authentication expiry checking"""

    # Recent timestamp (should pass)
    recent = int(time.time()) - 3600  # 1 hour ago
    result = is_auth_recent(recent, max_age_hours=24)

    if result:
        print("✅ Recent auth correctly accepted")
    else:
        print("❌ Recent auth rejected")

    # Old timestamp (should fail)
    old = int(time.time()) - (25 * 3600)  # 25 hours ago
    result = is_auth_recent(old, max_age_hours=24)

    if not result:
        print("✅ Expired auth correctly rejected")
    else:
        print("❌ Expired auth accepted")

if __name__ == "__main__":
    test_auth_expiry()
```

## 🎯 Production Testing Checklist

### Before Deploying

- [ ] Test with real Telegram account
- [ ] Verify hash validation works
- [ ] Test expiry checking
- [ ] Test database operations
- [ ] Test token generation
- [ ] Test linking existing accounts
- [ ] Test error handling
- [ ] Test CORS settings
- [ ] Test HTTPS (required for Telegram widget)
- [ ] Test on mobile devices

### Security Checks

- [ ] Hash validation always runs
- [ ] Expired auth is rejected
- [ ] Bot token is in environment variables (not code)
- [ ] Telegram IDs are stored securely
- [ ] Rate limiting on auth endpoints
- [ ] HTTPS enforced in production
- [ ] CORS properly configured

### User Experience

- [ ] Widget loads quickly
- [ ] Clear error messages
- [ ] Smooth redirect flow
- [ ] Works on mobile
- [ ] Works in different browsers
- [ ] Graceful fallback to email/password

## 📊 Expected Results

### Successful Login Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "123",
    "email": "telegram_987654321@telegram.local",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "user",
    "status": "active",
    "telegram_id": 987654321,
    "telegram_username": "johndoe"
  }
}
```

### Error Responses

**Invalid Hash:**
```json
{
  "detail": "Invalid Telegram authentication data"
}
```

**Expired Auth:**
```json
{
  "detail": "Authentication expired. Please try again."
}
```

**Already Linked:**
```json
{
  "detail": "This Telegram account is already linked to another user"
}
```

## 🚀 Next Steps

1. Run all tests locally
2. Fix any failures
3. Test with real Telegram account
4. Deploy to staging
5. Test on staging with HTTPS
6. Deploy to production

## 📞 Troubleshooting

**Widget doesn't show:**
- Check bot username is correct
- Check script URL is loaded
- Check browser console for errors

**Hash validation fails:**
- Verify bot token is correct
- Check data format matches Telegram's
- Ensure all fields are included in hash calculation

**Database errors:**
- Check migration ran successfully
- Verify telegram_id column exists
- Check unique constraint on telegram_id

**CORS errors:**
- Configure CORS in FastAPI
- Allow your frontend domain
- Allow Telegram widget origin
