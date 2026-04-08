"""Tests for the pipeline orchestrator."""

import json
from pathlib import Path

import pytest

import pipeline


class TestPipeline:
    """Integration tests for the full pipeline."""

    def test_full_pipeline_stub(self, tmp_path, monkeypatch):
        """Full pipeline runs end-to-end with stub backends and skip_post."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)
        monkeypatch.setattr("config.ANTHROPIC_API_KEY", "")

        result = pipeline.run(
            prompt="ambient test track",
            run_id="test_run_001",
            skip_post=True,
            music_model="stub",
            image_model="stub",
        )

        assert result["run_id"] == "test_run_001"
        assert "error" not in result
        assert result["stages"]["generate"]["status"] == "ok"
        assert result["stages"]["rank"]["status"] == "ok"
        assert result["stages"]["content"]["status"] == "ok"
        assert result["stages"]["post"]["status"] == "skipped"

    def test_manifest_written(self, tmp_path, monkeypatch):
        """Pipeline writes a manifest.json in the run directory."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)
        monkeypatch.setattr("config.ANTHROPIC_API_KEY", "")

        pipeline.run(
            prompt="test",
            run_id="test_manifest",
            skip_post=True,
            music_model="stub",
            image_model="stub",
        )

        manifest = tmp_path / "test_manifest" / "manifest.json"
        assert manifest.exists()
        data = json.loads(manifest.read_text())
        assert data["run_id"] == "test_manifest"

    def test_run_creates_output_structure(self, tmp_path, monkeypatch):
        """Pipeline creates the expected directory structure."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)
        monkeypatch.setattr("config.ANTHROPIC_API_KEY", "")

        pipeline.run(
            prompt="structure test",
            run_id="test_dirs",
            skip_post=True,
            music_model="stub",
            image_model="stub",
        )

        run_dir = tmp_path / "test_dirs"
        assert (run_dir / "generate").is_dir()
        assert (run_dir / "rank").is_dir()
        assert (run_dir / "content").is_dir()
        assert (run_dir / "content" / "description.txt").exists()
        assert (run_dir / "content" / "cover.png").exists()

    def test_make_run_id_format(self):
        """Run IDs follow the expected timestamp_uuid format."""
        rid = pipeline._make_run_id()
        parts = rid.split("_")
        assert len(parts) == 3  # date, time, uuid
        assert len(parts[0]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # short uuid

    def test_make_title_truncation(self):
        """Long prompts get truncated in the title."""
        long_prompt = "x" * 200
        title = pipeline._make_title(long_prompt, max_len=50)
        assert len(title) <= 50
        assert title.endswith("...")

    def test_make_title_short(self):
        """Short prompts aren't truncated."""
        title = pipeline._make_title("chill beat")
        assert title == "Blanc Beats — chill beat"

    def test_pipeline_with_post_dry_run(self, tmp_path, monkeypatch):
        """Pipeline with posting enabled falls through to dry-run."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)
        monkeypatch.setattr("config.ANTHROPIC_API_KEY", "")

        result = pipeline.run(
            prompt="post test",
            run_id="test_post",
            skip_post=False,
            music_model="stub",
            image_model="stub",
        )

        # Should succeed via dry-run (no credentials)
        assert result["stages"]["post"]["status"] == "ok"
        assert result["stages"]["post"].get("dry_run") is True
