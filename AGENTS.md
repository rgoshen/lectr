# PROJECT KNOWLEDGE BASE

**Generated:** 2026-10-12
**Commit:** 46db0bf
**Branch:** develop

## OVERVIEW

lectr: a CLI that turns DRM-free EPUB/PDF/MOBI/AZW3/TXT/Markdown books into chaptered `.m4b` (or per-chapter `.mp3`) audiobooks using the local Kokoro-82M model via `kokoro-onnx`. Python 3.13, uv-only, GPL-3.0. **Design-first: no code has landed. The docs are the product until v1 Task 1 executes.**

## STRUCTURE

```
lectr/
├── docs/specs/      # binding designs; newer doc amends older on conflict
├── docs/plans/      # executable checkbox-task plans (exact code, gates)
├── .claude/skills/  # story + wave: the v1 agent implementation workflow
├── .github/         # rulesets JSON, dependabot, issue/PR templates — no CI yet
├── SUMMARY.md       # rationale log, newest first; prepend entry before every commit
└── README.md / CONTRIBUTING.md / CLAUDE.md / AGENTS.md / LICENSE.md
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Product + architecture design | `docs/specs/2026-09-26-lectr-design.md` | §12 "Planning verification results" amends earlier sections |
| DevOps design (CI, release, versioning) | `docs/specs/2026-10-02-devops-design.md` | Amends v1 plan Tasks 15/16; wins on conflict |
| v1 implementation plan | `docs/plans/2026-09-26-lectr-v1.md` | 16 TDD tasks with exact code; Global Constraints are binding |
| Repo guardrails plan | `docs/plans/2026-10-02-repo-guardrails.md` | Rulesets + hygiene files; executed via PR #6 |
| Implement one v1 story | `.claude/skills/story/SKILL.md` | One GitHub Project 5 issue → green PR into `feature/lectr-v1` |
| Run parallel stories | `.claude/skills/wave/SKILL.md` | One subagent per ready story; merge PRs one at a time |
| Why any change was made | `SUMMARY.md` | Rationale log; the commit discipline lives here |
| Apply / re-apply repo settings | `CONTRIBUTING.md` "Repository settings" | `gh api` ruleset commands; maintainer approval required |
| ADRs | `docs/adr/` | Referenced by README/AGENTS; not yet created |

## CODE MAP

No code exists; reference centrality unmeasured. Planned entry points — create these, don't invent alternatives:

| Symbol | Type | Location (planned) | Role |
|--------|------|--------------------|------|
| `lectr.cli:main(argv) -> int` | CLI entry | `src/lectr/cli.py` | `[project.scripts]` console script |
| `lectr.__version__` | constant | `src/lectr/__init__.py` | package version |
| `_READERS` | dispatch table | `src/lectr/readers/__init__.py` | lowercase extension → reader; shared cleanup after |
| `KokoroSynthesizer` | class | `src/lectr/tts.py` | the only code that needs the real model |

Stage flow: `readers/` → `Book(...)` → `pipeline.py`+`tts.py` (one WAV per chapter, cached) → `audio.py` (ffmpeg → `.m4b` parts / `.mp3`).

## CONVENTIONS

- uv only — never pip in code, docs, or workflows. Sole exception: `uv pip` inside the Homebrew formula.
- Python `>=3.13,<3.14` (kokoro-onnx 0.6.1 declares `<3.14`). Platforms: macOS arm64 14+, Linux x86_64/aarch64, Windows x86_64. Intel Macs unsupported (no onnxruntime wheels).
- All tool config in one `pyproject.toml` (planned): Ruff line-length 100, rules E/F/W/I/B/UP/SIM/RUF; mypy `--strict` (missing-import ignored for `mobi` only); pytest `testpaths=["tests"]`, `pythonpath=["tests"]`, `addopts = "-m 'not e2e' --strict-markers"`; coverage branch=true, `fail_under = 80`.
- TDD red → green → refactor. Unit tests never touch the network or the Kokoro model — fake TTS + generated fixtures. ffmpeg-dependent tests: `@requires_ffmpeg` from `tests/helpers.py` (directly importable via `pythonpath`). `e2e` marker = real model, slow, downloads ~350 MB.
- snake_case modules/functions, PascalCase classes, UPPER_SNAKE_CASE constants, complete type annotations, four-space indent. Deps: add with `uv add [--dev]`, pinned, commit `uv.lock`.
- GitFlow: `feature/*`, `bugfix/*`, `chore/*` branch from `develop`, merge back via PR (`gh pr create --base develop`); `release/*` and `hotfix/*` merge into `main` only, then tag and back-merge to `develop`. Merge commits only — plan steps verify ancestry with `git merge-base --is-ancestor`. Conventional Commits; prepend a `SUMMARY.md` entry before every commit.

## ANTI-PATTERNS (THIS PROJECT)

- Never commit or attach copyrighted books, credentials, or downloaded model files.
- DRM-protected inputs are rejected with the verbatim `DRM_MESSAGE`; DRM removal is out of scope.
- ffmpeg/ffprobe only via `subprocess.run` with an argument list — never a shell.
- YAML only via `yaml.safe_load`. Model downloads verify pinned SHA-256 before use.
- A local security hook rejects any file write containing the `str.format` method call written out literally (dot, `format`, open paren) — even in docs. Use f-strings.
- No literal en/em dashes or curly quotes in Python strings (ruff RUF001); build them with `chr(0x2013)` etc.
- No direct commits to `main`/`develop`; no co-author or AI-generation trailers; no self-approval or auto-merge.
- No new runtime dependencies without asking; all must be GPL-3.0-compatible (project is GPL-3.0-only because it bundles `mobi`). No silent pin-arounds of vulnerability findings.
- Any `gh api` call that changes live repository settings (POST/PUT/PATCH): ask the maintainer and wait for an explicit yes.
- v1 scope is fixed: no OCR, no non-English narration, no GPU/parallel synthesis, no PDF header/footer stripping, no spoken footnotes, no alternate TTS engines.

## UNIQUE STYLES

- Plans are executed task-by-task via `/story <issue>` (one story → green PR) or `/wave <n>` (parallel Sonnet subagents, one per ready story). Story worktrees live under `lectr-worktrees/` next to the main checkout, branched from `origin/feature/lectr-v1`.
- Gate fails mid-plan: fix the smallest thing and note it in `SUMMARY.md` — never redesign.
- Branch/tag rules live in `.github/rulesets/*.json` so settings are reviewable and re-appliable via `gh api`; they are already applied live (PR + merge-commit enforced on `main`/`develop`; `v*` tags immutable). Required CI checks arrive with v1 Task 1b. Required approving reviews: 0 (sole maintainer cannot self-approve).
- Dependabot targets `develop` (security-update PRs may still target `main` — retarget by hand).

## COMMANDS

No scaffold yet — documentation changes validate with `git diff --check`. Once Task 1 lands:

```bash
uv sync                                   # create .venv
uv run lectr --help                       # run the CLI from source
uv run pytest                             # unit + integration (e2e excluded via addopts)
uv run pytest --cov=lectr                 # coverage gate: fail_under = 80
uv run pytest -m e2e                      # real model; slow, downloads ~350 MB
uv run ruff check && uv run ruff format --check && uv run mypy src
```

All four gates (pytest, ruff check, ruff format --check, mypy) must pass before every commit. After adding imports: `uv run ruff check --fix && uv run ruff format`.

## NOTES

- Doc precedence: devops-design (2026-10-02) supersedes v1 plan Tasks 15/16; design spec §12 supersedes earlier spec sections; v1 plan Global Constraints bind every step.
- CI (`.github/workflows/ci.yml`, `release.yml`) is designed (devops-design §4.2/§4.4) but absent — lands with v1 Task 1b, then required checks get added to `branches.json` and re-applied.
- Parallel waves conflict on `SUMMARY.md` (every PR prepends): merge wave PRs one at a time; `/story` rebases an existing PR.
- espeak-ng may be unnecessary if `kokoro-onnx` bundles it — confirm before release.
