"""
Domain Models for Content Protection

Framework-agnostic domain models using standard library dataclasses.
No Pydantic or other framework dependencies.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class WatermarkPosition(str, Enum):
    """Predefined watermark positions"""
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CENTER = "center"


class RiskLevel(str, Enum):
    """Content theft risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class WatermarkConfig:
    """
    Configuration for watermark application.

    Immutable configuration object that defines how watermarks should be applied.
    """
    text: str
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT
    opacity: float = 0.7
    font_size: int = 24
    color: str = "white"
    shadow: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values"""
        if not 0 <= self.opacity <= 1:
            raise ValueError(f"Opacity must be between 0 and 1, got {self.opacity}")
        if self.font_size <= 0:
            raise ValueError(f"Font size must be positive, got {self.font_size}")
        if not self.text.strip():
            raise ValueError("Watermark text cannot be empty")


@dataclass
class WatermarkResult:
    """
    Result of a watermark operation.

    Contains information about the success of the operation, the output file path,
    and any errors that occurred.
    """
    success: bool
    output_path: str | None = None
    error: str | None = None
    processing_time_ms: float = 0.0

    @property
    def is_success(self) -> bool:
        """Convenience property for checking success"""
        return self.success and self.output_path is not None


@dataclass
class TheftAnalysis:
    """
    Result of content theft detection analysis.

    Provides information about suspicious patterns, risk level,
    and recommendations for the content.
    """
    suspicious_patterns: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    recommendations: list[str] = field(default_factory=list)
    link_count: int = 0
    spam_score: float = 0.0

    @property
    def is_suspicious(self) -> bool:
        """Returns True if content has medium or high risk"""
        return self.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH)

    @property
    def has_links(self) -> bool:
        """Returns True if content contains links"""
        return self.link_count > 0


@dataclass
class ContentProtectionRequest:
    """
    Request for content protection operation.

    Specifies what type of content needs protection and the desired configuration.
    """
    content_type: Literal["image", "video", "text"]
    file_path: str | None = None
    text_content: str | None = None
    watermark_config: WatermarkConfig | None = None
    user_id: int | None = None
    check_theft: bool = False

    def __post_init__(self) -> None:
        """Validate request"""
        if self.content_type in ("image", "video") and not self.file_path:
            raise ValueError(f"file_path is required for {self.content_type} content")
        if self.content_type == "text" and not self.text_content:
            raise ValueError("text_content is required for text content")


@dataclass
class ContentProtectionResponse:
    """
    Response from content protection operation.

    Contains results of watermarking, theft analysis, and any errors.
    """
    success: bool
    watermark_result: WatermarkResult | None = None
    theft_analysis: TheftAnalysis | None = None
    error: str | None = None
    total_processing_time_ms: float = 0.0

    @property
    def is_protected(self) -> bool:
        """Returns True if content was successfully protected"""
        if not self.success:
            return False

        # Check watermark result
        if self.watermark_result and self.watermark_result.is_success:
            return True

        # Check theft analysis
        if self.theft_analysis and not self.theft_analysis.is_suspicious:
            return True

        return False
