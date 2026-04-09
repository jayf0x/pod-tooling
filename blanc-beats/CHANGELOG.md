# Changelog

## 2026-04-08 — Codebase refocus: Stage 1 only (real audio generation)

### What
Rewrote the entire codebase to match the updated PROMPT.md.
Only the generate stage is active now; rank, content, and post are stubs.

### Why
Narrowing scope to Stage 1: prompt in → real audio file out.
Everything else is deferred until audio generation is proven.

### Details
- **pipeline.py**: Added `--only` flag for single-stage execution, removed
  old multi-stage orchestration. Rank/content/post print `[STUB]`.
- **config.py**: Removed Claude API and YouTube config. Added Ollama, MODEL_DIR,
  LOG_DIR. Added rotating file handler (logs/pipeline.log, 5 backups).
- **generate/generator.py**: ACE-Step backend now uses Python pipeline API
  (ace_step.pipeline) instead of CLI binary. Raises SystemExit with exact
  install instructions if weights or packages are missing. Stub uses numpy +
  soundfile (with wave stdlib fallback) and prints `[STUB]`.
- **rank/, content/, post/**: Gutted to stub modules that print `[STUB]`.
  Old ranker, describe, cover, and youtube code removed.
- **setup_models.py**: New script to download ACE-Step weights from HuggingFace
  Hub via snapshot_download().
- **requirements.txt**: Removed anthropic, google-api-python-client, google-auth.
  Added numpy, soundfile, huggingface-hub.
- **.env.example**: Simplified for Stage 1. Added OLLAMA_MODEL, MODEL_DIR, LOG_DIR.
- **.gitignore**: Added models/ and logs/.
- **tests/**: Rewritten — 21 tests covering pipeline, generate, stubs, and
  setup_models. Tests verify real behavior (file sizes, [STUB] markers, SystemExit).
- **README.md**: Updated with model setup, new CLI usage, and current stage status.

## 2026-04-08 — MVP: Full pipeline scaffold

### What
Built the complete end-to-end pipeline: `generate → rank → content → post`.

### Why
First working version to prove the architecture and enable iterating on
individual stages independently.

### Details
- **generate/**: Music generation with ACE-Step backend + stub fallback.
  Produces valid WAV files. Falls back to stub when binary not found.
- **rank/**: Scores variants by RMS energy, file size, and duration.
  Writes rank report for debuggability.
- **content/**: Description via Claude API (with placeholder fallback).
  Cover image via Flux backend + stub fallback.
- **post/**: YouTube upload via Data API v3 with dry-run mode when
  credentials aren't present.
- **pipeline.py**: Orchestrator chains all stages, writes manifest.json
  per run, supports CLI invocation.
- **config.py**: Central config from .env, no hardcoded values.
- **tests/**: Unit tests for all modules (28 tests).
