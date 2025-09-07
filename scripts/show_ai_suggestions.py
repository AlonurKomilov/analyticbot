#!/usr/bin/env python3
"""
Show AI suggestions from Smart Auto-Fixer
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.ai_fix_enhanced import CodeFixer


async def main():
    """Show AI suggestions without applying them"""
    print("🔍 Getting AI suggestions from Smart Auto-Fixer...")

    fixer = CodeFixer()

    # Analyze issues
    print("📋 Analyzing code issues...")
    issues = fixer.analyze_code_issues()

    # Show current issues
    print("\n📊 Current Issues Found:")
    for issue_type, issue_list in issues.items():
        if issue_list:
            print(f"  • {issue_type}: {len(issue_list)}")
            # Show first few issues as examples
            for i, issue in enumerate(issue_list[:3]):
                print(f"    {i+1}. {issue}")
            if len(issue_list) > 3:
                print(f"    ... and {len(issue_list) - 3} more")

    # Get AI suggestions
    has_issues = any(len(issue_list) > 0 for issue_list in issues.values())
    if fixer.client and has_issues:
        print("\n🤖 Getting AI suggestions from Claude 3.5 Haiku...")
        prompt = fixer.create_ai_prompt(None, issues)
        ai_response = await fixer.get_ai_suggestions(prompt)

        if ai_response:
            print("\n" + "=" * 60)
            print("🎯 AI SUGGESTIONS FROM CLAUDE 3.5 HAIKU")
            print("=" * 60)
            print(ai_response)
            print("=" * 60)

            # Parse and show structured fixes
            fixes = fixer.parse_ai_suggestions(ai_response)
            if fixes:
                print(f"\n📝 Parsed {len(fixes)} actionable fixes:")
                for i, fix in enumerate(fixes, 1):
                    print(f"\n{i}. File: {fix.get('file', 'Unknown')}")
                    print(f"   Line: {fix.get('line', 'Unknown')}")
                    print(f"   Issue: {fix.get('issue', 'Unknown')}")
                    if fix.get("explanation"):
                        print(f"   Explanation: {fix['explanation']}")
        else:
            print("❌ No AI suggestions received")
    elif not fixer.client:
        print("❌ AI client not available (check ANTHROPIC_API_KEY)")
    else:
        print("✅ No issues found - code looks good!")


if __name__ == "__main__":
    asyncio.run(main())
