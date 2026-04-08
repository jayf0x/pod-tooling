"""
Central configuration for blanc-beats pipeline.
Loads settings from .env and exposes them as module-level constants.
"""

import os
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))

# ── API keys ───────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_OAUTH_TOKEN_FILE = os.getenv("YOUTUBE_OAUTH_TOKEN_FILE", "youtube_token.json")

# ── Model names ────────────────────────────────────────────────────────
MUSIC_MODEL = os.getenv("MUSIC_MODEL", "ace-step")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "flux")
DESCRIPTION_MODEL = os.getenv("DESCRIPTION_MODEL", "claude-sonnet-4-20250514")

# ── Pipeline tuning ───────────────────────────────────────────────────
VARIANTS_PER_RUN = int(os.getenv("VARIANTS_PER_RUN", "4"))
TOP_N = int(os.getenv("TOP_N", "1"))

# ── Logging ────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


def get_run_dir(run_id: str) -> Path:
    """Return and create the output directory for a given run.

    Args:
        run_id: Unique identifier for this pipeline run.

    Returns:
        Path to the run's output directory.
    """
    run_dir = OUTPUT_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
