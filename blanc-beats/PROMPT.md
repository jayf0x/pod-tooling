# PROMPT.md — current project state
_Update this file as the project grows. It is a living document._

## What this is
Blanc Beats: fully local AI music generation pipeline.
generate music → rank best → create post (description + cover art) → publish.

No cloud generation. API-only for publishing (later). Local models for everything else.

## Current priority: Stage 1 only — get real audio out of a real local model
Do not work on rank, content, or post stages right now.
Do not touch YouTube, Twitter, or any posting logic.
Focus: prompt in → real audio file out → I can press play and hear something.

## Stack decisions
- Python: 3.11 minimum. Do not use 3.9. Check `python3 --version` before scaffolding.
- Platform: macOS (Apple Silicon). Prefer MLX-optimized paths where available.
  If a library has an MPS or Metal backend, use it. If MLX variant exists, prefer it.
- Audio I/O: use soundfile or scipy.io.wavfile for WAV output. Never hand-roll WAV headers.
- Music gen models (pick one to get working first, stub the other):
    - ACE-Step 1.5 — primary target
    - HeartMuLa — fallback
- Description gen: Ollama (local). No Anthropic API key and package needed.
  Use ollama Python client. Model: llama3 or qwen3.5:8b (user-configurable via .env).
- Image gen: Flux via mlx-image or diffusers with MPS. Stub is fine for now.

## What "working" means for stage 1
1. I run: `python pipeline.py "chill lo-fi beat" --only generate`
2. A real .wav or .mp3 file appears in outputs/{run_id}/generate/
3. I can open it and hear audio generated from the prompt
4. It does not crash with a missing model — it tells me exactly what to install and how

## Model installation
- Provide a setup script or clear CLI instructions to download the model weights
- Target: HuggingFace Hub via `huggingface-hub` CLI or snapshot_download()
- Model weights go to: models/ in the project root (gitignored)
- Document exact model IDs and sizes in README.md under "Model setup"

## Debug mode (important)
Add a --stage flag to pipeline.py so any single stage can be run in isolation:
  python pipeline.py "prompt" --only generate
  python pipeline.py "prompt" --only rank
  python pipeline.py "prompt" --only content
  python pipeline.py "prompt" --only post
Each stage should be independently runnable without running the full pipeline.
A stage can load a previous run's outputs via --run-id to resume from that point.

## Error handling
- Log errors to logs/pipeline.log (rotating, keep last 5 runs)
- Critical errors (missing model weights, missing env var, bad config) must:
    1. Log clearly with the exact fix needed ("Run: python setup_models.py")
    2. Raise SystemExit — do not continue the pipeline silently
- Non-critical errors (e.g. one variant failed to generate): log + continue

## Code quality rules
- No hand-rolled binary formats. Use libraries.
- No stub files that silently succeed — stubs must print "[STUB] stage skipped"
  so it's obvious nothing real ran
- Every new module gets a docstring explaining what it does and what it returns
- Tests must test real behavior, not just "did it return something"
  Minimum: test that generate stage produces a file with non-zero size

## What to update after changes
- CHANGELOG.md: date + what changed + why
- BACKLOG.md: anything noticed but not fixed
- README.md: keep model setup and quickstart accurate
