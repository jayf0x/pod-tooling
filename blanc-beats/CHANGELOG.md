# Changelog

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
