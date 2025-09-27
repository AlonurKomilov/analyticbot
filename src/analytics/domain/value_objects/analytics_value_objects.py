"""
Analytics Domain Value Objects
"""

from dataclasses import dataclass

from ....shared_kernel.domain.value_objects import ValueObject


@dataclass(frozen=True)
class ChannelId(ValueObject):
    """Channel ID value object"""

    value: str

    def validate(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Channel ID must be a non-empty string")
        if len(self.value.strip()) == 0:
            raise ValueError("Channel ID cannot be empty or whitespace")

    def __str__(self) -> str:
        return self.value

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class PostId(ValueObject):
    """Post ID value object"""

    value: str

    def validate(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Post ID must be a non-empty string")
        if len(self.value.strip()) == 0:
            raise ValueError("Post ID cannot be empty or whitespace")

    def __str__(self) -> str:
        return self.value

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class MessageId(ValueObject):
    """Telegram Message ID value object"""

    value: int

    def validate(self) -> None:
        if self.value <= 0:
            raise ValueError("Message ID must be positive")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class ViewCount(ValueObject):
    """View count value object with business rules"""

    value: int

    def validate(self) -> None:
        if self.value < 0:
            raise ValueError("View count cannot be negative")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: "ViewCount") -> "ViewCount":
        """Add two view counts"""
        return ViewCount(self.value + other.value)

    def __gt__(self, other: "ViewCount") -> bool:
        """Compare view counts"""
        return self.value > other.value

    def increase_by(self, amount: int) -> "ViewCount":
        """Create new view count increased by amount"""
        if amount < 0:
            raise ValueError("Cannot increase by negative amount")
        return ViewCount(self.value + amount)


@dataclass(frozen=True)
class ChannelTitle(ValueObject):
    """Channel title value object"""

    value: str

    def validate(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Channel title cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Channel title too long (max 255 characters)")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ChannelUsername(ValueObject):
    """Channel username value object"""

    value: str

    def validate(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Channel username cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Channel username too long (max 255 characters)")
        # Channel usernames start with @
        if not self.value.startswith("@"):
            raise ValueError("Channel username must start with @")

    def __str__(self) -> str:
        return self.value

    @property
    def without_at(self) -> str:
        """Get username without @ symbol"""
        return self.value[1:] if self.value.startswith("@") else self.value


@dataclass(frozen=True)
class PostContent(ValueObject):
    """Post content value object"""

    text: str
    media_type: str | None = None
    media_id: str | None = None

    def validate(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("Post content cannot be empty")
        if len(self.text) > 10000:  # Telegram limit
            raise ValueError("Post content too long (max 10000 characters)")

    def __str__(self) -> str:
        return self.text

    @property
    def has_media(self) -> bool:
        """Check if post has media content"""
        return bool(self.media_type and self.media_id)

    @property
    def word_count(self) -> int:
        """Get approximate word count"""
        return len(self.text.split())


@dataclass(frozen=True)
class AnalyticsMetric(ValueObject):
    """Analytics metric value object"""

    name: str
    value: float
    unit: str = ""

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Metric name cannot be empty")
        if not isinstance(self.value, (int, float)):
            raise ValueError("Metric value must be numeric")

    def __str__(self) -> str:
        return f"{self.name}: {self.value} {self.unit}".strip()

    @property
    def formatted_value(self) -> str:
        """Get formatted value with unit"""
        return f"{self.value} {self.unit}".strip()

    @property
    def display_name(self) -> str:
        """Get display-friendly name"""
        return self.name.replace("_", " ").title()

    def as_percentage(self) -> "AnalyticsMetric":
        """Convert to percentage format"""
        return AnalyticsMetric(name=self.name, value=self.value * 100, unit="%")

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "formatted_value": self.formatted_value,
            "display_name": self.display_name,
        }
