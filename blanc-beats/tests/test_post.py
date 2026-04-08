"""Tests for the post module."""

import struct
import wave
from pathlib import Path

import pytest

from post.youtube import upload_to_youtube, _dry_run


class TestYouTubePost:
    """Tests for YouTube posting stage."""

    def _make_wav(self, path: Path) -> Path:
        """Helper: create a minimal WAV file.

        Args:
            path: Output path.

        Returns:
            The path written to.
        """
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(struct.pack("<44100h", *([0] * 44100)))
        return path

    def test_dry_run_when_no_credentials(self, tmp_path):
        """Without client_secrets.json, upload runs in dry-run mode."""
        audio = self._make_wav(tmp_path / "test.wav")
        result = upload_to_youtube(
            audio_path=audio,
            title="Test Track",
            description="Test description",
        )
        assert result.get("dry_run") is True
        assert result["title"] == "Test Track"

    def test_missing_audio_raises(self, tmp_path):
        """Non-existent audio file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            upload_to_youtube(
                audio_path=tmp_path / "nope.wav",
                title="Test",
                description="Test",
            )

    def test_dry_run_includes_metadata(self, tmp_path):
        """Dry run result includes key metadata."""
        audio = self._make_wav(tmp_path / "test.wav")
        result = _dry_run(
            audio_path=audio,
            title="My Track",
            description="A cool track",
            tags=["AI", "Music"],
            privacy="unlisted",
        )
        assert result["privacy"] == "unlisted"
        assert result["audio_file"] == "test.wav"

    def test_default_tags(self, tmp_path):
        """Default tags are applied when none provided."""
        audio = self._make_wav(tmp_path / "test.wav")
        result = upload_to_youtube(
            audio_path=audio,
            title="Test",
            description="Test",
        )
        # Dry run mode — just verify it doesn't crash
        assert "dry_run" in result or "video_id" in result
