"""Translation service for Urdu content translation."""

import hashlib
import os
import re
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from db.connection import get_translation_cache, set_translation_cache

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # For Gemini compatibility
# Using /openai/ endpoint which handles model names without prefix
TRANSLATION_MODEL = "gemini-2.5-flash"


def get_openai_client() -> OpenAI:
    """Get OpenAI client (supports Gemini via OPENAI_BASE_URL)."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    if OPENAI_BASE_URL:
        return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return OpenAI(api_key=OPENAI_API_KEY)


def compute_content_hash(content: str) -> str:
    """Compute MD5 hash of content."""
    return hashlib.md5(content.encode()).hexdigest()


def extract_code_blocks(content: str) -> tuple[str, list[tuple[str, str]]]:
    """Extract code blocks and replace with placeholders.

    Returns:
        Tuple of (content with placeholders, list of (placeholder, code))
    """
    code_blocks = []
    placeholder_pattern = "___CODE_BLOCK_{}___"

    def replace_block(match):
        idx = len(code_blocks)
        code_blocks.append((placeholder_pattern.format(idx), match.group(0)))
        return placeholder_pattern.format(idx)

    # Match fenced code blocks (```...```)
    pattern = r"```[\s\S]*?```"
    content_with_placeholders = re.sub(pattern, replace_block, content)

    return content_with_placeholders, code_blocks


def restore_code_blocks(content: str, code_blocks: list[tuple[str, str]]) -> str:
    """Restore code blocks from placeholders."""
    for placeholder, code in code_blocks:
        content = content.replace(placeholder, code)
    return content


# Minimum length for valid translation response (characters)
MIN_TRANSLATION_LENGTH = 50

# Friendly prompt that avoids triggering safety filters
TRANSLATION_SYSTEM_PROMPT = """You are a helpful translator specializing in technical documentation.
Your task is to translate English text into Urdu while maintaining readability for technical learners.

Guidelines:
- Translate prose and explanations into natural Urdu
- Keep technical terms (like API, function names, variables) in English
- Preserve all Markdown formatting (headers, bold, links, lists)
- Keep any placeholders like ___CODE_BLOCK_N___ exactly as they are
- Maintain the same structure and flow as the original

IMPORTANT: If you cannot translate for any reason, return the ORIGINAL ENGLISH TEXT exactly as provided. Never return an empty response or a very short response."""

TRANSLATION_PROMPT = """Please translate the following technical content into Urdu:

{content}

Translated content:"""


async def translate_content(
    content: str,
    source_path: str,
    target_language: str = "ur",
) -> str:
    """Translate content to the target language.

    Args:
        content: The content to translate
        source_path: Path to source file (for caching)
        target_language: Target language code (default: 'ur' for Urdu)

    Returns:
        Translated content with code blocks preserved.
        On error, returns the original content to prevent UI vanishing.
    """
    # Compute content hash for caching
    content_hash = compute_content_hash(content)

    # Check cache first
    try:
        cached = await get_translation_cache(source_path, content_hash, target_language)
        if cached:
            return cached
    except Exception:
        pass  # Continue without cache

    # Extract code blocks
    content_without_code, code_blocks = extract_code_blocks(content)

    try:
        # Translate with OpenAI/Gemini
        client = get_openai_client()

        response = client.chat.completions.create(
            model=TRANSLATION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": TRANSLATION_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": TRANSLATION_PROMPT.format(content=content_without_code),
                },
            ],
            temperature=0.3,
            max_tokens=8192,  # Increased to avoid truncation
        )

        # Safety check for empty response
        if not response.choices or not response.choices[0].message:
            print("DEBUG TRANSLATION: Empty response from API, returning original")
            return content

        translated = response.choices[0].message.content

        # Additional safety check
        if not translated:
            print("DEBUG TRANSLATION: Translated content is None, returning original")
            return content

        # Debug logging to see what we received
        print(f"DEBUG TRANSLATION: received {len(translated) if translated else 0} chars")
        print(f"DEBUG TRANSLATION preview: {translated[:200] if translated else 'None'}...")

        # Length check: treat very short responses as failures
        if not translated or len(translated.strip()) < MIN_TRANSLATION_LENGTH:
            print(f"DEBUG TRANSLATION: Response too short ({len(translated.strip()) if translated else 0} < {MIN_TRANSLATION_LENGTH}), returning original")
            return content

        # Restore code blocks
        final_content = restore_code_blocks(translated, code_blocks)

        # Cache the result (don't fail if caching fails)
        try:
            await set_translation_cache(
                source_path=source_path,
                content_hash=content_hash,
                translated_content=final_content,
                target_language=target_language,
                model_version=TRANSLATION_MODEL,
            )
        except Exception:
            pass  # Caching is optional

        return final_content

    except Exception as e:
        # On any error, return original content to prevent vanishing text
        import logging
        logging.warning(f"Translation failed, returning original content: {e}")
        print(f"DEBUG TRANSLATION ERROR: {e}")
        return content
