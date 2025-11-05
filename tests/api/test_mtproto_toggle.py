"""
Test MTProto Toggle Functionality
Tests the new enable/disable toggle endpoint
"""

import pytest
from fastapi import status


class TestMTProtoToggle:
    """Test MTProto enable/disable toggle"""

    def test_toggle_mtproto_disabled(self, client_with_auth, user_with_mtproto):
        """Test disabling MTProto"""
        # Toggle to disabled
        response = client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": False})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "disabled" in data["message"].lower()

    def test_toggle_mtproto_enabled(self, client_with_auth, user_with_mtproto):
        """Test enabling MTProto"""
        # First disable
        client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": False})

        # Then enable
        response = client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": True})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "enabled" in data["message"].lower()

    def test_toggle_reflects_in_status(self, client_with_auth, user_with_mtproto):
        """Test that toggle status is reflected in status endpoint"""
        # Disable MTProto
        client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": False})

        # Check status
        response = client_with_auth.get("/api/user-mtproto/status")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # When disabled, can_read_history should be False
        assert data["can_read_history"] is False

        # Re-enable
        client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": True})

        # Check status again
        response = client_with_auth.get("/api/user-mtproto/status")
        data = response.json()

        # When enabled and verified, can_read_history should be True
        if data["verified"] and data["connected"]:
            assert data["can_read_history"] is True

    def test_toggle_without_configuration(self, client_with_auth):
        """Test toggle fails without MTProto configuration"""
        response = client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": True})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "No MTProto configuration found" in data["detail"]

    def test_toggle_validation(self, client_with_auth, user_with_mtproto):
        """Test toggle request validation"""
        # Missing enabled field
        response = client_with_auth.post("/api/user-mtproto/toggle", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid type
        response = client_with_auth.post("/api/user-mtproto/toggle", json={"enabled": "yes"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Fixtures
@pytest.fixture
def user_with_mtproto(db_session, test_user):
    """Create user with MTProto configuration"""
    from core.models.user_bot_domain import BotStatus, UserBotCredentials
    from core.services.encryption_service import get_encryption_service

    encryption = get_encryption_service()

    credentials = UserBotCredentials(
        id=None,
        user_id=test_user.id,
        bot_token=encryption.encrypt("test_bot_token"),
        bot_username="test_bot",
        bot_id=123456,
        telegram_api_id=24113710,
        telegram_api_hash=encryption.encrypt("test_api_hash"),
        telegram_phone="+1234567890",
        session_string=encryption.encrypt("test_session"),
        status=BotStatus.ACTIVE,
        is_verified=True,
        mtproto_enabled=True,
    )

    from infra.db.repositories.user_bot_repository import UserBotRepository

    repo = UserBotRepository(db_session)

    # Save to database
    saved = repo.create(credentials)
    db_session.commit()

    return saved


@pytest.fixture
def client_with_auth(client, test_user):
    """Client with authentication token"""
    from apps.api.middleware.auth import create_access_token

    token = create_access_token(user_id=test_user.id)
    client.headers["Authorization"] = f"Bearer {token}"

    return client
