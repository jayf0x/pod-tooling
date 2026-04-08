"""Tests for the content module."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from content.describe import generate_description, _placeholder_description
from content.cover import generate_cover


class TestDescribe:
    """Tests for description generation."""

    def test_placeholder_when_no_api_key(self):
        """Returns placeholder description when ANTHROPIC_API_KEY is empty."""
        with patch("content.describe.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = ""
            mock_config.DESCRIPTION_MODEL = "claude-sonnet-4-20250514"
            result = generate_description("chill lo-fi beat")
            assert "chill lo-fi beat" in result
            assert "#" in result  # has hashtags

    def test_placeholder_format(self):
        """Placeholder includes the prompt and hashtags."""
        result = _placeholder_description("ambient techno")
        assert "ambient techno" in result
        assert "BlancBeats" in result

    def test_api_call_with_key(self):
        """When API key is set, calls the Anthropic client."""
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="A dreamy AI track #AIMusic")]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch("content.describe.config") as mock_config, \
             patch("content.describe.anthropic") as mock_anthropic:
            mock_config.ANTHROPIC_API_KEY = "sk-test-key"
            mock_config.DESCRIPTION_MODEL = "claude-sonnet-4-20250514"
            mock_anthropic.Anthropic.return_value = mock_client

            result = generate_description("dreamy ambient")
            assert result == "A dreamy AI track #AIMusic"
            mock_client.messages.create.assert_called_once()

    def test_metadata_included_in_prompt(self):
        """Metadata dict is passed into the user message."""
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="description")]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch("content.describe.config") as mock_config, \
             patch("content.describe.anthropic") as mock_anthropic:
            mock_config.ANTHROPIC_API_KEY = "sk-test-key"
            mock_config.DESCRIPTION_MODEL = "claude-sonnet-4-20250514"
            mock_anthropic.Anthropic.return_value = mock_client

            generate_description("test", metadata={"genre": "lo-fi"})
            call_args = mock_client.messages.create.call_args
            user_content = call_args.kwargs["messages"][0]["content"]
            assert "lo-fi" in user_content


class TestCover:
    """Tests for cover image generation."""

    def test_stub_creates_png(self, tmp_path):
        """Stub backend produces a valid PNG file."""
        result = generate_cover("test cover", run_dir=tmp_path, model="stub")
        assert result.exists()
        assert result.suffix == ".png"
        # Check PNG magic bytes
        data = result.read_bytes()
        assert data[:4] == b"\x89PNG"

    def test_cover_in_content_dir(self, tmp_path):
        """Cover is written to run_dir/content/."""
        result = generate_cover("test", run_dir=tmp_path, model="stub")
        assert "content" in str(result.parent)

    def test_unknown_image_model_raises(self, tmp_path):
        """Unknown model raises ValueError."""
        with pytest.raises(ValueError, match="Unknown image model"):
            generate_cover("test", run_dir=tmp_path, model="nonexistent")

    def test_flux_falls_back_to_stub(self, tmp_path):
        """Flux backend falls back to stub when binary not found."""
        result = generate_cover("test", run_dir=tmp_path, model="flux")
        assert result.exists()
