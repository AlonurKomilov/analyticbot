"""
MTProto Service Providers

Factory functions for creating MTProto-related services with proper dependency injection.
"""

from apps.api.services.channel_admin_check_service import ChannelAdminCheckService


def create_channel_admin_check_service(
    mtproto_service,
) -> ChannelAdminCheckService:
    """
    Factory for ChannelAdminCheckService.

    Args:
        mtproto_service: MTProtoService for getting user clients

    Returns:
        ChannelAdminCheckService instance
    """
    return ChannelAdminCheckService(mtproto_service=mtproto_service)


# Note: TelegramStorageService uses a different pattern (factory method)
# and doesn't need a DI provider since it's created on-demand per request
# with user-specific credentials.
