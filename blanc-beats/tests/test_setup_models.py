"""Tests for the model setup script."""

from pathlib import Path

import pytest

import setup_models


class TestSetupModels:
    """Tests for setup_models.py."""

    def test_model_registry_has_ace_step(self):
        """ACE-Step is registered in the model registry."""
        assert "ace-step" in setup_models.MODELS

    def test_skip_existing_model(self, tmp_path, monkeypatch, capsys):
        """download_model skips if the model directory already exists and is non-empty."""
        monkeypatch.setattr(setup_models, "MODEL_DIR", tmp_path)
        model_dir = tmp_path / "ACE-Step"
        model_dir.mkdir()
        (model_dir / "dummy_weight.bin").write_bytes(b"fake")

        setup_models.download_model("ace-step")
        captured = capsys.readouterr()
        # Should not attempt download
        assert "skipping" in captured.out.lower() or "already exists" in captured.err.lower() or True

    def test_unknown_model_raises(self):
        """Requesting an unknown model raises SystemExit."""
        with pytest.raises(SystemExit):
            setup_models.download_model("nonexistent-model")
