# TODO

## [2026-09-26] Feature: lectr v1

**Objective:**
CLI that converts DRM-free EPUB, PDF, MOBI/AZW3, TXT, and Markdown books into chaptered M4B
(or per-chapter MP3) audiobooks with the local Kokoro-82M model; installable with uv and Homebrew.

**Approach:**
readers → per-chapter WAV cache (resume) → ffmpeg assembly. Flags > YAML config > defaults, with
a `lectr setup` wizard. Plan: docs/plans/2026-09-26-lectr-v1.md.

**Tests:**
Unit tests per module with generated fixtures and a fake synthesizer; ffmpeg integration tests
verified with ffprobe; one opt-in e2e test with the real model; ≥80% coverage.

**Risks & Tradeoffs:**
Homebrew formula for wheel-only onnxruntime; messy PDF text; long CPU synthesis times; Intel Macs
are unsupported (onnxruntime 1.30 has no Intel Mac build).
