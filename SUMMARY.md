# Summary

## [2026-10-02 18:14] Commit Summary

**Change Type:** Feature
**Scope:** repository settings

**Summary:**
Branch ruleset (PR required, merge commits only, no force-push or deletion on `main`/`develop`)
and tag ruleset (`v*` cannot be moved or deleted) as JSON, with the `gh api` commands in
CONTRIBUTING. CONTRIBUTING no longer claims a required review.

**Rationale:**
GitFlow rules were documented but unenforced. Required checks wait for CI (v1 Task 1b).

**References:**
- Spec: docs/specs/2026-10-02-devops-design.md §4.1

## [2026-10-02 17:30] Commit Summary

**Change Type:** Docs
**Scope:** DevOps spec, v1 plan, guardrails plan, design spec

**Summary:**
Closed spec review findings R1–R22 on the DevOps design. Spec revised with inline `[Rxx]` tags
and a revision changelog; planning-time §10 kept. v1 plan: ci.yml no longer runs on push to
`main` (release.yml calls it) and uses `fail-fast: false`; release smoke test installs
`requirements.lock` plus the sdist like the Homebrew formula; `homebrew` job, environment, and
`HOMEBREW_TAP_TOKEN` removed in favour of a manual tap update in the runbook; one `psr version`
run with `build_command` replaces the three-run sequence. Guardrails plan: Dependabot
`commit-message.prefix: "chore(deps)"`. Design spec §9 note mentions the manual tap update.

**Rationale:**
Findings came from a spec-gap audit, an adversarial review, and a DevOps review checked against
GitHub, pip-audit, zizmor, and PSR sources. Maintainer chose the recommended options: sdist
smoke test, single PSR run, keep both PEP 740 and build provenance, manual tap updates (no
expiring token for one formula). IDs are R-prefixed because the plan already uses G1–G7. Both
plan workflows were extracted, YAML-parsed, and linted with zizmor 1.30.1 (no findings). The
single PSR run is not yet dry-run tested; Task 16 Step 6 requires it.

**References:**
- Spec: docs/specs/2026-10-02-devops-design.md (revision changelog R1–R22)
- Plans: docs/plans/2026-09-26-lectr-v1.md (Tasks 1, 1b, 16); docs/plans/2026-10-02-repo-guardrails.md (Task 3)

## [2026-10-02 17:22] Commit Summary

**Change Type:** Docs
**Scope:** v1 plan, guardrails plan

**Summary:**
New `docs/plans/2026-10-02-repo-guardrails.md` (rulesets as JSON, merge commits only, Dependabot
targeting `develop`, CODEOWNERS, PR template, issue forms, CONTRIBUTING settings section). v1
plan: Task 1 adds the semantic-release config and requires the guardrails plan first; new Task
1b (CI right after Task 1, 4-OS matrix with Linux aarch64, supply-chain job, required checks);
Task 15 becomes a pointer; Task 16 rewritten (release on merge to `main`, reusable CI, wheel
smoke test, attestations, SBOM, re-runnable tap PR, ADR-006, release runbook, hand-off list);
Global Constraints require green CI after each task; revision rows D1–D8; stale test count,
A2 row, file map, and a broken code fence in Task 14 fixed.

**Rationale:**
Every new command was dry-run in a scratch project (pip-audit, pip-licenses, cyclonedx-bom,
semantic-release) and both workflows were linted with zizmor before going into the plan, keeping
the plan's "every step was executed" standard. Tasks were renamed 1b instead of renumbered to
avoid breaking cross-references.

**References:**
- Spec: docs/specs/2026-10-02-devops-design.md
- Plans: docs/plans/2026-09-26-lectr-v1.md (Tasks 1, 1b, 14, 15, 16); docs/plans/2026-10-02-repo-guardrails.md

## [2026-10-02 17:20] Commit Summary

**Change Type:** Docs
**Scope:** design spec, DevOps spec

