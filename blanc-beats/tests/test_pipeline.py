"""Tests for the pipeline orchestrator."""

import json
from pathlib import Path

import pytest

import pipeline


class TestPipeline:
    """Integration tests for the pipeline."""

    def test_generate_only(self, tmp_path, monkeypatch):
        """--only generate runs only the generate stage with stub backend."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)

        result = pipeline.run(
            prompt="ambient test track",
            run_id="test_gen_only",
            only="generate",
            music_model="stub",
        )

        assert result["run_id"] == "test_gen_only"
        assert "error" not in result
        assert result["stages"]["generate"]["status"] == "ok"
        assert "rank" not in result["stages"]
        assert "content" not in result["stages"]
        assert "post" not in result["stages"]

    def test_full_pipeline_stub(self, tmp_path, monkeypatch):
        """Full pipeline runs end-to-end with stub generate and stub stages."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)

        result = pipeline.run(
            prompt="ambient test track",
            run_id="test_run_001",
            music_model="stub",
        )

        assert result["run_id"] == "test_run_001"
        assert "error" not in result
        assert result["stages"]["generate"]["status"] == "ok"
        assert result["stages"]["rank"]["status"] == "stub"
        assert result["stages"]["content"]["status"] == "stub"
        assert result["stages"]["post"]["status"] == "stub"

    def test_manifest_written(self, tmp_path, monkeypatch):
        """Pipeline writes a manifest.json in the run directory."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)

        pipeline.run(
            prompt="test",
            run_id="test_manifest",
            only="generate",
            music_model="stub",
        )

        manifest = tmp_path / "test_manifest" / "manifest.json"
        assert manifest.exists()
        data = json.loads(manifest.read_text())
        assert data["run_id"] == "test_manifest"

    def test_generate_creates_output_structure(self, tmp_path, monkeypatch):
        """Generate stage creates the expected directory structure."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)

        pipeline.run(
            prompt="structure test",
            run_id="test_dirs",
            only="generate",
            music_model="stub",
        )

        run_dir = tmp_path / "test_dirs"
        assert (run_dir / "generate").is_dir()

    def test_make_run_id_format(self):
        """Run IDs follow the expected timestamp_uuid format."""
        rid = pipeline._make_run_id()
        parts = rid.split("_")
        assert len(parts) == 3  # date, time, uuid
        assert len(parts[0]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # short uuid

    def test_invalid_stage_raises(self, tmp_path, monkeypatch):
        """Requesting an invalid --only stage raises ValueError."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)

        with pytest.raises(ValueError, match="Unknown stage"):
            pipeline.run(prompt="test", only="nonexistent")

    def test_ace_step_missing_weights_exits(self, tmp_path, monkeypatch):
        """ACE-Step without model weights raises SystemExit."""
        monkeypatch.setattr("config.OUTPUT_DIR", tmp_path)
        monkeypatch.setattr("config.MODEL_DIR", tmp_path / "empty_models")

        with pytest.raises(SystemExit, match="Missing ACE-Step"):
            pipeline.run(
                prompt="test",
                run_id="test_ace_fail",
                only="generate",
                music_model="ace-step",
            )
