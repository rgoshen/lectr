# Summary

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
