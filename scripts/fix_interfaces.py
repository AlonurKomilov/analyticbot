#!/usr/bin/env python3
"""
Fix interface files with correct Python syntax
"""

from pathlib import Path


def fix_interface_files():
    """Fix all interface files with proper indentation"""

    print("🔧 FIXING INTERFACE FILES SYNTAX")
    print("=" * 33)

    interfaces_dir = Path("src/shared_kernel/domain/interfaces")

    # Fix analytics_service.py - already fixed

    # Fix identity_service.py
    identity_content = '''"""
IdentityService Interface - Public API for identity module
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from datetime import datetime


@runtime_checkable
class IdentityService(Protocol):
    """IdentityService public interface"""
    
    async def authenticate_user(self, credentials: dict) -> Optional[dict]:
        """authenticate_user operation"""
        ...

    async def get_user_profile(self, user_id: int) -> Optional[dict]:
        """get_user_profile operation"""
        ...

    async def update_user_profile(self, user_id: int, data: dict) -> dict:
        """update_user_profile operation"""
        ...

    async def create_user(self, user_data: dict) -> dict:
        """create_user operation"""
        ...
'''

    with open(interfaces_dir / "identity_service.py", "w") as f:
        f.write(identity_content)
    print("   ✅ Fixed identity_service.py")

    # Fix payments_service.py
    payments_content = '''"""
PaymentService Interface - Public API for payments module
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from datetime import datetime


@runtime_checkable
class PaymentService(Protocol):
    """PaymentService public interface"""
    
    async def process_payment(self, payment_data: dict) -> dict:
        """process_payment operation"""
        ...

    async def get_payment_status(self, payment_id: int) -> str:
        """get_payment_status operation"""
        ...

    async def get_user_billing(self, user_id: int) -> dict:
        """get_user_billing operation"""
        ...

    async def cancel_subscription(self, user_id: int) -> bool:
        """cancel_subscription operation"""
        ...
'''

    with open(interfaces_dir / "payments_service.py", "w") as f:
        f.write(payments_content)
    print("   ✅ Fixed payments_service.py")

    # Fix channels_service.py
    channels_content = '''"""
ChannelService Interface - Public API for channels module
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from datetime import datetime


@runtime_checkable
class ChannelService(Protocol):
    """ChannelService public interface"""
    
    async def get_channel_info(self, channel_id: int) -> Optional[dict]:
        """get_channel_info operation"""
        ...

    async def add_channel(self, user_id: int, channel_data: dict) -> dict:
        """add_channel operation"""
        ...

    async def remove_channel(self, channel_id: int) -> bool:
        """remove_channel operation"""
        ...

    async def get_user_channels(self, user_id: int) -> List[dict]:
        """get_user_channels operation"""
        ...
'''

    with open(interfaces_dir / "channels_service.py", "w") as f:
        f.write(channels_content)
    print("   ✅ Fixed channels_service.py")

    # Fix bot_service_service.py
    bot_service_content = '''"""
BotService Interface - Public API for bot_service module
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from datetime import datetime


@runtime_checkable
class BotService(Protocol):
    """BotService public interface"""
    
    async def send_message(self, chat_id: int, message: str) -> dict:
        """send_message operation"""
        ...

    async def process_command(self, command: str, user_id: int) -> dict:
        """process_command operation"""
        ...

    async def handle_callback(self, callback_data: dict) -> dict:
        """handle_callback operation"""
        ...

    async def get_bot_status(self) -> dict:
        """get_bot_status operation"""
        ...
'''

    with open(interfaces_dir / "bot_service_service.py", "w") as f:
        f.write(bot_service_content)
    print("   ✅ Fixed bot_service_service.py")

    print("\n🎉 ALL INTERFACE FILES FIXED!")


if __name__ == "__main__":
    fix_interface_files()
