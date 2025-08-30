#!/usr/bin/env python3
"""
Enhanced AI-powered code fixer using Claude 3.5 Sonnet
Analyzes code issues and applies intelligent fixes
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from anthropic import Anthropic

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("⚠️  Anthropic library not available. Install with: pip install anthropic")

# Fallback fixes that don't require AI
AUTOMATED_FIXES = {
    "formatting": [
        ["ruff", "format", "."],
        ["ruff", "check", "--fix", "."],
        ["isort", ".", "--profile", "black"],
    ],
    "imports": [
        [
            "autoflake",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--in-place",
            "--recursive",
            ".",
        ],
        ["ruff", "check", "--select", "I", "--fix", "."],
    ],
    "security": [
        ["ruff", "check", "--select", "S", "--fix", "."],
        ["bandit", "-r", ".", "--format", "json", "--output", "bandit-report.json"],
    ],
    "performance": [
        ["ruff", "check", "--select", "PERF,UP", "--fix", "."],
    ],
    "type-hints": [
        ["pyupgrade", "--py311-plus"]
        + [
            str(p)
            for p in Path(".").rglob("*.py")
            if not any(part.startswith(".") for part in p.parts)
        ],
    ],
}


class CodeFixer:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key and HAS_ANTHROPIC:
            self.client = Anthropic(api_key=self.api_key)

    def run_command(self, cmd: list[str], capture_output: bool = True) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, timeout=300)
                return result.returncode, "", ""
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def apply_automated_fixes(self, fix_type: str = "all") -> dict[str, bool]:
        """Apply automated fixes without AI"""
        results = {}

        if fix_type == "all":
            fix_types = list(AUTOMATED_FIXES.keys())
        else:
            fix_types = [fix_type] if fix_type in AUTOMATED_FIXES else []

        print(f"🔧 Applying automated fixes: {', '.join(fix_types)}")

        for ftype in fix_types:
            print(f"\n📋 Applying {ftype} fixes...")
            success = True

            for cmd in AUTOMATED_FIXES[ftype]:
                print(f"  Running: {' '.join(cmd[:3])}{'...' if len(cmd) > 3 else ''}")
                exit_code, stdout, stderr = self.run_command(cmd)

                if (
                    exit_code != 0 and "bandit" not in cmd[0]
                ):  # Bandit may return non-zero for warnings
                    print(f"  ⚠️  Command failed: {stderr}")
                    success = False
                else:
                    print("  ✅ Success")

            results[ftype] = success

        return results

    def analyze_code_issues(self) -> dict[str, list[str]]:
        """Analyze code and identify issues"""
        issues = {
            "syntax_errors": [],
            "type_errors": [],
            "test_failures": [],
            "security_issues": [],
            "performance_issues": [],
        }

        # Check for Python syntax errors
        print("🔍 Checking for syntax errors...")
        for py_file in Path(".").rglob("*.py"):
            if any(part.startswith(".") for part in py_file.parts):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), str(py_file), "exec")
            except SyntaxError as e:
                issues["syntax_errors"].append(f"{py_file}:{e.lineno}: {e.msg}")

        # Run mypy for type errors
        print("🏷️  Checking type errors...")
        exit_code, stdout, stderr = self.run_command(["mypy", ".", "--ignore-missing-imports"])
        if exit_code != 0:
            issues["type_errors"] = stdout.split("\n")[:10]  # Limit output

        # Run tests to find failures
        print("🧪 Running tests...")
        exit_code, stdout, stderr = self.run_command(["pytest", "-q", "--maxfail=5"])
        if exit_code != 0:
            issues["test_failures"] = stdout.split("\n")[:10]  # Limit output

        # Security check with bandit
        print("🔒 Security analysis...")
        exit_code, stdout, stderr = self.run_command(["bandit", "-r", ".", "-f", "json"])
        if exit_code != 0 and stdout:
            try:
                bandit_results = json.loads(stdout)
                for result in bandit_results.get("results", [])[:5]:  # Limit to 5 issues
                    issues["security_issues"].append(
                        f"{result.get('filename', '')}:{result.get('line_number', '')}: "
                        f"{result.get('issue_text', '')}"
                    )
            except json.JSONDecodeError:
                pass

        return issues

    def create_ai_prompt(self, context_file: str | None = None, issues: dict | None = None) -> str:
        """Create a prompt for Claude AI to fix code issues"""
        prompt = """You are an expert Python developer helping to fix code quality issues. 

Please analyze the following code issues and provide specific, actionable fixes. Focus on:
1. Fixing syntax and type errors
2. Improving code structure and readability  
3. Addressing security vulnerabilities
4. Optimizing performance where possible
5. Ensuring tests pass

For each fix, provide:
- The specific file and line number
- The current problematic code
- The corrected code
- A brief explanation of why this fix is needed

"""

        if context_file and os.path.exists(context_file):
            with open(context_file, encoding="utf-8") as f:
                content = f.read()[:50000]  # Limit context size
                prompt += f"\n=== CONTEXT FROM FILE ===\n{content}\n"

        if issues:
            prompt += "\n=== IDENTIFIED ISSUES ===\n"
            for issue_type, issue_list in issues.items():
                if issue_list:
                    prompt += f"\n{issue_type.upper()}:\n"
                    for issue in issue_list[:5]:  # Limit issues
                        prompt += f"- {issue}\n"

        # Add current git diff
        exit_code, diff_output, _ = self.run_command(["git", "diff"])
        if exit_code == 0 and diff_output.strip():
            prompt += f"\n=== CURRENT CHANGES ===\n{diff_output[:10000]}\n"

        prompt += """
