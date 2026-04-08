# PROMPT.md — current project state
_Update this file as the project grows. It is a living document._

## What this project does
Local AI music generation pipeline:
generate music variants → rank top N → create post (description + cover image)
→ publish online. Fully local generation. API-only for posting.

## Current stack (best guess, agent may improve)
- Music gen: ACE-Step 1.5 or HeartMuLa (local)
- Image gen: Flux or similar (local)
- Description gen: Claude API (claude-sonnet-4-20250514)
- Posting: YouTube Data API v3, X API v2
- Python 3.11+

## Current structure
generate/ → rank/ → content/ → post/
Each stage is a self-contained folder. pipeline.py chains them.
Outputs written to outputs/{run_id}/ for crash safety and debuggability.

## Priorities right now
1. Get a working end-to-end pipeline, even if rough
2. Each stage should be independently testable
3. Scalability > perfection at this stage

## Known gaps / not started yet
- UI (possible later, don't design against it)
- Multi-platform posting (YouTube first)
- MLX / multiprocessing optimization (later)