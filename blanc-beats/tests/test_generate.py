"""Tests for the generate module."""

import tempfile
import wave
from pathlib import Path

import pytest

from generate.generator import generate_variants, Variant, _generate_stub


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
        """Each stub variant is a valid WAV file."""
        variants = generate_variants(
            prompt="chill lo-fi beat",
            run_dir=tmp_path,
            n=2,
            model="stub",
        )
        for v in variants:
            assert v.path.exists()
            assert v.path.suffix == ".wav"
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

    def test_ace_step_falls_back_to_stub(self, tmp_path):
        """ACE-Step backend falls back to stub when binary not found."""
        variants = generate_variants(
            prompt="test", run_dir=tmp_path, n=1, model="ace-step"
        )
        # Should succeed via fallback
        assert len(variants) == 1
        assert variants[0].model == "stub"