**Summary:**
Design spec: §1 platforms now name the supported architectures (Windows on ARM unsupported); §9
carries an amendment note pointing to the DevOps spec and lists all GitFlow branch types; §10
adds the release ADR; §12 notes that `requirements.lock` is a release asset. DevOps spec: new
§10 records what planning dry runs changed (SHA pins in both workflows per zizmor, `$/`
self-repository call, `actions/attest` for provenance and SBOM attestation, environment-mode
SBOM, exact license strings with two hand-reviewed `UNKNOWN` packages, release concurrency,
tap token in a `homebrew` environment); §4 tables aligned with it.

**Rationale:**
The DevOps spec supersedes design §9; leaving §9 unannotated would let an executor follow the
old tag-triggered design. Planning findings are recorded in the spec so spec and plan agree.

**References:**
- Spec: docs/specs/2026-10-02-devops-design.md

## [2026-10-02 16:43] Commit Summary

**Change Type:** Docs
**Scope:** DevOps design

**Summary:**
Added `docs/specs/2026-10-02-devops-design.md`: repo guardrails as ruleset JSON (merge-commit
only, PR required, `v*` tags immutable), CI moved to right after v1 Task 1 with a 4-OS matrix
(adds Linux aarch64) and a supply-chain job (pip-audit, pip-licenses GPL allow-list, zizmor),
python-semantic-release on `release/*` and `hotfix/*` branches, and a release workflow triggered
by merges to `main` that reuses CI, smoke-tests the wheel, attaches `requirements.lock` and a
CycloneDX SBOM to the GitHub Release, and publishes with build provenance and PEP 740
attestations.

**Rationale:**
An adversarial review of v1 plan Tasks 15–16 found that a release never waited for CI and that
a `v*` tag on any commit would publish; research found `uv publish` does not create attestations.
Releasing on merge to `main` (skipped when the version is already tagged) closes both and makes
re-runs harmless. `requirements.lock` moved to a release asset so Dependabot PRs stay green.
Alternatives considered: manual tag trigger with an ancestry guard; committed lock with manual
regeneration; CodeQL and Scorecard (out of scope for a single-maintainer CLI).

**References:**
- Spec: docs/specs/2026-10-02-devops-design.md
- Amends: docs/specs/2026-09-26-lectr-design.md §9; docs/plans/2026-09-26-lectr-v1.md Tasks 15–16

## [2026-10-01 17:40] Commit Summary

**Change Type:** Docs
**Scope:** docs/ layout

**Summary:**
Moved `docs/superpowers/plans/` and `docs/superpowers/specs/` to `docs/plans/` and
`docs/specs/`, removed the empty `docs/superpowers/`, and rewrote every path reference
(README, CONTRIBUTING, AGENTS.md, CLAUDE.md, SUMMARY.md, the plan).

**Rationale:**
The `superpowers` folder named the tool that generated the docs, not their content. Older
SUMMARY.md entries were rewritten too so their references still resolve. The plan's
`superpowers:` skill names are not paths and were left alone.

**References:**
- Spec: docs/specs/2026-09-26-lectr-design.md
- Plan: docs/plans/2026-09-26-lectr-v1.md

## [2026-09-27 18:35] Commit Summary

**Change Type:** Docs
**Scope:** CLAUDE.md

**Summary:**
Added CLAUDE.md for Claude Code: project status (spec and plan are the source of truth; spec
§12 amends earlier sections), uv/pytest/ruff/mypy commands including single-test runs, the
readers → pipeline/tts → audio architecture, project rules that are easy to break, and the
GitFlow workflow.

**Rationale:**
No code exists yet, so the file points at the spec and plan instead of listing a file tree
that Task 1 would make stale. It records non-obvious constraints (the local hook that rejects
the str.format call, ruff RUF001, merge commits only for PRs) that otherwise cost a failed attempt.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Global Constraints)

## [2026-09-27 18:34] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan, design spec, README (tech stack versions)

