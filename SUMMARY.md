# Summary

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
