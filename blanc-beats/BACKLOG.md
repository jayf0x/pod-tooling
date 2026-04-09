# Backlog

Non-blocking issues and future ideas. Newest at top.

## 2026-04-08 (Stage 1 refocus)

- [ ] **ACE-Step pipeline API verification**: Confirm ace_step.pipeline.ACEStepPipeline
      is the correct import path and that generate() returns (audio_array, sample_rate).
      May need to adjust based on actual package API once installed.
- [ ] **HeartMuLa fallback backend**: Stub a second music gen backend for HeartMuLa
      as a fallback option if ACE-Step doesn't work well.
- [ ] **MLX acceleration for ACE-Step**: Check if ACE-Step has an MLX-optimized
      variant for Apple Silicon. If so, prefer it over the default PyTorch path.
- [ ] **MPS device selection**: Ensure ACE-Step uses MPS (Metal) backend on macOS
      when available, rather than defaulting to CPU.

## 2026-04-08 (deferred from v1 — revisit after Stage 1)

- [ ] **Rank stage implementation**: RMS energy + CLAP similarity scoring.
- [ ] **Content stage — Ollama integration**: Description gen via local Ollama.
- [ ] **Content stage — Flux cover art**: Image gen via mlx-image or diffusers+MPS.
- [ ] **Post stage — YouTube upload**: YouTube Data API v3 with OAuth.
- [ ] **Audio→video conversion**: ffmpeg step to combine audio + cover → MP4.
- [ ] **X/Twitter posting**: post/twitter.py using X API v2.
- [ ] **Run history CLI**: `python pipeline.py --history` to list past runs.
- [ ] **Prompt templates**: Predefined genre/mood templates for quick generation.
