# Blanc Beats

Local AI music generation pipeline: generate variants, rank the best, create a
post (description + cover art), and publish online.

## Quickstart

```bash
# 1. Clone and enter the project
cd blanc-beats

# 2. Create a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your API keys

# 5. Run the pipeline (stub mode — no local models needed)
python pipeline.py "chill lo-fi beat" --music-model stub --image-model stub --skip-post

# 6. Run tests
pytest tests/ -v
```

## Pipeline stages

```
generate/ → rank/ → content/ → post/
```

| Stage | What it does | Backend |
|-------|-------------|---------|
| **generate/** | Creates N music variants from a prompt | ACE-Step (stub fallback) |
| **rank/** | Scores & picks top N variants | RMS + duration heuristics |
| **content/** | Generates description + cover image | Claude API + Flux (stub fallback) |
| **post/** | Uploads to platform | YouTube Data API v3 (dry-run fallback) |

Each run writes outputs to `outputs/{run_id}/` with a `manifest.json` for
crash safety and debuggability.

## Configuration

All settings live in `.env` — see `.env.example` for the full list.

## Project structure

```
blanc-beats/
├── config.py          # Central config from .env
├── pipeline.py        # Main orchestrator + CLI
├── generate/          # Music generation
├── rank/              # Variant ranking
├── content/           # Description + cover art
├── post/              # Platform uploading
├── tests/             # Unit tests
├── outputs/           # Run outputs (gitignored)
├── CHANGELOG.md       # Feature log
└── BACKLOG.md         # Future ideas
```
