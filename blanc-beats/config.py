"""
Central configuration for blanc-beats pipeline.

Loads settings from .env and exposes them as module-level constants.
All values are configurable via environment variables with sensible defaults.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))

# ── Model names ────────────────────────────────────────────────────────
MUSIC_MODEL = os.getenv("MUSIC_MODEL", "ace-step")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "stub")
# REASON: Image gen is stubbed for Stage 1 — focus is on audio output only.

# ── Ollama (local description gen — Stage 2+) ─────────────────────────
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ── Pipeline tuning ───────────────────────────────────────────────────
VARIANTS_PER_RUN = int(os.getenv("VARIANTS_PER_RUN", "4"))
TOP_N = int(os.getenv("TOP_N", "1"))

# ── Logging ────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Console handler
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# Rotating file handler — logs/pipeline.log, keep last 5 runs
LOG_DIR.mkdir(parents=True, exist_ok=True)
_file_handler = RotatingFileHandler(
    LOG_DIR / "pipeline.log",
    maxBytes=1_000_000,
    backupCount=5,
)
_file_handler.setLevel(getattr(logging, LOG_LEVEL))
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
)
logging.getLogger().addHandler(_file_handler)


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
