# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

lectr is a CLI that turns DRM-free EPUB/PDF/MOBI/AZW3/TXT/Markdown books into chaptered `.m4b`
(or per-chapter `.mp3`) audiobooks using the local Kokoro-82M model via `kokoro-onnx`.

Implementation has not started. The source of truth is:

- `docs/specs/2026-09-26-lectr-design.md` — design. **§12 "Planning verification
  results" amends earlier sections** (e.g. no system espeak-ng, no own text chunking,
  `readers/` is a package, Python 3.13 only, because the latest kokoro-onnx (0.6.1) declares `<3.14`; Intel Macs are
  unsupported because onnxruntime 1.30 has no Intel Mac wheels). Every component is pinned to its latest release; do not add older fallbacks.
- `docs/plans/2026-09-26-lectr-v1.md` — 16 TDD tasks with exact code, pinned deps,
  and verified ffmpeg arguments. Its "Global Constraints" section is binding. Execute it
  task-by-task on `feature/lectr-v1`; if a gate fails, fix the smallest thing and note it in
  `SUMMARY.md` rather than redesigning.

## Commands

uv only — never pip in code, docs, or workflows (`uv add`, `uv add --dev`, `uv sync`, `uv lock`).

```bash
uv sync                                   # create .venv
uv run lectr --help                       # run from source
uv run pytest                             # unit + integration (e2e excluded via addopts)
uv run pytest tests/test_epub.py -v       # one module
uv run pytest tests/test_epub.py::test_name
uv run pytest --cov=lectr                 # coverage gate: fail_under = 80
uv run pytest -m e2e                      # real Kokoro model; slow, downloads ~350 MB
uv run ruff check && uv run ruff format --check && uv run mypy src   # mypy is --strict
```

All four gates (pytest, ruff check, ruff format --check, mypy) must pass before every commit.
After adding imports, run `uv run ruff check --fix && uv run ruff format` to normalize order.

## Architecture

Three stages, each testable alone:

```
read_book(path) -> Book(title, author, cover, chapters) -> pipeline: one WAV per chapter in cache -> audio: ffmpeg -> .m4b parts / .mp3
   readers/                                                pipeline.py + tts.py                         audio.py
```

- `readers/__init__.py` dispatches by lowercase extension via `_READERS`, then applies shared
  cleanup. MOBI/AZW3 are unpacked by the `mobi` library: KF8 output reuses the EPUB reader;
  old MOBI HTML is split at NCX `filepos` anchors. Books with no chapter markers are split into
  ~5,000-word segments.
- `pipeline.py` owns resume: cache dir key is `sha256(book bytes + voice + speed + lectr version)[:16]`;
  each chapter is written to `NNN.wav.part` and `os.replace`d to `NNN.wav`, so only complete
  files count. Cache is deleted after successful assembly (unless `keep_cache`) and kept on
  failure. Preflight checks (format, chapter range, ffmpeg, output collisions) run before the
  model loads.
- `audio.py` plans M4B parts greedily under `max_part_hours` (default 12) and writes chapters
  via an escaped FFMETADATA file.
- `tts.py` downloads model files to `<name>.part`, verifies pinned SHA-256, then renames.
  `KokoroSynthesizer` is the only code that needs the real model; everything else is tested
  with a fake TTS.
- `config.py` resolves each key as CLI flag > YAML file > default into one `Settings`, and
  records the source for `lectr config show`. `wizard.py` reuses the same validators.
- Errors derive from `lectr.errors.LectrError`; the DRM message is the constant `DRM_MESSAGE`
  and must stay verbatim.

## Rules that are easy to break

- ffmpeg/ffprobe only via `subprocess.run([...])` with an argument list — never a shell.
- YAML only through `yaml.safe_load`.
- No runtime dependencies beyond those pinned in the plan without asking; all must be
  GPL-3.0-compatible (the project is GPL-3.0-only because it bundles `mobi`).
- A local security hook rejects any file write containing the `str.format` method call
  written out literally (dot, `format`, open paren) — even in docs. Use f-strings.
- No literal en/em dashes or curly quotes in Python strings (ruff `RUF001`); build them with
  `chr(0x2013)` etc.
- Unit tests never touch the model or network. ffmpeg-dependent tests use `@requires_ffmpeg`
  from `tests/helpers.py` (importable directly because `pythonpath = ["tests"]`).

## Git workflow

GitFlow with tagged releases: `feature/*` and `bugfix/*` branch from `develop` and merge back
through a PR; only `release/*` and `hotfix/*` merge into `main` (then tag and merge back to
`develop`). The GitHub default branch is `main`, so pass `--base develop` to `gh pr create`.
Merge PRs with a merge commit, not squash or rebase — plan steps check ancestry with
`git merge-base --is-ancestor`.

Conventional Commits, no co-author or AI-generation trailers, and prepend a `SUMMARY.md`
entry (template in the plan's Global Constraints) before every commit.
