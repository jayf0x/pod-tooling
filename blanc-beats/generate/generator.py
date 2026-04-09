from __future__ import annotations

"""
Music generation stage.

Generates N audio variants from a text prompt using a local model.
Primary target: ACE-Step 1.5 via HuggingFace/diffusers.
Fallback: stub that prints [STUB] so it's obvious nothing real ran.

Returns a list of Variant dataclasses pointing to the generated .wav files.
"""

import logging
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

    Raises:
        ValueError: If model is not in the backend registry.
        SystemExit: If model weights are missing (with install instructions).
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
    """Generate variants using ACE-Step 1.5 via the ace-step Python package.

    Expects model weights in config.MODEL_DIR / 'ACE-Step'.
    If weights are missing, raises SystemExit with exact install instructions.

    Args:
        prompt: Text description of the desired music.
        gen_dir: Output directory for .wav files.
        n: Number of variants to generate.
        model: Model name for metadata.

    Returns:
        List of Variant objects.

    Raises:
        SystemExit: If ace-step package or model weights are not available.
    """
    model_dir = config.MODEL_DIR / "ACE-Step"

    if not model_dir.exists():
        logger.error(
            "ACE-Step model weights not found at %s. "
            "Run: python setup_models.py",
            model_dir,
        )
        raise SystemExit(
            f"Missing ACE-Step model weights at {model_dir}.\n"
            "Fix: run `python setup_models.py` to download them."
        )

    try:
        import soundfile as sf
    except ImportError:
        logger.error("soundfile not installed. Run: pip install soundfile")
        raise SystemExit(
            "Missing dependency: soundfile.\n"
            "Fix: run `pip install -r requirements.txt`"
        )

    # REASON: ACE-Step inference is done via its pipeline API.
    # We import lazily so the rest of the codebase works without it installed.
    try:
        from ace_step.pipeline import ACEStepPipeline
    except ImportError:
        logger.error(
            "ace-step package not installed. "
            "Run: pip install ace-step"
        )
        raise SystemExit(
            "Missing dependency: ace-step.\n"
            "Fix: run `pip install ace-step`"
        )

    logger.info("Loading ACE-Step pipeline from %s", model_dir)
    pipe = ACEStepPipeline(model_dir=str(model_dir))

    variants: list[Variant] = []
    for i in range(n):
        out_path = gen_dir / f"variant_{i:03d}.wav"
        logger.info("Generating variant %d/%d", i + 1, n)
        try:
            # REASON: ACE-Step returns audio as a numpy array + sample rate.
            # We write it out with soundfile for clean WAV output.
            audio, sr = pipe.generate(prompt=prompt)
            sf.write(str(out_path), audio, sr)
            variants.append(Variant(path=out_path, prompt=prompt, model=model))
            logger.info("Wrote variant: %s", out_path)
        except Exception as exc:
            logger.error(
                "ACE-Step failed for variant %d: %s", i, exc, exc_info=True
            )
    return variants


def _generate_stub(
    prompt: str, gen_dir: Path, n: int, model: str
) -> list[Variant]:
    """Stub backend — prints [STUB] and writes minimal WAV files for testing.

    Produces valid WAV headers with 1 second of silence at 44100 Hz, 16-bit mono.
    Uses soundfile if available, falls back to the wave stdlib module.

    Args:
        prompt: Text description (stored in metadata).
        gen_dir: Output directory for .wav files.
        n: Number of variants to generate.
        model: Model name (overridden to 'stub' in metadata).

    Returns:
        List of Variant objects.
    """
    import numpy as np

    print("[STUB] generate stage — writing silent test WAVs")

    sample_rate = 44100
    duration_s = 1
    samples = np.zeros(sample_rate * duration_s, dtype=np.float32)

    try:
        import soundfile as sf
        writer = lambda path, data, sr: sf.write(str(path), data, sr)
    except ImportError:
        # Fallback: use stdlib wave module
        import struct
        import wave as wave_mod

        def writer(path, data, sr):
            """Write float32 samples as 16-bit WAV via stdlib."""
            int_data = (data * 32767).astype(np.int16)
            with wave_mod.open(str(path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(int_data.tobytes())

    variants: list[Variant] = []
    for i in range(n):
        out_path = gen_dir / f"variant_{i:03d}.wav"
        writer(out_path, samples, sample_rate)
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