**Summary:**
Pinned the tech stack to its latest releases. Python is 3.13 only (`>=3.13,<3.14`, classifier,
ruff `py313`, CI matrix and lock-check runner, Homebrew `python@3.13`). Removed the onnxruntime
1.23.2 lock fork for Intel Macs, so onnxruntime is 1.30.0 on every platform. Intel Macs are
unsupported, and the Homebrew formula declares `depends_on arch: :arm64` on macOS. Updated spec
§1 platforms and §12, ADR-001, the Task 1 TODO risks, the README prerequisites, and plan
changelog row V1.

**Rationale:**
A version audit found every pinned package and GitHub Action already at its latest release.
Python 3.14 is newer, but the latest kokoro-onnx, 0.6.1, declares `requires-python <3.14`
(https://github.com/thewh1teagle/kokoro-onnx/blob/main/pyproject.toml#L9; support pending in
https://github.com/thewh1teagle/kokoro-onnx/issues/187), so 3.13 is the newest supported version.
The user decided to run the latest onnxruntime on every platform. onnxruntime 1.30.0 has no
macOS x86_64 wheels (https://pypi.org/project/onnxruntime/1.30.0/#files); the last release with
them is 1.23.2, so Intel Macs are dropped instead of pinned to it. Verified: the plan's
pyproject.toml locks to `==3.13.*`, syncs and imports on 3.13.8, and all 37 locked packages match
their latest PyPI release.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Tasks 1, 14-16; changelog V1)
- Spec: docs/specs/2026-09-26-lectr-design.md (§1, §12)
- https://docs.brew.sh/Formula-Cookbook (depends_on arch)

## [2026-09-27 16:10] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan (Task 1)

**Summary:**
Task 1 Step 1 now brings the design work into `develop` by merging PR #1, not by fast-forwarding
locally. It pulls `develop` and uses `git merge-base --is-ancestor` to confirm the design work
landed before creating `feature/lectr-v1`.

**Rationale:**
Review asked for an ancestry check before `git merge --ff-only`. The fast-forward worked today
(`develop` sat at the base of `feature/design-spec`), but PR #1 now targets `develop`, so a local
merge would bypass the PR and commit directly to `develop`. If GitHub merges the PR with a merge
commit, the design tip is still an ancestor of `develop`, so the check holds either way.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Task 1, Step 1)
- PR: rgoshen/lectr#1

## [2026-09-26 17:55] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan (Task 1)

**Summary:**
Created local `main` and `develop` branches. Task 1 now fast-forwards `develop` to the design
work before branching, and appends `*.partial` to the existing `.gitignore` instead of replacing it.

**Rationale:**
The user asked for a `main` branch and committed a comprehensive `.gitignore`. The old Task 1
steps would have failed on `git branch main` and overwritten that file.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Task 1)

## [2026-09-26 17:45] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan, design spec

**Summary:**
Fold the adversarial review (A1–A20) into the plan. Long chapters now split into equal-sized
parts titled "Part i of n" (A8, refining G1 as the user directed).

**Rationale:**
A separate Opus reviewer attacked the plan with real probes. Before release it would have broken
CI (nonexistent setup-uv tag), the Homebrew formula on Intel Macs and macOS 13, and the tap push.
It also found common real-world books handled badly: Gutenberg-style EPUBs, nested PDF outlines,
and lopsided part sizes. The user kept A's split rule (any chapter over ~5,000 words) instead of
the reviewer's split-only-structureless-books proposal, and asked for balanced part sizes.
Every fix was implemented and tested in scratch first, then ported into the plan. Rebuilding
from the plan alone gives 121 passing tests, 95% coverage, and clean ruff and mypy.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Revision changelog A1–A20)
- Spec: docs/specs/2026-09-26-lectr-design.md §12 (Intel Macs row)

## [2026-09-26 17:10] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan

**Summary:**
Finalize G1: chapters over 5,000 words are split into `Title (i/n)` segments (option A).

**Rationale:**
The user chose A over streaming synthesis (B) and rejecting long chapters (C). A bounds memory,
keeps resume granular, and adds navigation to chapterless books with the least code.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Revision changelog, G1)

## [2026-09-26 16:55] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan

