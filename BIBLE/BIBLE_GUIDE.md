# BIBLE_GUIDE.md — Process & Rules

## Canonical Source of Truth
- `BIBLE/master_bible.md` is the single canonical bible. Update it **only** via Pull Requests.
- Each chapter lives under `BIBLE/books/book0N/chNN.md` with a paired `chNN.meta.json` for machine checks.

## Branching Model
- `main` = published truth.
- `book1/chNN-<slug>` = a chapter branch (e.g., `book1/ch01-exposure`).
- Open a PR for every chapter. The CI checks must pass.

## Per-Chapter Checklist
- Update or add `chNN.meta.json` with: timestamp (UTC ISO), POV(s), locations, characters present, power usage, and anchor changes.
- If you introduce new characters/locations/terms, update `BIBLE/canon.json` and `BIBLE/master_bible.md` in the same PR.
- Ensure the timeline doesn’t conflict with existing chapters.

## Release/Tagging
- Tag `v1.0.0` when Book 1 is locked, `v2.0.0` for Book 2, etc.
- Use `CHANGELOG.md` to record notable continuity edits.

See `BIBLE/tools/validators.py` and `continuity_checker.py` for the automated rules.
