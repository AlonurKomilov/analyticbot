"""
Content Formatter Service - Text Cleaning and Formatting

Handles all text formatting, cleaning, and transformation operations
for the Natural Language Generation system.

Part of NLG Service Refactoring (Priority #2)
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class ContentFormatter:
    """
    ✨ Content Formatter Service

    Single Responsibility: Format and clean text content

    Responsibilities:
    - Clean and format narratives
    - Handle whitespace and punctuation
    - Format numbers and percentages
    - Structure paragraphs and sections
    """

    def __init__(self):
        logger.info("ContentFormatter initialized")

    def clean_narrative(self, narrative: str) -> str:
        """
        Clean and format narrative text

        Args:
            narrative: Raw narrative text

        Returns:
            Cleaned and formatted narrative
        """
        try:
            if not narrative or not isinstance(narrative, str):
                return ""

            # Remove extra whitespace
            narrative = re.sub(r"\s+", " ", narrative)

            # Remove leading/trailing whitespace
            narrative = narrative.strip()

            # Ensure proper sentence endings
            if narrative and not narrative.endswith((".", "!", "?")):
                narrative += "."

            # Fix spacing around punctuation
            narrative = re.sub(r"\s+([.,!?;:])", r"\1", narrative)
            narrative = re.sub(r"([.,!?;:])\s*", r"\1 ", narrative)

            # Remove duplicate punctuation
            narrative = re.sub(r"([.,!?])\1+", r"\1", narrative)

            # Capitalize first letter
            if narrative:
                narrative = narrative[0].upper() + narrative[1:]

            return narrative.strip()

        except Exception as e:
            logger.error(f"Narrative cleaning failed: {e}")
            return narrative if narrative else ""

    def format_percentage(self, value: float, decimals: int = 1) -> str:
        """
        Format percentage values consistently

        Args:
            value: Percentage value
            decimals: Number of decimal places

        Returns:
            Formatted percentage string
        """
        try:
            return f"{value:.{decimals}f}%"
        except:
            return f"{value}%"

    def format_number(self, value: float, use_thousands_separator: bool = True) -> str:
        """
        Format numbers with proper separators

        Args:
            value: Numeric value
            use_thousands_separator: Whether to use thousands separator

        Returns:
            Formatted number string
        """
        try:
            if use_thousands_separator:
                return f"{value:,.0f}"
            else:
                return f"{value:.0f}"
        except:
            return str(value)

    def format_metric_value(self, value: Any, metric_type: str = "number") -> str:
        """
        Format metric values based on type

        Args:
            value: Metric value
            metric_type: Type of metric (number, percentage, rate, etc.)

        Returns:
            Formatted metric string
        """
        try:
            if metric_type == "percentage":
                return self.format_percentage(float(value))
            elif metric_type == "rate":
                return self.format_percentage(float(value))
            elif metric_type == "number":
                return self.format_number(float(value))
            elif metric_type == "currency":
                return f"${float(value):,.2f}"
            else:
                return str(value)
        except:
            return str(value)

    def format_time_period(self, days: int) -> str:
        """
        Format time period in human-readable format

        Args:
            days: Number of days

        Returns:
            Human-readable time period
        """
        if days == 1:
            return "1 day"
        elif days < 7:
            return f"{days} days"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week" + ("s" if weeks > 1 else "")
        elif days < 365:
            months = days // 30
            return f"{months} month" + ("s" if months > 1 else "")
        else:
            years = days // 365
            return f"{years} year" + ("s" if years > 1 else "")

    def format_change_description(
        self, current: float, previous: float, use_percentage: bool = True
    ) -> str:
        """
        Format change description (increase/decrease)

        Args:
            current: Current value
            previous: Previous value
            use_percentage: Whether to express as percentage

        Returns:
            Change description string
        """
        try:
            if previous == 0:
                return "increased significantly"

            change = ((current - previous) / previous) * 100

            if abs(change) < 1:
                return "remained stable"

            direction = "increased" if change > 0 else "decreased"

            if use_percentage:
                return f"{direction} by {abs(change):.1f}%"
            else:
                return f"{direction} from {previous:.0f} to {current:.0f}"

        except Exception as e:
            logger.error(f"Change description formatting failed: {e}")
            return "changed"

    def format_trend_description(self, direction: str, strength: float) -> str:
        """
        Format trend description with strength adjective

        Args:
            direction: Trend direction (increasing/decreasing/stable)
            strength: Trend strength (0.0 to 1.0)

        Returns:
            Descriptive trend string
        """
        if direction == "stable":
            return "stable"

        # Determine strength adjective
        if strength > 0.8:
            strength_adj = "strong"
        elif strength > 0.6:
            strength_adj = "steady"
        elif strength > 0.4:
            strength_adj = "moderate"
        else:
            strength_adj = "gradual"

        return f"{strength_adj} {direction}"

    def format_severity_label(self, severity: str) -> str:
        """
        Format severity labels consistently

        Args:
            severity: Severity level

        Returns:
            Formatted severity label
        """
        severity_map = {
            "critical": "🔴 Critical",
            "high": "🟠 High",
            "medium": "🟡 Medium",
            "moderate": "🟡 Moderate",
            "low": "🟢 Low",
            "info": "ℹ️ Info",
        }

        return severity_map.get(severity.lower(), severity.title())

    def format_confidence_label(self, confidence: float) -> str:
        """
        Format confidence score as label

        Args:
            confidence: Confidence score (0.0 to 1.0)

        Returns:
            Confidence label
        """
        if confidence >= 0.9:
            return "very high confidence"
        elif confidence >= 0.7:
            return "high confidence"
        elif confidence >= 0.5:
            return "moderate confidence"
        elif confidence >= 0.3:
            return "low confidence"
        else:
            return "very low confidence"

    def combine_sentences(self, sentences: list[str]) -> str:
        """
        Combine multiple sentences into a coherent paragraph

        Args:
            sentences: List of sentence strings

        Returns:
            Combined paragraph
        """
        if not sentences:
            return ""

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s and s.strip()]

        if not sentences:
            return ""

        # Combine sentences
        paragraph = " ".join(sentences)

        # Clean the result
        return self.clean_narrative(paragraph)

    def truncate_text(self, text: str, max_length: int = 200, suffix: str = "...") -> str:
        """
        Truncate text to maximum length

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text

        # Truncate at word boundary
        truncated = text[:max_length].rsplit(" ", 1)[0]
        return truncated + suffix

    def format_list_items(self, items: list[str], style: str = "bullet") -> str:
        """
        Format list items with proper styling

        Args:
            items: List of item strings
            style: List style (bullet, numbered, dash)

        Returns:
            Formatted list string
        """
        if not items:
            return ""

        formatted_items = []

        for i, item in enumerate(items, 1):
            if style == "numbered":
                formatted_items.append(f"{i}. {item}")
            elif style == "dash":
                formatted_items.append(f"- {item}")
            else:  # bullet
                formatted_items.append(f"• {item}")

        return "\n".join(formatted_items)

    def format_key_value_pairs(self, data: dict[str, Any]) -> str:
        """
        Format key-value pairs for display

        Args:
            data: Dictionary of key-value pairs

        Returns:
            Formatted string
        """
        if not data:
            return ""

        pairs = []
        for key, value in data.items():
            # Format key (convert snake_case to Title Case)
            formatted_key = key.replace("_", " ").title()
            pairs.append(f"{formatted_key}: {value}")

        return ", ".join(pairs)

    def wrap_text(self, text: str, width: int = 80, indent: str = "") -> str:
        """
        Wrap text to specified width

        Args:
            text: Text to wrap
            width: Maximum line width
            indent: Indentation string

        Returns:
            Wrapped text
        """
        if not text:
            return ""

        words = text.split()
        lines = []
        current_line = indent

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                if current_line == indent:
                    current_line += word
                else:
                    current_line += " " + word
            else:
                lines.append(current_line)
                current_line = indent + word

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    async def health_check(self) -> dict[str, Any]:
        """Health check for content formatter"""
        return {
            "service": "ContentFormatter",
            "status": "healthy",
            "capabilities": [
                "narrative_cleaning",
                "number_formatting",
                "percentage_formatting",
                "text_truncation",
                "list_formatting",
                "text_wrapping",
            ],
        }