**Summary:**
Revise the lectr v1 plan after a spec-gap audit: gaps G1–G7 closed. G1 (segmenting books that
have no chapter markers) is marked PROVISIONAL pending the user's decision.

**Rationale:**
The audit ran every code block in the plan in a scratch project instead of reviewing it by eye.
It found ruff and mypy gate failures (G2, G3) that would have stalled implementation, and a
memory/WAV-size failure for chapterless books (G1), confirmed in the kokoro-onnx source.
After the fixes: 107 tests pass, 95% coverage, and ruff and mypy are clean.

**References:**
- Plan: docs/plans/2026-09-26-lectr-v1.md (Revision changelog)

## [2026-09-26 16:20] Commit Summary

**Change Type:** Docs
**Scope:** Design spec, implementation plan

**Summary:**
Add the lectr v1 implementation plan (16 TDD tasks) and record the planning verification results
in spec §12.

**Rationale:**
Every to-verify item was checked against real artifacts instead of memory:
- kokoro-onnx 0.6.1 source: espeak-ng is bundled and long input is batched.
- voices-v1.0.bin: downloaded, hash verified, voices listed.
- GitHub release digests: model file hashes.
- onnxruntime wheel matrix: Python 3.11–3.13; no Intel-Mac wheels after 1.23.2.
- mobi: tested on Calibre-generated MOBI/AZW3 fixtures.
- pypdf: encrypted-PDF behavior (needs `cryptography`).
- ffmpeg 9.0.2: M4B/MP3 arguments checked with ffprobe.
- Homebrew: forces source builds, so the tap formula uses uv.

**References:**
- Spec: docs/specs/2026-09-26-lectr-design.md
- Plan: docs/plans/2026-09-26-lectr-v1.md

## [2026-09-26 15:40] Commit Summary

**Change Type:** Docs
**Scope:** README, design spec

**Summary:**
Replace the `<owner>` placeholder with `rgoshen`, so the Homebrew tap is `rgoshen/homebrew-tap`
and the install command is `brew install rgoshen/tap/lectr`.

**Rationale:**
The user confirmed `rgoshen` as the owning GitHub account. The `lectr` name is unclaimed on PyPI,
and neither `rgoshen/lectr` nor `rgoshen/homebrew-tap` exists yet.

**References:**
- Spec: docs/specs/2026-09-26-lectr-design.md

## [2026-09-26 15:35] Commit Summary

**Change Type:** Docs
**Scope:** Project docs

**Summary:**
Add README.md, CONTRIBUTING.md, and LICENSE.md (GPL-3.0).

**Rationale:**
Adapted from the README and CONTRIBUTING templates to the agreed design: uv and Homebrew
install paths, per-OS prerequisites, CLI usage, YAML config and wizard, GitFlow, TDD, and
Conventional Commits. LICENSE.md is the official GPL-3.0 Markdown text from gnu.org instead of
the MIT template, because bundling the GPL-3.0 `mobi` library requires GPL-3.0. The README marks
the project as unreleased, since the commands describe the planned v1.

**References:**
- Spec: docs/specs/2026-09-26-lectr-design.md

## [2026-09-26 15:05] Commit Summary

**Change Type:** Docs
**Scope:** Design

**Summary:**
Add the v1 design spec for lectr, a CLI that converts DRM-free e-books (EPUB, PDF, MOBI/AZW3,
TXT, Markdown) into M4B/MP3 audiobooks with the local Kokoro-82M TTS model.

**Rationale:**
Agreed during brainstorming: Kokoro for CPU-friendly quality (Piper sounds more synthetic,
XTTS-v2 is GPU-hungry and non-commercially licensed); GPL-3.0 so the `mobi` library can make
MOBI/AZW3 work without Calibre; per-chapter WAV cache so multi-hour jobs resume after
interruption and M4B parts can be planned from known durations (single-pass streaming and a
SQLite job store were rejected); 12-hour default part split to stay clear of player limits;
CLI flags over a YAML config written by a `lectr setup` wizard; distribution via PyPI with uv
plus a Homebrew tap.

**References:**
- Spec: docs/specs/2026-09-26-lectr-design.md
