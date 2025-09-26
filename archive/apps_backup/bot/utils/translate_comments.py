#!/usr/bin/env python3
"""
Script to translate Uzbek comments to English in code files
"""

import glob
import re

# Translation mapping for common Uzbek to English phrases
TRANSLATIONS = {
    # Common programming terms
    "ma'lumotlarini yuklash": "loading data",
    "ma'lumot yuklash": "load data",
    "Component mount va": "Component mount and",
    "o'zgarganda": "when changes",
    "dependency qo'shildi": "added to dependencies",
    "ham dependency qo'shildi": "also added to dependencies",
    "olib tashlandi": "removed",
    "transformatsiyasi": "transformation",
    "hisoblash": "calculation",
    "olish": "getting",
    "uchun": "for",
    "rangini": "range",
    "formatini o'zgartirish": "format conversion",
    "formatlash": "formatting",
    "yuklash": "loading",
    "ham yuklash": "also load",
    "Haftaning kunlari": "Days of week",
    "Soat formatini": "Hour format",
    "Heat map": "Heat map",
    "rang olish": "get color",
    "tavsiyalarni": "recommendations",
    "ma'lumotlari": "data",
    "Store method'larini olamiz": "Get store methods",
    "Top posts": "Top posts",
    "Best time recommendations'ni": "Load best time recommendations",
    "AI insights'ni": "Load AI insights",
    "AI tavsiyalarni": "Format AI recommendations",
    "Heatmap": "Heatmap",
    "Confidence level": "Confidence level",
    "Performance badge": "Get performance badge",
    "Engagement rate": "Calculate engagement rate",
    "Summary statistics": "Summary statistics",
    "Menu handlers": "Menu handlers",
    "Menu action handlers": "Menu action handlers",
    "Metric formatters": "Metric formatters",
    "filter": "filter",
    "Wait for data to load": "Wait for data to load",
    "label and legend": "label and legend",
    "select and table header": "select and table header",
}


def translate_comment(comment_text):
    """Translate Uzbek comment to English"""
    text = comment_text.strip()

    # Direct translations
    for uzb, eng in TRANSLATIONS.items():
        if uzb in text:
            text = text.replace(uzb, eng)

    return text


def process_file(file_path):
    """Process a single file to translate comments"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Find all single-line comments starting with //
        comment_pattern = r"(\s*//\s*)([^\r\n]*)"

        def replace_comment(match):
            indent = match.group(1)
            comment = match.group(2)
            translated = translate_comment(comment)
            return f"{indent}{translated}"

        content = re.sub(comment_pattern, replace_comment, content)

        # Write back only if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Updated: {file_path}")
            return True
        else:
            print(f"- No changes: {file_path}")
            return False

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False


def main():
    """Main function"""
    print("🌐 Starting translation of comments from Uzbek to English...")

    # File patterns to process
    patterns = [
        "/workspaces/analyticbot/twa-frontend/src/**/*.jsx",
        "/workspaces/analyticbot/twa-frontend/src/**/*.js",
        "/workspaces/analyticbot/**/*.py",
    ]

    total_files = 0
    updated_files = 0

    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            # Skip node_modules, .git, __pycache__ etc
            if any(
                skip in file_path
                for skip in ["node_modules", ".git", "__pycache__", "dist", "build"]
            ):
                continue

            total_files += 1
            if process_file(file_path):
                updated_files += 1

    print("\n📊 Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Files updated: {updated_files}")
    print(f"Files unchanged: {total_files - updated_files}")

    print("\n🎉 Translation completed!")


if __name__ == "__main__":
    main()
