"""
Content Theft Detection Service

Pure business logic for detecting suspicious content patterns.
No external dependencies - only standard library.
"""

import re

from core.services.bot.content.models import RiskLevel, TheftAnalysis


class TheftDetectorService:
    """
    Service for detecting potential content theft and spam.

    Uses pattern matching and heuristics to identify suspicious content.
    Framework-agnostic with no external dependencies.
    """

    # Suspicious patterns that might indicate stolen/spam content
    SUSPICIOUS_PATTERNS = [
        r"@\w+",  # Telegram mentions
        r"t\.me/",  # Telegram links
        r"telegram\.me/",  # Alternative Telegram links
        r"click here",  # Typical spam phrase
        r"free money",  # Scam indicator
        r"earn [\$€£]\d+",  # Money promises
        r"limited offer",  # Urgency scam
        r"act now",  # Urgency scam
        r"100% guaranteed",  # False promise
        r"risk.free",  # False assurance
    ]

    # High-risk patterns (immediate red flags)
    HIGH_RISK_PATTERNS = [
        r"bitcoin.*wallet",
        r"send.*money",
        r"bank.*account",
        r"credit.*card",
        r"password",
        r"phishing",
    ]

    def __init__(self) -> None:
        """Initialize the theft detector service."""
        # Compile patterns once for better performance
        self._suspicious_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SUSPICIOUS_PATTERNS
        ]
        self._high_risk_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.HIGH_RISK_PATTERNS
        ]

    async def analyze_content(self, text: str) -> TheftAnalysis:
        """
        Analyze text content for suspicious patterns.

        Args:
            text: Text content to analyze

        Returns:
            TheftAnalysis with detected patterns and risk level
        """
        if not text or not text.strip():
            return TheftAnalysis(
                suspicious_patterns=[],
                risk_level=RiskLevel.LOW,
                recommendations=["Content is empty"],
                link_count=0,
                spam_score=0.0,
            )

        # Detect suspicious patterns
        suspicious_matches: list[str] = []
        for pattern in self._suspicious_patterns:
            matches = pattern.findall(text)
            if matches:
                suspicious_matches.extend(matches)

        # Detect high-risk patterns
        high_risk_matches: list[str] = []
        for pattern in self._high_risk_patterns:
            matches = pattern.findall(text)
            if matches:
                high_risk_matches.extend(matches)

        # Count links
        link_count = self._count_links(text)

        # Calculate spam score
        spam_score = self._calculate_spam_score(
            text=text,
            suspicious_count=len(suspicious_matches),
            high_risk_count=len(high_risk_matches),
            link_count=link_count,
        )

        # Determine risk level
        risk_level = self._determine_risk_level(
            high_risk_count=len(high_risk_matches),
            spam_score=spam_score,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level=risk_level,
            suspicious_matches=suspicious_matches,
            high_risk_matches=high_risk_matches,
            link_count=link_count,
        )

        return TheftAnalysis(
            suspicious_patterns=suspicious_matches + high_risk_matches,
            risk_level=risk_level,
            recommendations=recommendations,
            link_count=link_count,
            spam_score=spam_score,
        )

    def _count_links(self, text: str) -> int:
        """Count HTTP/HTTPS links in text."""
        link_pattern = re.compile(r"https?://\S+", re.IGNORECASE)
        return len(link_pattern.findall(text))

    def _calculate_spam_score(
        self,
        text: str,
        suspicious_count: int,
        high_risk_count: int,
        link_count: int,
    ) -> float:
        """
        Calculate spam score from 0.0 (clean) to 1.0 (definite spam).

        Args:
            text: The text content
            suspicious_count: Number of suspicious pattern matches
            high_risk_count: Number of high-risk pattern matches
            link_count: Number of links found

        Returns:
            Spam score between 0.0 and 1.0
        """
        text_length = len(text)

        # Base score from pattern matches
        score = 0.0

        # High-risk patterns are very significant
        score += high_risk_count * 0.3

        # Suspicious patterns add to score
        score += suspicious_count * 0.1

        # Many links relative to text length is suspicious
        if text_length > 0:
            link_density = link_count / (text_length / 100)  # Links per 100 chars
            score += min(link_density * 0.2, 0.5)

        # Too many links is spam
        if link_count > 5:
            score += 0.2

        # Cap at 1.0
        return min(score, 1.0)

    def _determine_risk_level(
        self,
        high_risk_count: int,
        spam_score: float,
    ) -> RiskLevel:
        """
        Determine risk level based on analysis.

        Args:
            high_risk_count: Number of high-risk patterns found
            spam_score: Calculated spam score

        Returns:
            Risk level (LOW, MEDIUM, or HIGH)
        """
        # Any high-risk pattern is immediate high risk
        if high_risk_count > 0:
            return RiskLevel.HIGH

        # Spam score thresholds
        if spam_score >= 0.6:
            return RiskLevel.HIGH
        elif spam_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        suspicious_matches: list[str],
        high_risk_matches: list[str],
        link_count: int,
    ) -> list[str]:
        """
        Generate recommendations based on analysis.

        Args:
            risk_level: Determined risk level
            suspicious_matches: List of suspicious pattern matches
            high_risk_matches: List of high-risk pattern matches
            link_count: Number of links found

        Returns:
            List of recommendation strings
        """
        recommendations: list[str] = []

        if risk_level == RiskLevel.LOW:
            recommendations.append("Content appears safe")
            return recommendations

        # High-risk recommendations
        if high_risk_matches:
            recommendations.append(
                f"⚠️ HIGH RISK: Found {len(high_risk_matches)} high-risk patterns"
            )
            recommendations.append("Consider blocking or reporting this content")

        # Suspicious pattern recommendations
        if suspicious_matches and not high_risk_matches:
            recommendations.append(
                f"Found {len(suspicious_matches)} suspicious patterns"
            )
            recommendations.append("Review content carefully before sharing")

        # Link recommendations
        if link_count > 5:
            recommendations.append(
                f"High link density ({link_count} links) - potential spam"
            )
        elif link_count > 0 and risk_level == RiskLevel.MEDIUM:
            recommendations.append("Verify links before clicking")

        # General recommendations
        if risk_level == RiskLevel.HIGH:
            recommendations.append("Do not share personal information")
            recommendations.append("Report to moderators if necessary")
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("Add watermark to protect from theft")
            recommendations.append("Monitor for unauthorized sharing")

        return recommendations
