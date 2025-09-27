"""
Payments Domain Value Objects

Type-safe, immutable value objects for the payments domain.
Each value object encapsulates business validation and formatting logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from uuid import uuid4

from src.shared_kernel.domain.value_objects import ValueObject

# ========== ENUMERATIONS ==========


class PaymentProviderType(str, Enum):
    """Payment provider types"""

    STRIPE = "stripe"
    PAYME = "payme"
    CLICK = "click"
    PAYPAL = "paypal"
    MOCK = "mock"


class PaymentStatusType(str, Enum):
    """Payment status types"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentMethodTypeEnum(str, Enum):
    """Payment method types"""

    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    PHONE = "phone"  # For Click/Payme


class SubscriptionStatusType(str, Enum):
    """Subscription status types"""

    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    SUSPENDED = "suspended"


class BillingCycleType(str, Enum):
    """Billing cycle types"""

    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    QUARTERLY = "quarterly"


# ========== MONEY AND AMOUNTS ==========


@dataclass(frozen=True)
class Money(ValueObject):
    """Money value object with currency and amount"""

    amount: Decimal
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")

        # Round to 2 decimal places for currency
        rounded_amount = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", rounded_amount)
        object.__setattr__(self, "currency", self.currency.upper())

    def add(self, other: Money) -> Money:
        """Add two money amounts with same currency"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: Money) -> Money:
        """Subtract money amounts with same currency"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Result cannot be negative")
        return Money(result, self.currency)

    def multiply(self, factor: Decimal | float) -> Money:
        """Multiply money by a factor"""
        if isinstance(factor, float):
            factor = Decimal(str(factor))
        return Money(self.amount * factor, self.currency)

    def is_zero(self) -> bool:
        """Check if amount is zero"""
        return self.amount == Decimal("0")

    def to_cents(self) -> int:
        """Convert to cents for payment processors"""
        return int(self.amount * 100)

    @classmethod
    def from_cents(cls, cents: int, currency: str) -> Money:
        """Create from cents value"""
        return cls(Decimal(cents) / 100, currency)

    def format_display(self) -> str:
        """Format for display purposes"""
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class PaymentAmount(ValueObject):
    """Payment amount with validation"""

    money: Money

    def __post_init__(self):
        if self.money.amount <= 0:
            raise ValueError("Payment amount must be positive")

    @property
    def amount(self) -> Decimal:
        return self.money.amount

    @property
    def currency(self) -> str:
        return self.money.currency

    def to_cents(self) -> int:
        return self.money.to_cents()

    @classmethod
    def from_cents(cls, cents: int, currency: str) -> PaymentAmount:
        return cls(Money.from_cents(cents, currency))


# ========== IDENTIFIERS ==========


