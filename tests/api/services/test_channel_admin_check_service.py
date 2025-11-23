"""
Unit tests for ChannelAdminCheckService

Tests the MTProto admin checking service with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.api.services.channel_admin_check_service import ChannelAdminCheckService


@pytest.fixture
def mock_mtproto_service():
    """Mock MTProtoService."""
    return AsyncMock()


@pytest.fixture
def mock_mtproto_client():
    """Mock MTProto client with Telethon client."""
    client = MagicMock()
    client.client = AsyncMock()
    return client


@pytest.fixture
def service(mock_mtproto_service):
    """Create ChannelAdminCheckService with mocked dependencies."""
    return ChannelAdminCheckService(mtproto_service=mock_mtproto_service)


@pytest.mark.asyncio
async def test_check_admin_status_no_client(service, mock_mtproto_service):
    """Test when MTProto client is not available."""
    mock_mtproto_service.get_user_client.return_value = None

    result = await service.check_mtproto_admin_status(
        user_id=123,
        channel_id=456,
        channel_username="@testchannel",
        telegram_id=-1001234567890,
    )

    assert result["is_admin"] is False
    assert result["error"] == "MTProto client not available for user"
    assert result["method_used"] == "failed"


@pytest.mark.asyncio
async def test_check_admin_status_import_error(service, mock_mtproto_service, mock_mtproto_client):
    """Test when Telethon library is not available."""
    mock_mtproto_service.get_user_client.return_value = mock_mtproto_client

    with patch(
        "apps.api.services.channel_admin_check_service.GetParticipantRequest",
        side_effect=ImportError("No telethon"),
    ):
        result = await service.check_mtproto_admin_status(
            user_id=123,
            channel_id=456,
            channel_username="@testchannel",
        )

    assert result["is_admin"] is False
    assert "telethon" in result["error"].lower()
    assert result["method_used"] == "failed"


@pytest.mark.asyncio
async def test_check_admin_status_username_success(
    service, mock_mtproto_service, mock_mtproto_client
):
    """Test successful admin check via username."""
    mock_mtproto_service.get_user_client.return_value = mock_mtproto_client

    # Mock entity resolution via username
    mock_entity = MagicMock()
    mock_mtproto_client.client.get_entity.return_value = mock_entity

    # Mock get_me
    mock_me = MagicMock()
    mock_mtproto_client.client.get_me.return_value = mock_me

    # Mock participant response (admin)
    mock_participant_obj = MagicMock()
    mock_participant_obj.__class__.__name__ = "ChannelParticipantAdmin"
    mock_participant_obj.admin_rights = MagicMock(
        change_info=True,
        post_messages=True,
        edit_messages=True,
        delete_messages=True,
        ban_users=False,
        invite_users=True,
        pin_messages=True,
        add_admins=False,
        manage_call=False,
    )

    mock_participant = MagicMock()
    mock_participant.participant = mock_participant_obj
    mock_mtproto_client.client.return_value = mock_participant

    result = await service.check_mtproto_admin_status(
        user_id=123,
        channel_id=456,
        channel_username="@testchannel",
    )

    assert result["is_admin"] is True
    assert result["method_used"] == "username"
    assert result["participant_type"] == "ChannelParticipantAdmin"
    assert result["admin_rights"] is not None
    assert result["admin_rights"]["post_messages"] is True
    assert result["error"] is None


@pytest.mark.asyncio
async def test_check_admin_status_telegram_id_fallback(
    service, mock_mtproto_service, mock_mtproto_client
):
    """Test fallback to telegram_id when username fails."""
    mock_mtproto_service.get_user_client.return_value = mock_mtproto_client

    # Mock entity resolution: username fails, ID succeeds
    mock_entity = MagicMock()

    async def get_entity_side_effect(identifier):
        if isinstance(identifier, str):
            raise Exception("Username not found")
        return mock_entity

    mock_mtproto_client.client.get_entity.side_effect = get_entity_side_effect

    # Mock get_me
    mock_me = MagicMock()
    mock_mtproto_client.client.get_me.return_value = mock_me

    # Mock participant response (creator)
    mock_participant_obj = MagicMock()
    mock_participant_obj.__class__.__name__ = "ChannelParticipantCreator"

    mock_participant = MagicMock()
    mock_participant.participant = mock_participant_obj
    mock_mtproto_client.client.return_value = mock_participant

    result = await service.check_mtproto_admin_status(
        user_id=123,
        channel_id=456,
        channel_username="@testchannel",
        telegram_id=-1001234567890,
    )

    assert result["is_admin"] is True
    assert result["method_used"] == "telegram_id"
    assert result["participant_type"] == "ChannelParticipantCreator"


@pytest.mark.asyncio
async def test_check_admin_status_not_admin(service, mock_mtproto_service, mock_mtproto_client):
    """Test when user is not admin (regular member)."""
    mock_mtproto_service.get_user_client.return_value = mock_mtproto_client

    # Mock entity resolution
    mock_entity = MagicMock()
    mock_mtproto_client.client.get_entity.return_value = mock_entity

    # Mock get_me
    mock_me = MagicMock()
    mock_mtproto_client.client.get_me.return_value = mock_me

    # Mock participant response (regular member)
    mock_participant_obj = MagicMock()
    mock_participant_obj.__class__.__name__ = "ChannelParticipant"

    mock_participant = MagicMock()
    mock_participant.participant = mock_participant_obj
    mock_mtproto_client.client.return_value = mock_participant

    result = await service.check_mtproto_admin_status(
        user_id=123,
        channel_id=456,
        channel_username="@testchannel",
    )

    assert result["is_admin"] is False
    assert result["participant_type"] == "ChannelParticipant"


@pytest.mark.asyncio
async def test_check_admin_status_entity_resolution_failure(
    service, mock_mtproto_service, mock_mtproto_client
):
    """Test when entity cannot be resolved."""
    mock_mtproto_service.get_user_client.return_value = mock_mtproto_client

    # Mock entity resolution failure
    mock_mtproto_client.client.get_entity.side_effect = Exception("Channel not found")

    result = await service.check_mtproto_admin_status(
        user_id=123,
        channel_id=456,
        channel_username="@testchannel",
        telegram_id=-1001234567890,
    )

    assert result["is_admin"] is False
    assert "Failed to resolve channel entity" in result["error"]
    assert result["method_used"] == "failed"


@pytest.mark.asyncio
async def test_check_admin_status_unexpected_error(
    service, mock_mtproto_service, mock_mtproto_client
):
    """Test handling of unexpected errors."""
    mock_mtproto_service.get_user_client.side_effect = Exception("Database error")

    result = await service.check_mtproto_admin_status(
        user_id=123,
        channel_id=456,
    )

    assert result["is_admin"] is False
    assert "Unexpected error" in result["error"]
    assert "Database error" in result["error"]