Please provide specific fixes in this format:
```
FILE: path/to/file.py
LINE: 42
ISSUE: Brief description of the problem
FIX: The corrected code
EXPLANATION: Why this fix is needed
```

Focus on the most critical issues first. Provide concrete, actionable fixes.
"""

        return prompt

    async def get_ai_suggestions(self, prompt: str) -> str | None:
        """Get AI suggestions from Claude"""
        if not self.client:
            print("⚠️  No AI client available")
            return None

        try:
            print("🤖 Getting AI suggestions from Claude...")
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text if response.content else None

        except Exception as e:
            print(f"❌ AI request failed: {str(e)}")
            return None

    def parse_ai_suggestions(self, suggestions: str) -> list[dict]:
        """Parse AI suggestions into actionable fixes"""
        fixes = []

        # Look for code blocks with fixes
        pattern = r"FILE:\s*(.+?)\nLINE:\s*(\d+)\nISSUE:\s*(.+?)\nFIX:\s*(.+?)\nEXPLANATION:\s*(.+?)(?=\n\n|\nFILE:|\Z)"
        matches = re.findall(pattern, suggestions, re.DOTALL | re.IGNORECASE)

        for match in matches:
            file_path, line_num, issue, fix_code, explanation = match
            fixes.append(
                {
                    "file": file_path.strip(),
                    "line": int(line_num.strip()) if line_num.strip().isdigit() else 0,
                    "issue": issue.strip(),
                    "fix": fix_code.strip(),
                    "explanation": explanation.strip(),
                }
            )

        return fixes

    def apply_ai_fixes(self, fixes: list[dict]) -> int:
        """Apply AI-suggested fixes to files"""
        applied_count = 0

        for fix in fixes:
            file_path = Path(fix["file"])
            if not file_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue

            try:
                print(f"🔧 Applying fix to {file_path}:{fix['line']}")
                print(f"   Issue: {fix['issue']}")
                print(f"   Fix: {fix['explanation']}")

                # Read file content
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                # Apply fix if line number is valid
                if 0 < fix["line"] <= len(lines):
                    lines[fix["line"] - 1] = fix["fix"] + "\n"

                    # Write back to file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)

                    applied_count += 1
                    print("   ✅ Applied")
                else:
                    print(f"   ⚠️  Invalid line number: {fix['line']}")

            except Exception as e:
                print(f"   ❌ Failed to apply fix: {str(e)}")

        return applied_count

    async def fix_code(
        self,
        context_file: str | None = None,
        fix_type: str = "all",
        apply_fixes: bool = False,
    ) -> dict:
        """Main method to analyze and fix code issues"""
        result = {
            "automated_fixes": {},
            "ai_suggestions": None,
            "applied_fixes": 0,
            "issues_found": {},
        }

        # Step 1: Apply automated fixes
        print("🚀 Starting automated code fixing...")
        result["automated_fixes"] = self.apply_automated_fixes(fix_type)

        # Step 2: Analyze remaining issues
        print("\n🔍 Analyzing code issues...")
        issues = self.analyze_code_issues()
        result["issues_found"] = {k: len(v) for k, v in issues.items()}

        # Step 3: Get AI suggestions if available and issues exist
        has_issues = any(len(issue_list) > 0 for issue_list in issues.values())
        if self.client and has_issues:
            prompt = self.create_ai_prompt(context_file, issues)
            ai_response = await self.get_ai_suggestions(prompt)

            if ai_response:
                result["ai_suggestions"] = ai_response

                # Step 4: Apply AI fixes if requested
                if apply_fixes:
                    fixes = self.parse_ai_suggestions(ai_response)
                    result["applied_fixes"] = self.apply_ai_fixes(fixes)

                    # Run formatting again after AI fixes
                    print("\n🎨 Final formatting pass...")
                    self.run_command(["ruff", "format", "."])

        return result


def main():
    parser = argparse.ArgumentParser(description="Enhanced AI-powered code fixer")
    parser.add_argument("--context", type=str, help="Context file with additional information")
    parser.add_argument(
        "--fix-type",
        choices=[
            "all",
            "formatting",
            "imports",
            "security",
            "performance",
            "type-hints",
        ],
        default="all",
        help="Type of fixes to apply",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply AI-suggested fixes automatically"
    )
    parser.add_argument("--api-key", type=str, help="Anthropic API key")

    args = parser.parse_args()

    # Initialize fixer
    fixer = CodeFixer(api_key=args.api_key)

    # Run fixes
    try:
        result = asyncio.run(
            fixer.fix_code(
                context_file=args.context,
                fix_type=args.fix_type,
                apply_fixes=args.apply,
            )
        )

        # Print summary
        print("\n" + "=" * 50)
        print("🎯 CODE FIXING SUMMARY")
        print("=" * 50)

        print("\n📊 Automated Fixes:")
        for fix_type, success in result["automated_fixes"].items():
            status = "✅" if success else "❌"
            print(f"  {status} {fix_type}")

        print("\n🔍 Issues Found:")
        for issue_type, count in result["issues_found"].items():
            if count > 0:
                print(f"  • {issue_type}: {count}")

        if result["ai_suggestions"]:
            print("\n🤖 AI Analysis: Available")
            if result["applied_fixes"] > 0:
                print(f"   Applied fixes: {result['applied_fixes']}")
        elif fixer.client is None and any(count > 0 for count in result["issues_found"].values()):
            print("\n⚠️  AI Analysis: Not available (missing API key or library)")
            print("   Consider installing anthropic and setting ANTHROPIC_API_KEY")

        # Exit with appropriate code
        has_remaining_issues = any(count > 0 for count in result["issues_found"].values())
        sys.exit(1 if has_remaining_issues else 0)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