@dataclass(frozen=True)
class PaymentId(ValueObject):
    """Payment identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Payment ID cannot be empty")

    @classmethod
    def generate(cls) -> PaymentId:
        """Generate new payment ID"""
        return cls(f"pay_{uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PaymentMethodId(ValueObject):
    """Payment method identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Payment method ID cannot be empty")

    @classmethod
    def generate(cls) -> PaymentMethodId:
        """Generate new payment method ID"""
        return cls(f"pm_{uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SubscriptionId(ValueObject):
    """Subscription identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Subscription ID cannot be empty")

    @classmethod
    def generate(cls) -> SubscriptionId:
        """Generate new subscription ID"""
        return cls(f"sub_{uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PlanId(ValueObject):
    """Subscription plan identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Plan ID cannot be empty")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CustomerId(ValueObject):
    """Customer identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Customer ID cannot be empty")

    @classmethod
    def from_user_id(cls, user_id: int) -> CustomerId:
        """Create customer ID from user ID"""
        return cls(f"cust_{user_id}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TransactionId(ValueObject):
    """Transaction identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Transaction ID cannot be empty")

    @classmethod
    def generate(cls) -> TransactionId:
        """Generate new transaction ID"""
        return cls(f"txn_{uuid4().hex[:16]}")

    def __str__(self) -> str:
        return self.value


# ========== PAYMENT DETAILS ==========


@dataclass(frozen=True)
class PaymentProvider(ValueObject):
    """Payment provider information"""

    provider_type: PaymentProviderType

    def __post_init__(self):
        if not isinstance(self.provider_type, PaymentProviderType):
            raise ValueError(f"Invalid provider type: {self.provider_type}")

    @property
    def name(self) -> str:
        return self.provider_type.value

    def is_stripe(self) -> bool:
        return self.provider_type == PaymentProviderType.STRIPE

    def is_local_uzb(self) -> bool:
        """Check if it's a local Uzbekistan provider"""
        return self.provider_type in [
            PaymentProviderType.PAYME,
            PaymentProviderType.CLICK,
        ]

    def supports_subscriptions(self) -> bool:
        """Check if provider supports subscriptions"""
        return self.provider_type in [
            PaymentProviderType.STRIPE,
            PaymentProviderType.PAYPAL,
        ]


@dataclass(frozen=True)
class PaymentStatus(ValueObject):
    """Payment status with validation"""

    status: PaymentStatusType

    def __post_init__(self):
        if not isinstance(self.status, PaymentStatusType):
            raise ValueError(f"Invalid payment status: {self.status}")

    @property
    def value(self) -> str:
        return self.status.value

    def is_final(self) -> bool:
        """Check if payment is in final state"""
        return self.status in [
            PaymentStatusType.SUCCEEDED,
            PaymentStatusType.FAILED,
            PaymentStatusType.CANCELED,
            PaymentStatusType.REFUNDED,
        ]

    def is_successful(self) -> bool:
        return self.status == PaymentStatusType.SUCCEEDED

    def is_pending(self) -> bool:
        return self.status in [PaymentStatusType.PENDING, PaymentStatusType.PROCESSING]


@dataclass(frozen=True)
class PaymentMethodType(ValueObject):
    """Payment method type"""

    method_type: PaymentMethodTypeEnum

    def __post_init__(self):
        if not isinstance(self.method_type, PaymentMethodTypeEnum):
            raise ValueError(f"Invalid payment method type: {self.method_type}")

    @property
    def value(self) -> str:
        return self.method_type.value

    def is_card(self) -> bool:
        return self.method_type == PaymentMethodTypeEnum.CARD


# ========== SUBSCRIPTION DETAILS ==========


@dataclass(frozen=True)
class SubscriptionStatus(ValueObject):
    """Subscription status with business rules"""

    status: SubscriptionStatusType

    def __post_init__(self):
        if not isinstance(self.status, SubscriptionStatusType):
            raise ValueError(f"Invalid subscription status: {self.status}")

    @property
    def value(self) -> str:
        return self.status.value

    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in [
            SubscriptionStatusType.ACTIVE,
            SubscriptionStatusType.TRIALING,
        ]

    def is_canceled(self) -> bool:
        return self.status == SubscriptionStatusType.CANCELED

    def needs_payment(self) -> bool:
        """Check if subscription needs payment"""
        return self.status in [
            SubscriptionStatusType.PAST_DUE,
            SubscriptionStatusType.UNPAID,
        ]

    def can_be_canceled(self) -> bool:
        """Check if subscription can be canceled"""
        return self.status in [
            SubscriptionStatusType.ACTIVE,
            SubscriptionStatusType.TRIALING,
            SubscriptionStatusType.PAST_DUE,
        ]


@dataclass(frozen=True)
class PaymentMethodStatus(ValueObject):
    """Payment method status enumeration"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"

    def __init__(self, value: str):
        if value not in [self.ACTIVE, self.INACTIVE, self.EXPIRED, self.BLOCKED]:
            raise ValueError(f"Invalid payment method status: {value}")
        self.value = value

    def __str__(self) -> str:
        return self.value


class SubscriptionStatus(ValueObject):
    """Subscription status enumeration"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"

    def __init__(self, value: str):
        if value not in [
            self.ACTIVE,
            self.INACTIVE,
            self.PAUSED,
            self.CANCELED,
            self.EXPIRED,
        ]:
            raise ValueError(f"Invalid subscription status: {value}")
        self.value = value

    def __str__(self) -> str:
        return self.value


class BillingCycle(ValueObject):
    """Billing cycle information"""

    cycle: BillingCycleType

    def __post_init__(self):
        if not isinstance(self.cycle, BillingCycleType):
            raise ValueError(f"Invalid billing cycle: {self.cycle}")

    @property
    def value(self) -> str:
        return self.cycle.value

    def get_period_days(self) -> int:
        """Get number of days in billing cycle"""
        period_map = {
            BillingCycleType.WEEKLY: 7,
            BillingCycleType.MONTHLY: 30,
            BillingCycleType.QUARTERLY: 90,
            BillingCycleType.YEARLY: 365,
        }
        return period_map[self.cycle]

    def is_annual(self) -> bool:
        return self.cycle == BillingCycleType.YEARLY


@dataclass(frozen=True)
class BillingPeriod(ValueObject):
    """Billing period with start and end dates"""

    start_date: datetime
    end_date: datetime

    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")

    def contains_date(self, check_date: datetime) -> bool:
        """Check if date is within billing period"""
        return self.start_date <= check_date <= self.end_date

    def is_current(self) -> bool:
        """Check if this period is current"""
        now = datetime.utcnow()
        return self.contains_date(now)

    def days_remaining(self) -> int:
        """Get days remaining in period"""
        now = datetime.utcnow()
        if now > self.end_date:
            return 0
        return (self.end_date - now).days

    def duration_days(self) -> int:
        """Get total duration of period in days"""
        return (self.end_date - self.start_date).days


# ========== CARD DETAILS ==========


@dataclass(frozen=True)
class ExpiryDate(ValueObject):
    """Card expiry date"""

    month: int
    year: int

    def __post_init__(self):
        if not (1 <= self.month <= 12):
            raise ValueError("Month must be between 1 and 12")

        current_year = datetime.now().year
        if self.year < current_year or self.year > current_year + 20:
            raise ValueError(f"Year must be between {current_year} and {current_year + 20}")

    def is_expired(self) -> bool:
        """Check if card is expired"""
        now = datetime.now()
        return self.year < now.year or (self.year == now.year and self.month < now.month)

    def to_date(self) -> date:
        """Convert to date object (last day of month)"""
        if self.month == 12:
            return date(self.year + 1, 1, 1)
        else:
            return date(self.year, self.month + 1, 1)

    def format_display(self) -> str:
        """Format for display (MM/YY)"""
        return f"{self.month:02d}/{str(self.year)[-2:]}"


@dataclass(frozen=True)
class CardDetails(ValueObject):
    """Card details for payment methods"""

    last_four: str
    brand: str
    expiry: ExpiryDate

    def __post_init__(self):
        if not self.last_four or len(self.last_four) != 4 or not self.last_four.isdigit():
            raise ValueError("Last four must be exactly 4 digits")

        if not self.brand or not self.brand.strip():
            raise ValueError("Card brand cannot be empty")

        object.__setattr__(self, "brand", self.brand.lower())

    def is_expired(self) -> bool:
        return self.expiry.is_expired()

    def masked_display(self) -> str:
        """Display masked card number"""
        return f"**** **** **** {self.last_four}"

    def format_display(self) -> str:
        """Format for display"""
        return f"{self.brand.title()} {self.masked_display()} {self.expiry.format_display()}"


# ========== EXTERNAL PROVIDER REFERENCES ==========


@dataclass(frozen=True)
class ProviderPaymentId(ValueObject):
    """External payment provider's payment ID"""

    provider: PaymentProvider
    provider_id: str

    def __post_init__(self):
        if not self.provider_id or not self.provider_id.strip():
            raise ValueError("Provider payment ID cannot be empty")

    def __str__(self) -> str:
        return f"{self.provider.name}:{self.provider_id}"


@dataclass(frozen=True)
class ProviderCustomerId(ValueObject):
    """External payment provider's customer ID"""

    provider: PaymentProvider
    provider_id: str

    def __post_init__(self):
        if not self.provider_id or not self.provider_id.strip():
            raise ValueError("Provider customer ID cannot be empty")

    def __str__(self) -> str:
        return f"{self.provider.name}:{self.provider_id}"


@dataclass(frozen=True)
class ProviderSubscriptionId(ValueObject):
    """External payment provider's subscription ID"""

    provider: PaymentProvider
    provider_id: str

    def __post_init__(self):
        if not self.provider_id or not self.provider_id.strip():
            raise ValueError("Provider subscription ID cannot be empty")

    def __str__(self) -> str:
        return f"{self.provider.name}:{self.provider_id}"
