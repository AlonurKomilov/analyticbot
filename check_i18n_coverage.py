#!/usr/bin/env python3
"""
Check i18n translation coverage across languages
"""

import json
from pathlib import Path


def get_all_keys(data: dict, prefix: str = "") -> set[str]:
    """Recursively get all keys from nested dictionary"""
    keys = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
        else:
            keys.add(full_key)
    return keys


def load_translation_file(filepath: Path) -> dict:
    """Load a JSON translation file"""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}


def analyze_coverage():
    """Analyze translation coverage across languages"""
    base_path = Path("/home/abcdev/projects/analyticbot/apps/frontend/apps/user/src/i18n/locales")
    languages = ["en", "ru", "uz"]

    # Get all translation files
    translation_files = [
        "analytics.json",
        "auth.json",
        "channels.json",
        "common.json",
        "dashboard.json",
        "errors.json",
        "navigation.json",
        "posts.json",
        "settings.json",
    ]

    print("=" * 80)
    print("I18N TRANSLATION COVERAGE REPORT")
    print("=" * 80)
    print(f"\nLanguages: {', '.join(languages)}")
    print(f"Translation files: {len(translation_files)}")
    print()

    total_issues = 0
    file_coverage = {}

    for file_name in translation_files:
        print(f"\n{'─' * 80}")
        print(f"📄 {file_name}")
        print("─" * 80)

        # Load translations for all languages
        translations = {}
        for lang in languages:
            file_path = base_path / lang / file_name
            translations[lang] = load_translation_file(file_path)

        # Get all keys for each language
        keys_by_lang = {lang: get_all_keys(translations[lang]) for lang in languages}

        # Calculate coverage
        all_keys = set()
        for keys in keys_by_lang.values():
            all_keys.update(keys)

        total_keys = len(all_keys)
        file_coverage[file_name] = {"total_keys": total_keys, "by_language": {}}

        if total_keys == 0:
            print("⚠️  No translations found")
            continue

        print(f"\nTotal unique keys: {total_keys}")
        print()

        # Check each language
        has_issues = False
        for lang in languages:
            lang_keys = keys_by_lang[lang]
            missing_keys = all_keys - lang_keys
            extra_keys = lang_keys - all_keys
            coverage_percent = (len(lang_keys) / total_keys * 100) if total_keys > 0 else 0

            file_coverage[file_name]["by_language"][lang] = {
                "count": len(lang_keys),
                "coverage": coverage_percent,
                "missing": len(missing_keys),
                "extra": len(extra_keys),
            }

            status = "✅" if len(missing_keys) == 0 else "❌"
            print(
                f"{status} {lang.upper()}: {len(lang_keys)}/{total_keys} keys ({coverage_percent:.1f}%)"
            )

            if missing_keys:
                has_issues = True
                total_issues += len(missing_keys)
                print(f"   Missing {len(missing_keys)} keys:")
                for key in sorted(missing_keys)[:10]:  # Show first 10
                    print(f"     - {key}")
                if len(missing_keys) > 10:
                    print(f"     ... and {len(missing_keys) - 10} more")

            if extra_keys:
                print(f"   ⚠️  Has {len(extra_keys)} extra keys not in other languages")

        if not has_issues:
            print("\n✅ All languages have complete coverage for this file!")

    # Summary
    print(f"\n\n{'=' * 80}")
    print("📊 SUMMARY")
    print("=" * 80)

    for lang in languages:
        total_keys_count = sum(file_coverage[f]["total_keys"] for f in translation_files)
        lang_keys_count = sum(
            file_coverage[f]["by_language"][lang]["count"] for f in translation_files
        )
        missing_count = sum(
            file_coverage[f]["by_language"][lang]["missing"] for f in translation_files
        )

        coverage = (lang_keys_count / total_keys_count * 100) if total_keys_count > 0 else 0
        status = "✅" if missing_count == 0 else "❌"

        print(f"\n{status} {lang.upper()}:")
        print(f"   Coverage: {coverage:.1f}% ({lang_keys_count}/{total_keys_count} keys)")
        if missing_count > 0:
            print(f"   Missing: {missing_count} translations")

    print(f"\n{'=' * 80}")
    if total_issues == 0:
        print("🎉 Perfect! All languages have 100% translation coverage!")
    else:
        print(f"⚠️  Found {total_issues} missing translations across all files")
    print("=" * 80)


if __name__ == "__main__":
    analyze_coverage()
