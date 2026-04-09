"""
Model setup script for blanc-beats.

Downloads model weights from HuggingFace Hub into the local models/ directory.
Run this once before using the pipeline with real models.

Usage:
    python setup_models.py              # Download all models
    python setup_models.py ace-step     # Download only ACE-Step
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_ROOT / "models"

# ── Model registry ────────────────────────────────────────────────────
# Each entry: (local_dir_name, huggingface_repo_id, description, approx_size)
MODELS = {
    "ace-step": {
        "dir": "ACE-Step",
        "repo_id": "ACE-Step/ACE-Step-v1-5",
        "description": "ACE-Step 1.5 — text-to-music generation",
        "size": "~3.5 GB",
    },
}


def download_model(name: str) -> None:
    """Download a single model from HuggingFace Hub.

    Args:
        name: Model key from the MODELS registry.

    Raises:
        SystemExit: If huggingface-hub is not installed or download fails.
    """
    if name not in MODELS:
        logger.error("Unknown model '%s'. Available: %s", name, list(MODELS.keys()))
        raise SystemExit(1)

    info = MODELS[name]
    dest = MODEL_DIR / info["dir"]

    if dest.exists() and any(dest.iterdir()):
        logger.info("Model '%s' already exists at %s — skipping.", name, dest)
        return

    logger.info(
        "Downloading %s (%s) from %s ...",
        info["description"], info["size"], info["repo_id"],
    )

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        logger.error("huggingface-hub not installed. Run: pip install huggingface-hub")
        raise SystemExit(
            "Missing dependency: huggingface-hub.\n"
            "Fix: run `pip install -r requirements.txt`"
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        snapshot_download(
            repo_id=info["repo_id"],
            local_dir=str(dest),
        )
        logger.info("Downloaded '%s' to %s", name, dest)
    except Exception as exc:
        logger.error("Download failed for '%s': %s", name, exc, exc_info=True)
        raise SystemExit(f"Failed to download {name}: {exc}")


def main() -> None:
    """Entry point — download requested or all models."""
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(MODELS.keys())

    print(f"Model directory: {MODEL_DIR}")
    print(f"Models to download: {targets}\n")

    for name in targets:
        download_model(name)

    print("\nDone. You can now run the pipeline:")
    print('  python pipeline.py "chill lo-fi beat" --only generate')


if __name__ == "__main__":
    main()
