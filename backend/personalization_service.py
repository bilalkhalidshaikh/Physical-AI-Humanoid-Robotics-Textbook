"""Personalization service for user-specific content adaptation."""

import hashlib
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from db.connection import (
    fetch_user_profile,
    get_personalization_cache,
    set_personalization_cache,
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # For Gemini compatibility
# Using /openai/ endpoint which handles model names without prefix
PERSONALIZATION_MODEL = "gemini-2.5-flash"

# Minimum length for valid personalization response (characters)
MIN_PERSONALIZATION_LENGTH = 50


def get_openai_client() -> OpenAI:
    """Get OpenAI client (supports Gemini via OPENAI_BASE_URL)."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    if OPENAI_BASE_URL:
        return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return OpenAI(api_key=OPENAI_API_KEY)


def compute_hash(text: str) -> str:
    """Compute MD5 hash of text."""
    return hashlib.md5(text.encode()).hexdigest()


PERSONALIZATION_PROMPT = """You are an expert robotics educator personalizing content for individual learners.

The student has the following background:
---
{background}
---

Adapt the following technical content to be more relevant and understandable for this student:

1. If they have software experience, connect robotics concepts to familiar programming patterns
2. If they have hardware experience, relate to physical systems they may know
3. Adjust complexity based on their experience level
4. Add relevant analogies based on their background
5. Maintain all technical accuracy
6. Keep the same structure and formatting
7. Preserve all code examples unchanged
8. Add helpful context where their background might create confusion

Original content:
---
{content}
---

Provide the personalized content, maintaining the original markdown formatting."""


async def personalize_content(
    content: str,
    source_path: str,
    user_id: str,
) -> str:
    """Personalize content based on user's background.

    Args:
        content: The content to personalize
        source_path: Path to source file (for caching)
        user_id: User ID for profile lookup

    Returns:
        Personalized content.
        On error, returns the original content to prevent UI vanishing.
    """
    try:
        # Fetch user profile
        profile = await fetch_user_profile(user_id)

        if not profile:
            # No profile, return original content
            return content

        if not profile.get("onboarding_completed"):
            # Profile not complete, return original
            return content

        if not profile.get("personalization_enabled", True):
            # Personalization disabled, return original
            return content

        # Build background text
        background_parts = []
        if profile.get("software_background"):
            background_parts.append(f"Software experience: {profile['software_background']}")
        if profile.get("hardware_background"):
            background_parts.append(f"Hardware experience: {profile['hardware_background']}")

        if not background_parts:
            # No background info, return original
            return content

        background_text = "\n".join(background_parts)

        # Compute hashes for caching
        content_hash = compute_hash(content)
        profile_hash = compute_hash(background_text)

        # Check cache
        try:
            cached = await get_personalization_cache(
                user_id=user_id,
                source_path=source_path,
                content_hash=content_hash,
                profile_hash=profile_hash,
            )
            if cached:
                return cached
        except Exception:
            pass  # Continue without cache

        # Generate personalized content
        client = get_openai_client()

        response = client.chat.completions.create(
            model=PERSONALIZATION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert robotics educator who personalizes technical content based on student backgrounds.",
                },
                {
                    "role": "user",
                    "content": PERSONALIZATION_PROMPT.format(
                        background=background_text,
                        content=content,
                    ),
                },
            ],
            temperature=0.5,
            max_tokens=4000,
        )

        personalized = response.choices[0].message.content

        # Debug logging to see what we received
        print(f"DEBUG PERSONALIZATION: received {len(personalized) if personalized else 0} chars")
        print(f"DEBUG PERSONALIZATION preview: {personalized[:200] if personalized else 'None'}...")

        # Length check: treat very short responses as failures
        if not personalized or len(personalized.strip()) < MIN_PERSONALIZATION_LENGTH:
            print(f"DEBUG PERSONALIZATION: Response too short ({len(personalized.strip()) if personalized else 0} < {MIN_PERSONALIZATION_LENGTH}), returning original")
            return content

        # Cache the result (don't fail if caching fails)
        try:
            await set_personalization_cache(
                user_id=user_id,
                source_path=source_path,
                content_hash=content_hash,
                profile_hash=profile_hash,
                personalized_content=personalized,
                model_version=PERSONALIZATION_MODEL,
            )
        except Exception:
            pass  # Caching is optional

        return personalized

    except Exception as e:
        # On any error, return original content to prevent vanishing text
        import logging
        logging.warning(f"Personalization failed, returning original content: {e}")
        print(f"DEBUG PERSONALIZATION ERROR: {e}")
        return content
