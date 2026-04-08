# Backlog

Non-blocking issues and future ideas. Newest at top.

## 2026-04-08

- [ ] **Audio→video conversion**: YouTube requires video. Need ffmpeg step to
      combine audio + cover image into MP4 before upload.
- [ ] **Learned ranker**: Replace RMS heuristic with a small quality model
      (e.g., CLAP similarity score between prompt and audio).
- [ ] **X/Twitter posting**: Add post/twitter.py using X API v2.
- [ ] **MLX acceleration**: Explore running ACE-Step / Flux on Apple Silicon
      via MLX for faster local inference.
- [ ] **Retry logic**: Add configurable retries for API calls (Claude, YouTube).
- [ ] **Run history CLI**: `python pipeline.py --history` to list past runs.
- [ ] **Prompt templates**: Predefined genre/mood templates for quick generation.
- [ ] **OAuth flow helper**: Script to generate YouTube OAuth tokens interactively.
