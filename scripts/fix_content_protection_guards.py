#!/usr/bin/env python3
"""
Script to add guard clauses to all callback handlers in content_protection.py
Fixes aiogram type warnings by adding proper type narrowing
"""

import re
from pathlib import Path


def add_guard_clause_to_callback(content: str, func_name: str) -> str:
    """Add guard clause after function signature if not present"""

    # Pattern to find function and its first line
    pattern = rf'(async def {func_name}\(callback: CallbackQuery[^)]*\):\s*\n\s*"""[^"]*"""\s*\n)'

    guard_clause = """
    # Guard clauses for type safety
    if not callback.message:
        await callback.answer("❌ Invalid callback state")
        return

"""

    def replacer(match):
        func_header = match.group(1)
        # Check if guard already exists
        if "Guard clauses" in content[match.end() : match.end() + 200]:
            return func_header
        return func_header + guard_clause

    return re.sub(pattern, replacer, content)


def main():
    file_path = Path(
        "/home/abcdeveloper/projects/analyticbot/apps/bot/handlers/content_protection.py"
    )

    # Read file
    content = file_path.read_text()

    # Callback handlers that need guards (excluding already fixed ones)
    handlers_to_fix = [
        "handle_custom_watermark_text",
        "handle_custom_emoji_start",
        "handle_theft_check_start",
        "handle_usage_stats",
        "handle_upgrade_premium",
        "handle_cancel",
    ]

    # Add guards to each
    for handler in handlers_to_fix:
        content = add_guard_clause_to_callback(content, handler)

    # Write back
    file_path.write_text(content)
    print(f"✅ Added guard clauses to {len(handlers_to_fix)} callback handlers")


if __name__ == "__main__":
    main()
