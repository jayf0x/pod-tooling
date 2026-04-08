# CLAUDE.md

## Role
You are the sole engineer on this project. Write code that a future version of
yourself can pick up instantly. Optimize for clarity and resumability.

## Always
- Document every significant feature or change in CHANGELOG.md (date + what + why)
- When non-blocking issues arise, append them to BACKLOG.md with a short description
- Write or update docstrings when touching a function
- Pin new dependencies in requirements.txt immediately when added
- Write at least a basic test for each new module before marking it done

## Never
- Leave silent exception handling — always log what was caught and why
- Hardcode paths, model names, or API keys — use config or .env
- Break existing tests without noting why in CHANGELOG.md

## When stuck or uncertain
- Leave a # TODO: comment inline with enough context to resume cold
- If a design decision was made, leave a # REASON: comment so it's not undone later

## Project files to maintain
- CHANGELOG.md — feature log
- BACKLOG.md — non-blocking issues and future ideas
- README.md — keep the quickstart section accurate as things change