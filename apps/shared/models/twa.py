"""Pydantic models used by both API and Bot layers.

These models are intentionally minimal and framework-independent.
They provide a shared vocabulary for data exchange between layers
without creating tight coupling.

Originally located in apps.bot.models.twa - moved to apps.shared.models
as part of Phase 1.5 to break API→Bot cross-dependencies.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Button(BaseModel):
    """Telegram inline button model"""

    text: str
    url: str


class AddChannelRequest(BaseModel):
    """Request body for adding a new channel.

    The field is named ``channel_username`` in the model but also accepts
    ``channel_name`` for backwards compatibility with older clients.
    """

    channel_username: str = Field(alias="channel_name")

    # Allow requests to populate ``channel_username`` using the alias.
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("channel_username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:  # noqa: D401 - short note
        """Ensure the username starts with '@'."""
        if not v or not v.startswith("@"):
            raise ValueError("Channel username must start with @")
        return v


class SchedulePostRequest(BaseModel):
    """Request body for scheduling a post."""

    channel_id: int
    scheduled_at: datetime
    text: str | None = None
    media_id: str | None = None
    media_type: str | None = None
    buttons: list[Button] | None = None


class Channel(BaseModel):
    """Representation of a Telegram channel in API responses."""

    id: int
    title: str
    username: str | None = None


class ScheduledPost(BaseModel):
    """Representation of a scheduled post returned from the API."""

    id: int
    channel_id: int
    scheduled_at: datetime
    text: str | None = None
    media_id: str | None = None
    media_type: str | None = None
    buttons: list[Button] | None = None


class User(BaseModel):
    """User model for API/Bot data exchange"""

    id: int
    username: str | None = None


class Plan(BaseModel):
    """Subscription plan model"""

    name: str
    max_channels: int
    max_posts_per_month: int


class InitialDataResponse(BaseModel):
    """Initial data response for frontend initialization"""

    user: User
    plan: Plan | None = None
    channels: list[Channel] = Field(default_factory=list)
    scheduled_posts: list[ScheduledPost] = Field(default_factory=list)
    features: dict[str, bool] = Field(default_factory=dict)


class ValidationErrorResponse(BaseModel):
    """Standard validation error response"""

    detail: str


class MessageResponse(BaseModel):
    """Standard message response"""

    message: str
