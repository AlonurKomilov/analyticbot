"""Pydantic models used by the FastAPI layer.

The original project referenced a number of classes that were removed
from the repository.  To keep the API functional we provide lightweight
Pydantic models that mirror the simple dictionary structures returned by
the repositories.  These models are intentionally minimal and are not
backed by any ORM.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Button(BaseModel):
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
    id: int
    username: str | None = None


class Plan(BaseModel):
    name: str
    max_channels: int
    max_posts_per_month: int


class InitialDataResponse(BaseModel):
    user: User
    plan: Plan | None = None
    channels: list[Channel] = Field(default_factory=list)
    scheduled_posts: list[ScheduledPost] = Field(default_factory=list)


class ValidationErrorResponse(BaseModel):
    detail: str


class MessageResponse(BaseModel):
    message: str
