from __future__ import annotations

"""
Main pipeline orchestrator for blanc-beats.

Chains: generate → rank → content → post
Each stage reads from / writes to outputs/{run_id}/<stage>/
"""

import json
import logging
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import config
from generate import generate_variants
from rank import rank_variants
from content import generate_description, generate_cover
from post import upload_to_youtube

logger = logging.getLogger(__name__)


def run(
    prompt: str,
    run_id: str | None = None,
    skip_post: bool = False,
    music_model: str | None = None,
    image_model: str | None = None,
) -> dict:
    """Execute the full blanc-beats pipeline.

    Args:
        prompt: Text description of the music to generate.
        run_id: Optional run identifier (auto-generated if omitted).
        skip_post: If True, skip the posting stage (useful for testing).
        music_model: Override music generation model.
        image_model: Override image generation model.

    Returns:
        Dict summarizing the run results.
    """
    run_id = run_id or _make_run_id()
    run_dir = config.get_run_dir(run_id)

    logger.info("═══ Pipeline start: run_id=%s ═══", run_id)
    logger.info("Prompt: %s", prompt)

    result = {
        "run_id": run_id,
        "prompt": prompt,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stages": {},
    }

    try:
        # ── Stage 1: Generate ──────────────────────────────────────
        logger.info("── Stage 1/4: Generate ──")
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

        # ── Stage 2: Rank ──────────────────────────────────────────
        logger.info("── Stage 2/4: Rank ──")
        winners = rank_variants(variants=variants, run_dir=run_dir)
        result["stages"]["rank"] = {
            "status": "ok",
            "winners": [
                {"file": str(w.variant.path), "score": w.score}
                for w in winners
            ],
        }

        if not winners:
            raise RuntimeError("No variants survived ranking.")

        best = winners[0]

        # ── Stage 3: Content ───────────────────────────────────────
        logger.info("── Stage 3/4: Content ──")
        description = generate_description(
            prompt=prompt,
            metadata=best.breakdown,
        )

        cover_path = generate_cover(
            prompt=f"Album cover art for: {prompt}",
            run_dir=run_dir,
            model=image_model,
        )

        # Save description to file for debuggability
        desc_path = run_dir / "content" / "description.txt"
        desc_path.parent.mkdir(parents=True, exist_ok=True)
        desc_path.write_text(description)

        result["stages"]["content"] = {
            "status": "ok",
            "description": description,
            "cover": str(cover_path),
        }

        # ── Stage 4: Post ─────────────────────────────────────────
        if skip_post:
            logger.info("── Stage 4/4: Post (SKIPPED) ──")
            result["stages"]["post"] = {"status": "skipped"}
        else:
            logger.info("── Stage 4/4: Post ──")
            title = _make_title(prompt)
            post_result = upload_to_youtube(
                audio_path=best.variant.path,
                title=title,
                description=description,
                cover_path=cover_path,
            )
            result["stages"]["post"] = {"status": "ok", **post_result}

    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        result["error"] = str(exc)
    finally:
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        # Write run manifest
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


def _make_title(prompt: str, max_len: int = 80) -> str:
    """Create a YouTube-friendly title from the prompt.

    Args:
        prompt: Original music prompt.
        max_len: Maximum title length.

    Returns:
        Truncated, clean title string.
    """
    title = f"Blanc Beats — {prompt}"
    if len(title) > max_len:
        title = title[: max_len - 3] + "..."
    return title


# ── CLI entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the blanc-beats pipeline.")
    parser.add_argument("prompt", help="Music generation prompt")
    parser.add_argument("--run-id", help="Custom run ID")
    parser.add_argument("--skip-post", action="store_true", help="Skip posting stage")
    parser.add_argument("--music-model", help="Override music model")
    parser.add_argument("--image-model", help="Override image model")

    args = parser.parse_args()

    result = run(
        prompt=args.prompt,
        run_id=args.run_id,
        skip_post=args.skip_post,
        music_model=args.music_model,
        image_model=args.image_model,
    )

    print(json.dumps(result, indent=2, default=str))
