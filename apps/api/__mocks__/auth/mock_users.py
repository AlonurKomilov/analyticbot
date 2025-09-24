"""
Authentication Mock Data Module
Extracted from auth_router.py to maintain clean separation of mock data
Provides seamless demo user experience for showcasing the platform
"""

import bcrypt

# Demo user credentials (publicly known for demonstration)
DEMO_CREDENTIALS = {
    "demo@analyticbot.com": "demo123456",
    "viewer@analyticbot.com": "viewer123",
    "guest@analyticbot.com": "guest123",
}


def _hash_password(password: str) -> str:
    """Hash password for demo users"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_mock_users_database() -> dict[str, dict]:
    """Create mock users database for development/testing and demos"""
    return {
        # Development/Testing Users
        "test@example.com": {
            "id": "test_12345",
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "$2b$12$example_hash",
            "is_demo": False,
            "plan": "free",
        },
        # Demo Users (for public demonstrations)
        "demo@analyticbot.com": {
            "id": "demo_user_001",
            "email": "demo@analyticbot.com",
            "username": "Demo User",
            "hashed_password": _hash_password("demo123456"),
            "is_demo": True,
            "plan": "pro",
            "demo_type": "full_featured",
            "description": "Full-featured demo account with all capabilities",
        },
        "viewer@analyticbot.com": {
            "id": "demo_viewer_002",
            "email": "viewer@analyticbot.com",
            "username": "Demo Viewer",
            "hashed_password": _hash_password("viewer123"),
            "is_demo": True,
            "plan": "basic",
            "demo_type": "read_only",
            "description": "Read-only demo account for viewing analytics",
        },
        "guest@analyticbot.com": {
            "id": "demo_guest_003",
            "email": "guest@analyticbot.com",
            "username": "Demo Guest",
            "hashed_password": _hash_password("guest123"),
            "is_demo": True,
            "plan": "free",
            "demo_type": "limited",
            "description": "Limited demo account with basic features",
        },
        # Admin Demo User
        "admin@analyticbot.com": {
            "id": "demo_admin_999",
            "email": "admin@analyticbot.com",
            "username": "Demo Admin",
            "hashed_password": "$2b$12$admin_hash",
            "is_demo": True,
            "is_admin": True,
            "plan": "enterprise",
            "demo_type": "admin",
            "description": "Admin demo account with full system access",
        },
    }


def get_mock_user_by_email(email: str) -> dict | None:
    """Get mock user by email (development/testing fallback)"""
    mock_users = create_mock_users_database()
    return mock_users.get(email)


def is_demo_user(email: str) -> bool:
    """Check if email belongs to a demo user"""
    mock_users = create_mock_users_database()
    user = mock_users.get(email)
    return user is not None and user.get("is_demo", False)


def is_demo_user_by_id(user_id: str) -> bool:
    """Check if user ID belongs to a demo user"""
    mock_users = create_mock_users_database()
    for user in mock_users.values():
        if user["id"] == user_id:
            return user.get("is_demo", False)
    return False


def get_demo_user_type(email: str) -> str | None:
    """Get demo user type (full_featured, read_only, limited, admin)"""
    mock_users = create_mock_users_database()
    user = mock_users.get(email)
    if user and user.get("is_demo", False):
        return user.get("demo_type", "limited")
    return None


def get_demo_user_by_email(email: str) -> dict | None:
    """Get demo user by email for authentication"""
    mock_users = create_mock_users_database()
    user = mock_users.get(email)
    if user and user.get("is_demo", False):
        return {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "hashed_password": user["hashed_password"],
        }
    return None


def get_demo_user_type_by_id(user_id: str) -> str | None:
    """Get demo user type by user ID"""
    mock_users = create_mock_users_database()
    for user in mock_users.values():
        if user["id"] == user_id and user.get("is_demo", False):
            return user.get("demo_type", "limited")
    return None


def get_demo_credentials_info() -> dict:
    """Get public demo credentials for documentation/frontend"""
    return {
        "demo_accounts": [
            {
                "email": "demo@analyticbot.com",
                "password": "demo123456",
                "type": "full_featured",
                "description": "Full-featured demo with all Pro features",
            },
            {
                "email": "viewer@analyticbot.com",
                "password": "viewer123",
                "type": "read_only",
                "description": "Read-only analytics viewer",
            },
            {
                "email": "guest@analyticbot.com",
                "password": "guest123",
                "type": "limited",
                "description": "Basic features demo",
            },
        ],
        "note": "These are public demo accounts for trying the platform",
    }


def verify_demo_password(email: str, password: str) -> bool:
    """Verify demo user password"""
    if email not in DEMO_CREDENTIALS:
        return False

    expected_password = DEMO_CREDENTIALS[email]
    return password == expected_password


def simulate_password_update(user_id: str, hashed_password: str) -> bool:
    """Simulate password update operation for development/testing"""
    # In production, this would update the actual database
    # For demo users, password updates are ignored
    if is_demo_user_by_id(user_id):
        return False  # Demo users can't change passwords
    return True
