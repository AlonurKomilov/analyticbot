"""
Content Protection Handler Package

Refactored from single 841-line file into modular structure (Issue #4 Phase 2).

Module Structure:
- states.py: FSM states for workflows (20 lines)
- validation.py: Type guards and validators (45 lines)
- watermarking.py: Image watermarking handlers (250 lines)
- premium_features.py: Premium emoji features (150 lines)
- theft_detection.py: Content theft analysis (120 lines)
- usage_tracking.py: Feature usage statistics (75 lines)
- services/tier_service.py: User tier management (160 lines)
- router.py: Router aggregation (30 lines)

Total: ~850 lines (9 files, avg ~95 lines/file)

✅ Clean Architecture Fix (Issue #4 Phase 2.8):
- Removed direct DB imports from handlers
- Uses DI container for repository injection
- Follows clean architecture (apps -> core -> infra)
- Fixed import linter violations

Migration Note:
- Old: apps.bot.handlers.content_protection (single file)
- New: apps.bot.handlers.content_protection.router (package)
"""

from .router import router
from .states import ContentProtectionStates

__all__ = ["router", "ContentProtectionStates"]
