# Repository Guidelines

## Project Structure & Module Organization

`lectr` is currently design-first; implementation has not yet landed. Read `README.md` for the product overview and `CONTRIBUTING.md` for the human workflow. The binding technical sources are `docs/superpowers/specs/2026-09-26-lectr-design.md` and `docs/superpowers/plans/2026-09-26-lectr-v1.md`.

The planned Python package lives in `src/lectr/`. Keep format-specific parsing in `src/lectr/readers/`, orchestration in `pipeline.py`, synthesis in `tts.py`, and encoding in `audio.py`. Mirror modules with `tests/test_<module>.py`; place generated or freely licensed samples in `tests/fixtures/`. Record significant decisions in `docs/adr/`.

## Build, Test, and Development Commands

Use `uv` exclusively for Python and dependency management. Once the scaffold exists:

```bash
uv sync                                   # create the environment
uv run lectr --help                       # run the CLI from source
uv run pytest --cov=lectr                 # tests and 80% coverage gate
uv run ruff check                         # lint
uv run ruff format --check                # verify formatting
uv run mypy src                           # strict type checking
uv run pytest -m e2e                      # real model; slow and opt-in
```

Before the scaffold lands, use `git diff --check` to validate documentation changes.

## Coding Style & Naming Conventions

Target Python 3.13 with four-space indentation and complete type annotations. Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; and `UPPER_SNAKE_CASE` for constants. Ruff owns formatting and import order; mypy runs in strict mode. Prefer small, single-purpose functions and existing standard-library features. Add dependencies with `uv add` or `uv add --dev`, then commit `uv.lock`.

## Testing Guidelines

Follow red, green, refactor: write a failing pytest test before implementation. Name tests `test_<observable_behavior>`. Unit tests must avoid the network and Kokoro model; use fake TTS and generated fixtures. Mark ffmpeg-dependent coverage with `@requires_ffmpeg`. Keep changed-code coverage at or above 80%; reserve `e2e` for the critical real-model workflow.

## Commit & Pull Request Guidelines

Branch from `develop` using `feature/<topic>` or `bugfix/<topic>`; use `release/*` and `hotfix/*` only for release work. Follow Conventional Commits, for example `feat(readers): parse EPUB3 nav titles`. Keep commits atomic and passing, and prepend the required rationale entry to `SUMMARY.md` before each commit.

Target pull requests at `develop`. Include the change, rationale, risks, linked issue or ADR, and verification commands. Include CLI output for user-facing behavior changes. Require one peer review; do not self-approve, auto-merge, or add AI/co-author trailers.

## Security & Test Data

Accept only DRM-free inputs. Never commit copyrighted books, credentials, or downloaded model files. Invoke ffmpeg with argument lists, parse YAML with `yaml.safe_load`, verify model checksums, and keep dependencies GPL-3.0-compatible.
