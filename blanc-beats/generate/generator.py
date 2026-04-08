from __future__ import annotations

"""
Music generation stage.

Generates N audio variants from a text prompt using a local model
(ACE-Step, HeartMuLa, etc.). The backend is swappable via config.MUSIC_MODEL.
"""

import logging
import subprocess
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import config

logger = logging.getLogger(__name__)

# REASON: dataclass over dict — gives us dot-access, type hints, and
# easy serialization later without pulling in pydantic for the MVP.


@dataclass
class Variant:
    """A single generated music variant."""

    path: Path
    prompt: str
    model: str
    metadata: dict = field(default_factory=dict)


def generate_variants(
    prompt: str,
    run_dir: Path,
    n: int | None = None,
    model: str | None = None,
) -> list[Variant]:
    """Generate *n* music variants for *prompt* and save them to *run_dir*.

    Args:
        prompt: Text description of the desired music.
        run_dir: Directory where audio files will be written.
        n: Number of variants to generate (default: config.VARIANTS_PER_RUN).
        model: Model backend to use (default: config.MUSIC_MODEL).

    Returns:
        List of Variant objects, one per generated file.
    """
    n = n or config.VARIANTS_PER_RUN
    model = model or config.MUSIC_MODEL

    gen_dir = run_dir / "generate"
    gen_dir.mkdir(parents=True, exist_ok=True)

    backend = _BACKENDS.get(model)
    if backend is None:
        raise ValueError(
            f"Unknown music model '{model}'. "
            f"Available: {list(_BACKENDS.keys())}"
        )

    logger.info("Generating %d variants with model=%s", n, model)
    variants = backend(prompt, gen_dir, n, model)
    logger.info("Generated %d variants in %s", len(variants), gen_dir)
    return variants


# ── Backends ───────────────────────────────────────────────────────────


def _generate_ace_step(
    prompt: str, gen_dir: Path, n: int, model: str
) -> list[Variant]:
    """Generate variants using the ACE-Step CLI.

    Expects `ace-step` to be on PATH or configured via ACE_STEP_BIN env var.
    """
    import os

    ace_bin = os.getenv("ACE_STEP_BIN", "ace-step")

    if not shutil.which(ace_bin):
        logger.warning(
            "ACE-Step binary '%s' not found on PATH — falling back to stub.",
            ace_bin,
        )
        return _generate_stub(prompt, gen_dir, n, model)

    variants: list[Variant] = []
    for i in range(n):
        out_path = gen_dir / f"variant_{i:03d}.wav"
        cmd = [ace_bin, "--prompt", prompt, "--output", str(out_path)]
        logger.info("Running: %s", " ".join(cmd))
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            variants.append(Variant(path=out_path, prompt=prompt, model=model))
        except subprocess.CalledProcessError as exc:
            logger.error(
                "ACE-Step failed for variant %d: %s\nstderr: %s",
                i, exc, exc.stderr,
            )
    return variants


def _generate_stub(
    prompt: str, gen_dir: Path, n: int, model: str
) -> list[Variant]:
    """Stub backend that writes minimal WAV files for testing.

    Produces valid WAV headers with 1 second of silence at 44100 Hz, 16-bit mono.
    """
    import struct

    sample_rate = 44100
    num_samples = sample_rate  # 1 second
    bits_per_sample = 16
    num_channels = 1
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align

    variants: list[Variant] = []
    for i in range(n):
        out_path = gen_dir / f"variant_{i:03d}.wav"
        with open(out_path, "wb") as f:
            # WAV header
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + data_size))
            f.write(b"WAVE")
            # fmt chunk
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))  # chunk size
            f.write(struct.pack("<H", 1))   # PCM
            f.write(struct.pack("<H", num_channels))
            f.write(struct.pack("<I", sample_rate))
            f.write(struct.pack("<I", byte_rate))
            f.write(struct.pack("<H", block_align))
            f.write(struct.pack("<H", bits_per_sample))
            # data chunk
            f.write(b"data")
            f.write(struct.pack("<I", data_size))
            f.write(b"\x00" * data_size)
        variants.append(
            Variant(
                path=out_path,
                prompt=prompt,
                model="stub",
                metadata={"note": "silent stub for testing"},
            )
        )
        logger.debug("Wrote stub variant: %s", out_path)

    return variants


# ── Backend registry ───────────────────────────────────────────────────

_BACKENDS: dict[str, callable] = {
    "ace-step": _generate_ace_step,
    "stub": _generate_stub,
}
