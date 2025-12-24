"""Pydantic models for user data."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PreferredLanguage(str, Enum):
    """Supported languages for the platform."""
    ENGLISH = "en"
    URDU = "ur"


class UserProfile(BaseModel):
    """User profile for personalization."""

    user_id: str = Field(..., description="User UUID from auth system")
    software_background: Optional[str] = Field(
        None,
        max_length=2500,
        description="User's software development experience and skills"
    )
    hardware_background: Optional[str] = Field(
        None,
        max_length=2500,
        description="User's hardware/robotics experience and skills"
    )
    background_summary: Optional[str] = Field(
        None,
        description="AI-generated summary of user's background"
    )
    preferred_language: PreferredLanguage = Field(
        default=PreferredLanguage.ENGLISH,
        description="User's preferred content language"
    )
    personalization_enabled: bool = Field(
        default=True,
        description="Whether to enable content personalization"
    )
    onboarding_completed: bool = Field(
        default=False,
        description="Whether user has completed onboarding"
    )

    class Config:
        use_enum_values = True


class UserProfileResponse(BaseModel):
    """Response model for user profile endpoints."""

    user_id: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    background_summary: Optional[str] = None
    preferred_language: str = "en"
    personalization_enabled: bool = True
    onboarding_completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserContext(BaseModel):
    """User context for RAG personalization."""

    user_id: Optional[str] = None
    is_authenticated: bool = False
    profile: Optional[UserProfile] = None

    @property
    def has_profile(self) -> bool:
        """Check if user has completed their profile."""
        return (
            self.profile is not None
            and self.profile.onboarding_completed
        )

    @property
    def background_text(self) -> str:
        """Get combined background text for personalization."""
        if not self.profile:
            return ""

        parts = []
        if self.profile.software_background:
            parts.append(f"Software: {self.profile.software_background}")
        if self.profile.hardware_background:
            parts.append(f"Hardware: {self.profile.hardware_background}")

        return "\n".join(parts)
