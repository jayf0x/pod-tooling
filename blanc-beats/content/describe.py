from __future__ import annotations

"""
Description generation stage.

Uses the Claude API to produce a post-ready description
for a music track based on its generation prompt and metadata.
"""

import logging
from pathlib import Path

import anthropic

import config

logger = logging.getLogger(__name__)

# REASON: System prompt kept separate so it's easy to iterate on tone/style
# without touching code logic.
_SYSTEM_PROMPT = (
    "You are a music curator writing short, engaging social-media descriptions "
    "for AI-generated music tracks. Keep it under 280 characters for X compatibility. "
    "Include relevant hashtags. Be authentic — don't oversell."
)


def generate_description(
    prompt: str,
    metadata: dict | None = None,
    model: str | None = None,
) -> str:
    """Generate a social-media description for a music track.

    Args:
        prompt: The original music generation prompt.
        metadata: Optional dict with extra context (genre, mood, etc.).
        model: Claude model to use (default: config.DESCRIPTION_MODEL).

    Returns:
        Generated description string.

    Raises:
        anthropic.APIError: If the API call fails.
    """
    model = model or config.DESCRIPTION_MODEL

    if not config.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — returning placeholder description.")
        return _placeholder_description(prompt)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    user_msg = f"Write a description for this AI-generated track.\n\nPrompt: {prompt}"
    if metadata:
        user_msg += f"\nMetadata: {metadata}"

    logger.info("Requesting description from %s", model)

    message = client.messages.create(
        model=model,
        max_tokens=300,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    description = message.content[0].text.strip()
    logger.info("Generated description (%d chars)", len(description))
    return description


def _placeholder_description(prompt: str) -> str:
    """Return a basic placeholder when the API key is missing.

    Args:
        prompt: The music generation prompt.

    Returns:
        A simple placeholder description string.
    """
    return f"🎵 New AI-generated track: {prompt} #AIMusic #BlancBeats"
