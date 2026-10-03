# Contributing to lectr

Thanks for your interest in contributing! This document outlines the process and expectations
for contributing to this project.

## Code of Conduct

Maintain a respectful, constructive attitude in issues, reviews, and discussions.

## How to Contribute

### 1. Discuss changes first

- For features or behavior changes, open an issue before starting work.
- Link related issues, ADRs (`docs/adr/`), or design specs (`docs/specs/`).

### 2. Branch (GitFlow)

- `main` — released code. `develop` — integration branch. Never commit directly to either.
- Branch from `develop`:

  ```bash
  git checkout develop
  git checkout -b feature/<short-description>   # new functionality
  git checkout -b bugfix/<short-description>    # non-production fixes
  git checkout -b chore/<short-description>      # tooling, docs, repo settings
  ```

- `hotfix/*` branches from `main` for urgent release fixes; `release/*` for release prep.

### 3. Test-driven development

- Follow red → green → refactor: write a failing test first, make it pass with the minimum
  code, then clean up.
- Unit tests are the bulk of the suite. They must not need the Kokoro model or network —
  use the fake TTS and generated fixtures in `tests/`.
- Integration tests that need `ffmpeg` skip automatically when it is not installed.
- Keep tests deterministic, independent, and free of implementation details.
- Coverage on changed code must be at least 80%.

### 4. Commit conventions

- [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`, `ci:`
  — e.g. `feat(readers): parse EPUB3 nav titles`.
- One small, atomic, test-passing change per commit.
- Before each commit, prepend an entry to `SUMMARY.md` describing what changed and why.
- Do not add co-author or AI-generation trailers.

### 5. Pull requests

- Target `develop`, and keep PRs small and self-contained.
- Run all checks locally first (see below); once CI lands, it runs them on Linux, macOS, and Windows.
- Describe the change, rationale, and risks, and link related issues and ADRs.
- Pull requests from contributors are reviewed by the maintainer before merging. GitHub
  enforces a pull request and a merge commit (no squash or rebase) on `main` and `develop`.
  Required CI checks are added when CI lands (v1 plan Task 1b). There is no auto-merge.

### 6. Documentation

- Update `README.md` for user-visible changes.
- Add an ADR in `docs/adr/` for significant technical decisions.

## Development Setup

1. Install [uv](https://docs.astral.sh/uv/) and `ffmpeg` (see README prerequisites).
2. Clone and sync:

   ```bash
   git clone <your-fork-url>
   cd lectr
   uv sync
   ```

3. Run the checks:

   ```bash
   uv run pytest --cov=lectr
   uv run ruff check
   uv run ruff format --check
   uv run mypy src
   ```

4. Optional end-to-end run with the real model (slow, downloads ~350 MB):

   ```bash
   uv run pytest -m e2e
   ```

Dependencies are managed only with uv (`uv add`, `uv add --dev`, `uv lock`). Commit
`uv.lock` with any dependency change. New dependencies must be license-compatible with
GPL-3.0.

## Repository settings (maintainer)

Branch and tag rules live in `.github/rulesets/` and are applied with the GitHub CLI. Apply
them once, and re-apply after editing a file:

```bash
# Create (first time)
gh api --method POST repos/rgoshen/lectr/rulesets --input .github/rulesets/branches.json
gh api --method POST repos/rgoshen/lectr/rulesets --input .github/rulesets/tags.json

# Update (after editing a file)
id=$(gh api repos/rgoshen/lectr/rulesets --jq '.[] | select(.name=="protect-main-develop") | .id')
gh api --method PUT "repos/rgoshen/lectr/rulesets/$id" --input .github/rulesets/branches.json
id=$(gh api repos/rgoshen/lectr/rulesets --jq '.[] | select(.name=="protect-release-tags") | .id')
gh api --method PUT "repos/rgoshen/lectr/rulesets/$id" --input .github/rulesets/tags.json

# Merge commits only
gh api --method PATCH repos/rgoshen/lectr -F allow_squash_merge=false -F allow_rebase_merge=false
```

Dependabot version updates target `develop`, but Dependabot security-update PRs may open
against the default branch `main` (unverified). If one does, close it and redo the bump on a
`chore/` or `bugfix/` branch from `develop`, because only `release/*` and `hotfix/*` merge
into `main`.

## Reporting Issues

- Search existing issues first.
- Include: OS, `lectr --version`, the command you ran, the input format, expected vs. actual
  behavior, and the error output.
- Do not attach copyrighted books; describe the file or share a small, freely licensed sample.

## License

By contributing, you agree that your contributions are licensed under the
[GPL-3.0](LICENSE.md).
