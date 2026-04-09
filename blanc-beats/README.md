# Blanc Beats

Fully local AI music generation pipeline: generate variants, rank the best,
create a post (description + cover art), and publish online.

**Current focus: Stage 1** — get real audio out of a real local model.

## Quickstart

```bash
# 1. Clone and enter the project
cd blanc-beats

# 2. Create a virtual environment (Python 3.11+ required)
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env

# 5. Download model weights (~3.5 GB)
python setup_models.py

# 6. Generate music
python pipeline.py "chill lo-fi beat" --only generate

# 7. Run in stub mode (no models needed, for testing)
python pipeline.py "chill lo-fi beat" --only generate --music-model stub

# 8. Run tests
pytest tests/ -v
```

## Model setup

Models are downloaded to `models/` (gitignored) via `setup_models.py`.

| Model | HuggingFace ID | Size | Purpose |
|-------|---------------|------|---------|
| ACE-Step 1.5 | `ACE-Step/ACE-Step-v1-5` | ~3.5 GB | Text-to-music generation |

```bash
# Download all models
python setup_models.py

# Download a specific model
python setup_models.py ace-step
```

## Pipeline stages

```
generate/ → rank/ → content/ → post/
```

| Stage | Status | What it does |
|-------|--------|-------------|
| **generate/** | Active | Creates N music variants from a prompt (ACE-Step 1.5) |
| **rank/** | Stub | Will score & pick top N variants |
| **content/** | Stub | Will generate description (Ollama) + cover image (Flux) |
| **post/** | Stub | Will upload to YouTube / X |

## CLI usage

```bash
# Run a single stage
python pipeline.py "chill lo-fi beat" --only generate

# Run full pipeline (only generate is real; rest are stubs)
python pipeline.py "chill lo-fi beat"

# Resume from a previous run
python pipeline.py "chill lo-fi beat" --only generate --run-id 20260408_143052_a1b2c3

# Override model
python pipeline.py "chill lo-fi beat" --only generate --music-model stub
```

Each run writes outputs to `outputs/{run_id}/` with a `manifest.json`.

## Configuration

All settings live in `.env` — see `.env.example` for the full list.

## Project structure

```
blanc-beats/
├── config.py          # Central config from .env
├── pipeline.py        # Main orchestrator + CLI
├── setup_models.py    # Model weight downloader
├── generate/          # Music generation (active)
├── rank/              # Variant ranking (stub)
├── content/           # Description + cover art (stub)
├── post/              # Platform uploading (stub)
├── tests/             # Unit tests
├── models/            # Downloaded model weights (gitignored)
├── outputs/           # Run outputs (gitignored)
├── logs/              # Pipeline logs (gitignored)
├── CHANGELOG.md       # Feature log
└── BACKLOG.md         # Future ideas
```
