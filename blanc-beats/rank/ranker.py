from __future__ import annotations

"""
Ranking stage.

Scores generated variants and returns the top N.
MVP uses basic audio heuristics (RMS energy, duration validity).
Designed to be replaced with a learned ranker later.
"""

import logging
import struct
import wave
from dataclasses import dataclass
from pathlib import Path

from generate.generator import Variant
import config

logger = logging.getLogger(__name__)


@dataclass
class ScoredVariant:
    """A variant with its computed score."""

    variant: Variant
    score: float
    breakdown: dict


def rank_variants(
    variants: list[Variant],
    run_dir: Path,
    top_n: int | None = None,
) -> list[ScoredVariant]:
    """Score and rank variants, returning the top N.

    Args:
        variants: List of generated Variant objects.
        run_dir: Pipeline run directory (for writing rank report).
        top_n: Number of top variants to keep (default: config.TOP_N).

    Returns:
        Top N ScoredVariant objects sorted best-first.
    """
    top_n = top_n or config.TOP_N

    if not variants:
        logger.warning("No variants to rank.")
        return []

    scored: list[ScoredVariant] = []
    for v in variants:
        try:
            score, breakdown = _score_variant(v)
            scored.append(ScoredVariant(variant=v, score=score, breakdown=breakdown))
            logger.debug("Scored %s: %.4f (%s)", v.path.name, score, breakdown)
        except Exception as exc:
            logger.error("Failed to score %s: %s", v.path, exc)

    scored.sort(key=lambda s: s.score, reverse=True)
    winners = scored[:top_n]

    logger.info(
        "Ranked %d variants → top %d: %s",
        len(scored),
        len(winners),
        [w.variant.path.name for w in winners],
    )

    # Write rank report for debuggability
    rank_dir = run_dir / "rank"
    rank_dir.mkdir(parents=True, exist_ok=True)
    _write_report(scored, rank_dir / "rank_report.txt")

    return winners


def _score_variant(variant: Variant) -> tuple[float, dict]:
    """Compute a simple quality score for an audio variant.

    MVP heuristics:
    - RMS energy (louder ≠ better, but silence = bad)
    - File size sanity check
    - Valid WAV structure

    Args:
        variant: The Variant to score.

    Returns:
        Tuple of (overall_score, breakdown_dict).
    """
    path = variant.path
    breakdown = {}

    if not path.exists():
        raise FileNotFoundError(f"Variant file missing: {path}")

    # File size score: penalize very small files (likely corrupt)
    file_size = path.stat().st_size
    # REASON: 1KB threshold catches corrupt/empty WAVs but allows short clips
    size_score = min(file_size / 50_000, 1.0)
    breakdown["size_score"] = round(size_score, 4)

    # RMS energy from raw PCM data
    rms = _compute_rms(path)
    # Normalize RMS to 0-1 range (16-bit audio max RMS ~23170)
    rms_score = min(rms / 5000, 1.0) if rms > 0 else 0.0
    breakdown["rms_score"] = round(rms_score, 4)
    breakdown["rms_raw"] = round(rms, 2)

    # Duration check
    duration = _get_duration(path)
    breakdown["duration_s"] = round(duration, 2)
    # Prefer tracks between 15s and 300s
    if 15 <= duration <= 300:
        dur_score = 1.0
    elif duration > 0:
        dur_score = 0.5
    else:
        dur_score = 0.0
    breakdown["duration_score"] = dur_score

    overall = (size_score * 0.2) + (rms_score * 0.5) + (dur_score * 0.3)
    return round(overall, 4), breakdown


def _compute_rms(path: Path) -> float:
    """Compute RMS energy of a WAV file.

    Args:
        path: Path to the WAV file.

    Returns:
        RMS energy value as a float.
    """
    try:
        with wave.open(str(path), "rb") as wf:
            n_frames = wf.getnframes()
            if n_frames == 0:
                return 0.0
            sample_width = wf.getsampwidth()
            raw = wf.readframes(n_frames)

            if sample_width == 2:
                fmt = f"<{n_frames * wf.getnchannels()}h"
                samples = struct.unpack(fmt, raw)
            else:
                # Fallback: treat as bytes
                samples = list(raw)

            sum_sq = sum(s * s for s in samples)
            return (sum_sq / len(samples)) ** 0.5
    except Exception as exc:
        logger.error("RMS computation failed for %s: %s", path, exc)
        return 0.0


def _get_duration(path: Path) -> float:
    """Get duration in seconds of a WAV file.

    Args:
        path: Path to the WAV file.

    Returns:
        Duration in seconds.
    """
    try:
        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / wf.getframerate()
    except Exception as exc:
        logger.error("Duration read failed for %s: %s", path, exc)
        return 0.0


def _write_report(scored: list[ScoredVariant], path: Path) -> None:
    """Write a human-readable ranking report.

    Args:
        scored: All scored variants in rank order.
        path: Output file path.
    """
    lines = ["# Ranking Report", ""]
    for i, sv in enumerate(scored, 1):
        lines.append(f"{i}. {sv.variant.path.name}  score={sv.score:.4f}")
        for k, v in sv.breakdown.items():
            lines.append(f"   {k}: {v}")
        lines.append("")
    path.write_text("\n".join(lines))
    logger.debug("Rank report written to %s", path)
