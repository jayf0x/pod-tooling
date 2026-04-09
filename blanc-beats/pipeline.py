from __future__ import annotations

"""
Main pipeline orchestrator for blanc-beats.

Chains: generate → rank → content → post
Each stage reads from / writes to outputs/{run_id}/<stage>/

Supports running individual stages via --only flag:
    python pipeline.py "chill lo-fi beat" --only generate
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import config
from generate import generate_variants

logger = logging.getLogger(__name__)

# ── Valid stages ──────────────────────────────────────────────────────
STAGES = ("generate", "rank", "content", "post")


def run(
    prompt: str,
    run_id: str | None = None,
    only: str | None = None,
    music_model: str | None = None,
) -> dict:
    """Execute the blanc-beats pipeline (or a single stage).

    Args:
        prompt: Text description of the music to generate.
        run_id: Optional run identifier (auto-generated if omitted).
        only: If set, run only this single stage. Must be one of STAGES.
        music_model: Override music generation model.

    Returns:
        Dict summarizing the run results.
    """
    if only and only not in STAGES:
        raise ValueError(f"Unknown stage '{only}'. Valid stages: {list(STAGES)}")

    run_id = run_id or _make_run_id()
    run_dir = config.get_run_dir(run_id)

    logger.info("═══ Pipeline start: run_id=%s ═══", run_id)
    logger.info("Prompt: %s", prompt)
    if only:
        logger.info("Running single stage: %s", only)

    result = {
        "run_id": run_id,
        "prompt": prompt,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stages": {},
    }

    try:
        # ── Stage 1: Generate ──────────────────────────────────────
        if only is None or only == "generate":
            logger.info("── Stage: Generate ──")
            variants = generate_variants(
                prompt=prompt,
                run_dir=run_dir,
                model=music_model,
            )
            result["stages"]["generate"] = {
                "status": "ok",
                "count": len(variants),
                "files": [str(v.path) for v in variants],
            }

        # ── Stage 2: Rank (stub) ──────────────────────────────────
        if only is None or only == "rank":
            logger.info("── Stage: Rank ──")
            print("[STUB] rank stage skipped")
            result["stages"]["rank"] = {"status": "stub"}

        # ── Stage 3: Content (stub) ───────────────────────────────
        if only is None or only == "content":
            logger.info("── Stage: Content ──")
            print("[STUB] content stage skipped")
            result["stages"]["content"] = {"status": "stub"}

        # ── Stage 4: Post (stub) ──────────────────────────────────
        if only is None or only == "post":
            logger.info("── Stage: Post ──")
            print("[STUB] post stage skipped")
            result["stages"]["post"] = {"status": "stub"}

    except SystemExit:
        raise
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        result["error"] = str(exc)
    finally:
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        manifest_path = run_dir / "manifest.json"
        manifest_path.write_text(json.dumps(result, indent=2, default=str))
        logger.info("Manifest written to %s", manifest_path)
        logger.info("═══ Pipeline end: run_id=%s ═══", run_id)

    return result


def _make_run_id() -> str:
    """Generate a timestamped run ID.

    Returns:
        String like '20260408_143052_a1b2c3'.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"{ts}_{short_uuid}"


# ── CLI entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the blanc-beats pipeline.")
    parser.add_argument("prompt", help="Music generation prompt")
    parser.add_argument("--run-id", help="Custom run ID (also used to resume a prior run)")
    parser.add_argument(
        "--only",
        choices=STAGES,
        help="Run only a single stage in isolation",
    )
    parser.add_argument("--music-model", help="Override music model")

    args = parser.parse_args()

    result = run(
        prompt=args.prompt,
        run_id=args.run_id,
        only=args.only,
        music_model=args.music_model,
    )

    print(json.dumps(result, indent=2, default=str))
