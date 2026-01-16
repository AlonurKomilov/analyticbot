"""
Marketplace Domain Value Objects
================================

Value objects for the marketplace domain.
These are immutable objects defined by their attributes rather than identity.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Credits:
    """
    Value object representing credits (marketplace currency).
    """

    amount: int

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Credits cannot be negative")

    def __add__(self, other: "Credits") -> "Credits":
        return Credits(self.amount + other.amount)

    def __sub__(self, other: "Credits") -> "Credits":
        return Credits(self.amount - other.amount)

    def __mul__(self, multiplier: int) -> "Credits":
        return Credits(self.amount * multiplier)

    def __ge__(self, other: "Credits") -> bool:
        return self.amount >= other.amount

    def __le__(self, other: "Credits") -> bool:
        return self.amount <= other.amount

    def __gt__(self, other: "Credits") -> bool:
        return self.amount > other.amount

    def __lt__(self, other: "Credits") -> bool:
        return self.amount < other.amount

    @classmethod
    def zero(cls) -> "Credits":
        return cls(0)

    def to_display_string(self) -> str:
        """Format credits for display"""
        if self.amount >= 1000:
            return f"{self.amount / 1000:.1f}K"
        return str(self.amount)


@dataclass(frozen=True)
class Price:
    """
    Value object representing a price with optional discount.
    """

    current: Credits
    original: Credits | None = None

    @property
    def has_discount(self) -> bool:
        return self.original is not None and self.original > self.current

    @property
    def discount_percentage(self) -> int:
        if not self.has_discount or not self.original:
            return 0
        return int((1 - self.current.amount / self.original.amount) * 100)

    @property
    def savings(self) -> Credits:
        if not self.has_discount or not self.original:
            return Credits.zero()
        return self.original - self.current


@dataclass(frozen=True)
class ServiceKey:
    """
    Value object representing a marketplace service key.
    Service keys follow the pattern: {category}_{feature_name}
    """

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Service key cannot be empty")
        if "_" not in self.value:
            raise ValueError("Service key must contain underscore separator")

    @property
    def category(self) -> str:
        """Extract category from service key (e.g., 'bot' from 'bot_anti_spam')"""
        return self.value.split("_")[0]

    @property
    def feature(self) -> str:
        """Extract feature name from service key (e.g., 'anti_spam' from 'bot_anti_spam')"""
        return "_".join(self.value.split("_")[1:])

    def is_bot_service(self) -> bool:
        return self.category == "bot"

    def is_mtproto_service(self) -> bool:
        return self.category == "mtproto"

    def is_ai_service(self) -> bool:
        return self.category == "ai"


@dataclass(frozen=True)
class Rating:
    """
    Value object representing a rating (1-5 stars).
    """

    value: float
    count: int = 0

    def __post_init__(self):
        if not (0 <= self.value <= 5):
            raise ValueError("Rating must be between 0 and 5")
        if self.count < 0:
            raise ValueError("Rating count cannot be negative")

    @property
    def display_value(self) -> str:
        """Format rating for display"""
        return f"{self.value:.1f}"

    @property
    def stars_full(self) -> int:
        """Number of full stars"""
        return int(self.value)

    @property
    def has_half_star(self) -> bool:
        """Check if there's a half star"""
        return (self.value - self.stars_full) >= 0.5

    def with_new_rating(self, new_rating: int) -> "Rating":
        """Calculate new average with additional rating"""
        if not (1 <= new_rating <= 5):
            raise ValueError("New rating must be between 1 and 5")

        new_count = self.count + 1
        new_value = ((self.value * self.count) + new_rating) / new_count
        return Rating(value=round(new_value, 2), count=new_count)


@dataclass(frozen=True)
class UsageQuota:
    """
    Value object representing usage quota limits.
    """

    daily: int | None = None
    monthly: int | None = None

    def has_daily_limit(self) -> bool:
        return self.daily is not None

    def has_monthly_limit(self) -> bool:
        return self.monthly is not None

    def check_daily(self, current_usage: int) -> bool:
        """Check if daily usage is within limit"""
        if not self.daily:
            return True
        return current_usage < self.daily

    def check_monthly(self, current_usage: int) -> bool:
        """Check if monthly usage is within limit"""
        if not self.monthly:
            return True
        return current_usage < self.monthly

    def daily_remaining(self, current_usage: int) -> int | None:
        """Get remaining daily usage"""
        if not self.daily:
            return None
        return max(0, self.daily - current_usage)

    def monthly_remaining(self, current_usage: int) -> int | None:
        """Get remaining monthly usage"""
        if not self.monthly:
            return None
        return max(0, self.monthly - current_usage)


@dataclass(frozen=True)
class FeatureList:
    """
    Value object representing a list of features for an item/service.
    """

    items: tuple[str, ...]  # Immutable tuple

    def __init__(self, items: list[str]):
        object.__setattr__(self, "items", tuple(items))

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __contains__(self, item: str) -> bool:
        return item in self.items

    def to_list(self) -> list[str]:
        return list(self.items)
