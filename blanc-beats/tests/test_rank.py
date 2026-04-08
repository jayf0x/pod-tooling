"""Tests for the rank module."""

import wave
import struct
from pathlib import Path

import pytest

from generate.generator import Variant
from rank.ranker import rank_variants, _score_variant, _compute_rms


class TestRankVariants:
    """Tests for the ranking stage."""

    def _make_wav(self, path: Path, n_samples: int = 44100, amplitude: int = 0) -> Path:
        """Helper: write a WAV file with a given number of samples.

        Args:
            path: Output file path.
            n_samples: Number of samples (at 44100 Hz, this is seconds).
            amplitude: Sample amplitude (0 = silence).

        Returns:
            The path written to.
        """
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            data = struct.pack(f"<{n_samples}h", *([amplitude] * n_samples))
            wf.writeframes(data)
        return path

    def test_rank_returns_top_n(self, tmp_path):
        """rank_variants returns exactly top_n results."""
        variants = []
        for i in range(4):
            p = tmp_path / f"v{i}.wav"
            self._make_wav(p, n_samples=44100 * (i + 1), amplitude=100 * (i + 1))
            variants.append(Variant(path=p, prompt="test", model="stub"))

        winners = rank_variants(variants, run_dir=tmp_path, top_n=2)
        assert len(winners) == 2

    def test_rank_sorted_by_score(self, tmp_path):
        """Winners are sorted best-first."""
        # Make one loud, one silent
        loud = tmp_path / "loud.wav"
        self._make_wav(loud, n_samples=44100, amplitude=10000)

        silent = tmp_path / "silent.wav"
        self._make_wav(silent, n_samples=44100, amplitude=0)

        variants = [
            Variant(path=silent, prompt="test", model="stub"),
            Variant(path=loud, prompt="test", model="stub"),
        ]

        winners = rank_variants(variants, run_dir=tmp_path, top_n=2)
        assert winners[0].score >= winners[1].score

    def test_rank_empty_list(self, tmp_path):
        """Empty input returns empty output."""
        result = rank_variants([], run_dir=tmp_path)
        assert result == []

    def test_score_missing_file(self, tmp_path):
        """Scoring a variant with a missing file raises FileNotFoundError."""
        v = Variant(path=tmp_path / "nope.wav", prompt="test", model="stub")
        with pytest.raises(FileNotFoundError):
            _score_variant(v)

    def test_rank_report_written(self, tmp_path):
        """Ranking writes a report file."""
        p = tmp_path / "v.wav"
        self._make_wav(p)
        variants = [Variant(path=p, prompt="test", model="stub")]
        rank_variants(variants, run_dir=tmp_path, top_n=1)
        assert (tmp_path / "rank" / "rank_report.txt").exists()

    def test_rms_silent_file(self, tmp_path):
        """RMS of a silent file is 0."""
        p = tmp_path / "silent.wav"
        self._make_wav(p, amplitude=0)
        assert _compute_rms(p) == 0.0

    def test_rms_nonzero(self, tmp_path):
        """RMS of a non-silent file is positive."""
        p = tmp_path / "loud.wav"
        self._make_wav(p, amplitude=5000)
        assert _compute_rms(p) > 0
