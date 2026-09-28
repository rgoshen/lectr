# Summary

## [2026-09-27 18:17] Commit Summary

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
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Global Constraints)

## [2026-09-27 18:16] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan, design spec, README (tech stack versions)

**Summary:**
Every component now targets its latest release with no older fallbacks. Python 3.14 only
(`>=3.14,<3.15`, classifiers, ruff `py314`, CI matrix, Homebrew `python@3.14`). Removed the
onnxruntime 1.23.2 fork for Intel Macs; Intel Macs are unsupported, and the formula requires
`arch: :arm64` on macOS. Spec §1 platforms, §12 rows, ADR-001, the TODO.md risks, the README
prerequisites are updated; plan changelog row V1 records the audit.

**Rationale:**
The user directed latest versions only and no downgrades. A version audit found every pinned
package and GitHub Action already latest; only Python (3.11-3.13) and the onnxruntime 1.23.2
Intel fork lagged. onnxruntime has no cp314 wheel for macOS
x86_64 (1.23.2 stops at cp313, and 1.30.0 cp314 has no Intel Mac build), so running 3.14 means
dropping Intel Macs. Verified by locking the plan's pyproject.toml (`requires-python ==3.14.*`) and syncing on
3.14.7: all 37 locked packages match their latest PyPI release.

**References:**
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Tasks 1, 14-16; changelog V1)
- Spec: docs/superpowers/specs/2026-09-26-lectr-design.md (§1, §12)
- https://pypi.org/project/onnxruntime/1.30.0/#files
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
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Task 1, Step 1)
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
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Task 1)

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
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Revision changelog A1–A20)
- Spec: docs/superpowers/specs/2026-09-26-lectr-design.md §12 (Intel Macs row)

## [2026-09-26 17:10] Commit Summary

**Change Type:** Docs
**Scope:** Implementation plan

**Summary:**
Finalize G1: chapters over 5,000 words are split into `Title (i/n)` segments (option A).

**Rationale:**
The user chose A over streaming synthesis (B) and rejecting long chapters (C). A bounds memory,
keeps resume granular, and adds navigation to chapterless books with the least code.

**References:**
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Revision changelog, G1)

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
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md (Revision changelog)

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
- Spec: docs/superpowers/specs/2026-09-26-lectr-design.md
- Plan: docs/superpowers/plans/2026-09-26-lectr-v1.md

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
- Spec: docs/superpowers/specs/2026-09-26-lectr-design.md

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
- Spec: docs/superpowers/specs/2026-09-26-lectr-design.md

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
- Spec: docs/superpowers/specs/2026-09-26-lectr-design.md
