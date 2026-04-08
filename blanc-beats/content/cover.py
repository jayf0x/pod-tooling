from __future__ import annotations

"""
Cover image generation stage.

Generates a cover image for a music track using a local image model
(Flux, etc.). The backend is swappable via config.IMAGE_MODEL.
"""

import logging
import shutil
import subprocess
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def generate_cover(
    prompt: str,
    run_dir: Path,
    model: str | None = None,
) -> Path:
    """Generate a cover image for a music track.

    Args:
        prompt: Text description to guide image generation.
        run_dir: Pipeline run directory.
        model: Image model backend (default: config.IMAGE_MODEL).

    Returns:
        Path to the generated image file.
    """
    model = model or config.IMAGE_MODEL
    content_dir = run_dir / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    out_path = content_dir / "cover.png"

    backend = _BACKENDS.get(model)
    if backend is None:
        raise ValueError(
            f"Unknown image model '{model}'. Available: {list(_BACKENDS.keys())}"
        )

    logger.info("Generating cover image with model=%s", model)
    backend(prompt, out_path)
    logger.info("Cover image saved to %s", out_path)
    return out_path


def _generate_flux(prompt: str, out_path: Path) -> None:
    """Generate cover using the Flux CLI.

    Args:
        prompt: Image generation prompt.
        out_path: Where to save the image.
    """
    import os

    flux_bin = os.getenv("FLUX_BIN", "flux")

    if not shutil.which(flux_bin):
        logger.warning(
            "Flux binary '%s' not found on PATH — falling back to stub.", flux_bin
        )
        _generate_stub(prompt, out_path)
        return

    cmd = [flux_bin, "--prompt", prompt, "--output", str(out_path)]
    logger.info("Running: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        logger.error("Flux failed: %s\nstderr: %s", exc, exc.stderr)
        raise


def _generate_stub(prompt: str, out_path: Path) -> None:
    """Write a minimal valid PNG as a placeholder.

    Produces a 1x1 pixel black PNG. Good enough for pipeline testing.

    Args:
        prompt: Image generation prompt (unused, kept for interface parity).
        out_path: Where to save the image.
    """
    # Minimal valid PNG: 1x1 black pixel
    import struct
    import zlib

    def _make_png() -> bytes:
        """Build a minimal 1x1 black PNG in memory."""
        signature = b"\x89PNG\r\n\x1a\n"

        # IHDR
        ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
        ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

        # IDAT
        raw_data = b"\x00\x00\x00\x00"  # filter byte + RGB
        compressed = zlib.compress(raw_data)
        idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
        idat = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc)

        # IEND
        iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
        iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

        return signature + ihdr + idat + iend

    out_path.write_bytes(_make_png())
    logger.debug("Wrote stub cover image: %s", out_path)


# ── Backend registry ───────────────────────────────────────────────────

_BACKENDS: dict[str, callable] = {
    "flux": _generate_flux,
    "stub": _generate_stub,
}
