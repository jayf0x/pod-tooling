"""Tests for the generate module."""

import wave
from pathlib import Path

import pytest

from generate.generator import generate_variants, Variant


class TestGenerateVariants:
    """Tests for generate_variants and the stub backend."""

    def test_stub_generates_correct_count(self, tmp_path):
        """Stub backend produces exactly N variants."""
        variants = generate_variants(
            prompt="test prompt",
            run_dir=tmp_path,
            n=3,
            model="stub",
        )
        assert len(variants) == 3

    def test_stub_creates_wav_files(self, tmp_path):
        """Each stub variant is a valid WAV file with non-zero size."""
        variants = generate_variants(
            prompt="chill lo-fi beat",
            run_dir=tmp_path,
            n=2,
            model="stub",
        )
        for v in variants:
            assert v.path.exists()
            assert v.path.suffix == ".wav"
            assert v.path.stat().st_size > 0
            # Verify it's a valid WAV
            with wave.open(str(v.path), "rb") as wf:
                assert wf.getnframes() > 0
                assert wf.getframerate() == 44100

    def test_variant_has_correct_metadata(self, tmp_path):
        """Variant dataclass carries prompt and model info."""
        variants = generate_variants(
            prompt="ambient synth pad",
            run_dir=tmp_path,
            n=1,
            model="stub",
        )
        v = variants[0]
        assert v.prompt == "ambient synth pad"
        assert v.model == "stub"
        assert isinstance(v.metadata, dict)

    def test_output_dir_structure(self, tmp_path):
        """Variants are written into run_dir/generate/."""
        generate_variants(prompt="test", run_dir=tmp_path, n=1, model="stub")
        gen_dir = tmp_path / "generate"
        assert gen_dir.is_dir()
        assert len(list(gen_dir.glob("*.wav"))) == 1

    def test_unknown_model_raises(self, tmp_path):
        """Requesting a non-existent model raises ValueError."""
        with pytest.raises(ValueError, match="Unknown music model"):
            generate_variants(prompt="test", run_dir=tmp_path, model="nonexistent")

    def test_ace_step_missing_weights_raises_exit(self, tmp_path, monkeypatch):
        """ACE-Step backend raises SystemExit when model weights are missing."""
        monkeypatch.setattr("config.MODEL_DIR", tmp_path / "no_models")
        with pytest.raises(SystemExit, match="Missing ACE-Step"):
            generate_variants(
                prompt="test", run_dir=tmp_path, n=1, model="ace-step"
            )

    def test_stub_prints_stub_marker(self, tmp_path, capsys):
        """Stub backend prints [STUB] so it's obvious nothing real ran."""
        generate_variants(prompt="test", run_dir=tmp_path, n=1, model="stub")
        captured = capsys.readouterr()
        assert "[STUB]" in captured.out
