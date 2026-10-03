# lectr — Design Spec

**Date:** 2026-09-26
**Status:** Draft, awaiting review
**License:** GPL-3.0

## 1. Purpose

`lectr` is a command-line tool that turns a DRM-free e-book into an audiobook using a
**local** neural text-to-speech model — no cloud APIs. Anyone should be able to install it
with a package manager on macOS, Linux, or Windows.

### Success criteria

- `lectr convert book.epub` produces a listenable `.m4b` with correct chapter navigation,
  cover, and title/author metadata.
- Runs on an ordinary laptop CPU (no GPU required).
- An interrupted conversion resumes from the last completed chapter.
- Installable via `uv tool install lectr` (all OSes) and `brew install rgoshen/tap/lectr`
  (macOS, Linux).

### Decisions (agreed during brainstorming)

| Topic | Decision |
|---|---|
| Platforms | macOS (Apple Silicon, 14+), Linux (x86_64, aarch64), Windows (x86_64). Intel Macs and Windows on ARM are unsupported (see §12 and the DevOps spec) |
| Distribution | PyPI (installed with `uv tool install`) + own Homebrew tap. Windows via PyPI only. |
| Tooling | uv for everything (init, deps, run, build, publish). No pip in docs or workflows. |
| TTS | Kokoro-82M via `kokoro-onnx`, English only for v1. Synthesis isolated in one module; no engine plugin system. |
| License | GPL-3.0 (required by bundling the GPL-3.0 `mobi` library) |
| Input formats | EPUB, PDF, MOBI/AZW3, TXT, Markdown (DRM-free only) |
| Output | M4B (default) with chapters; `--format mp3` for one file per chapter |
| Long books | Split M4B between chapters when longer than `max_part_hours` (default 12) |
| Pipeline | Per-chapter WAV cache with resume, then assemble |
| Configuration | CLI flags > YAML config file > built-in defaults; `lectr setup` wizard writes the file |

### Out of scope for v1

DRM removal, OCR, non-English languages, GPU acceleration, parallel chapter synthesis,
PDF header/footer stripping, reading footnotes aloud, alternate TTS engines.

## 2. Architecture

Three stages, each testable in isolation:

```
read_book(path) ──► Book ──► synthesize chapters ──► cache/NNN.wav ──► assemble ──► .m4b / .mp3
   readers.py                 tts.py + pipeline.py                      audio.py
```

```
src/lectr/
  cli.py        argparse subcommands; builds Settings; dispatches
  config.py     Settings dataclass, YAML load/save, precedence, validation
  wizard.py     `lectr setup` interactive prompts
  readers.py    read_book() + one reader per format
  tts.py        model download/verification, Kokoro wrapper, voice list
  pipeline.py   chapter cache, resume, progress, cleanup
  audio.py      part planning, ffmpeg M4B/MP3 assembly, ffmpeg detection
```

Data model:

```python
@dataclass
class Chapter:
    title: str
    text: str

@dataclass
class Book:
    title: str
    author: str
    cover: bytes | None
    chapters: list[Chapter]
```

## 3. CLI and configuration

### Commands

```
lectr convert BOOK [flags]   Convert a book
lectr setup                  Interactive wizard; writes config.yaml
lectr config show            Print effective settings and the source of each (flag/file/default)
lectr voices                 List Kokoro voices
lectr chapters BOOK          List detected chapters and exit
lectr model download         Download and verify model files, then exit
```

### `convert` flags

| Flag | Config key | Default | Notes |
|---|---|---|---|
| `-o, --output PATH` | `output_dir` | next to BOOK | File path or directory |
| `--format {m4b,mp3}` | `format` | `m4b` | |
| `--max-part-hours N` | `max_part_hours` | `12` | Must be > 0 |
| `--bitrate KBPS` | `bitrate` | `64` | AAC or MP3 |
| `--voice NAME` | `voice` | `af_heart`* | Must exist in voices file |
| `--speed X` | `speed` | `1.0` | 0.5–2.0 |
| `--chapters RANGE` | — | all | e.g. `1-3,7` (1-based) |
| `--title`, `--author TEXT` | — | from book | Metadata overrides |
| `--cover PATH` | — | from book | |
| `--cache-dir PATH` | `cache_dir` | OS user cache dir | |
| `--no-resume` | — | resume on | Deletes this book's cache first |
| `--keep-cache` | `keep_cache` | `false` | |
| `--model-dir PATH` | `model_dir` | OS user data dir | |
| `--overwrite` | `overwrite` | `false` | Refuse to replace existing output otherwise |
| `--config PATH` | — | OS config dir | Alternate config file |
| `-q/--quiet`, `-v/--verbose` | — | normal | |
| `--version` | — | | Top-level |

\* Default voice to be confirmed present in `voices-v1.0.bin` during implementation.

### Precedence

CLI flag > config file > built-in default, resolved per key into a single `Settings` object.
`lectr config show` reports which source supplied each value.

### Config file

Location via `platformdirs.user_config_dir("lectr")`:
macOS `~/Library/Application Support/lectr/config.yaml`, Linux `~/.config/lectr/config.yaml`,
Windows `%APPDATA%\lectr\config.yaml`.

```yaml
voice: af_heart
speed: 1.0
format: m4b          # m4b | mp3
bitrate: 64
max_part_hours: 12
output_dir: null     # null = next to the book; e.g. ~/Audiobooks
cache_dir: null      # null = OS default
model_dir: null
keep_cache: false
overwrite: false
```

- Loaded with `yaml.safe_load` only.
- Unknown keys → error naming the key. Invalid values → error naming key, value, and allowed range.
- `~` is expanded in path values.

### Wizard (`lectr setup`)

- Asks each key in order using `input()`, showing the current value as `[default]`; Enter keeps it.
- Validates each answer with the same validators as the config loader; re-prompts on invalid input.
- Shows a summary and writes only after confirmation. Ctrl-C/EOF exits without writing.
- Offers to download the model at the end.
- `convert` never launches the wizard. With no config file it prints a one-line tip.

## 4. Readers

`read_book(path)` dispatches by lowercase extension:
`.epub`, `.pdf`, `.mobi`, `.azw3`, `.txt`, `.md`/`.markdown`. Anything else → error listing
supported formats.

| Format | Implementation | Chapters | Metadata / cover |
|---|---|---|---|
| EPUB | stdlib `zipfile`, `xml.etree.ElementTree`, `html.parser` | `META-INF/container.xml` → OPF spine order; titles from EPUB3 nav or NCX; fallback one chapter per spine item titled from first heading or "Chapter N" | OPF `dc:title`, `dc:creator`; cover from manifest (`properties="cover-image"` or `meta name="cover"`) |
| MOBI/AZW3 | `mobi` library unpacks to a temp dir; EPUB output → EPUB reader; HTML output → split on `<mbp:pagebreak>` / `h1`–`h2` | as EPUB | as EPUB when available |
| PDF | `pypdf` | Top-level outline entries mapped to page ranges; no outline → single chapter + warning | Document info title/author; no cover |
| TXT | stdlib | Lines matching `^(chapter\|part)\s+([0-9]+\|[ivxlcdm]+\|[a-z]+)\b` (case-insensitive); none → single chapter | Title from filename |
| Markdown | stdlib | `#`/`##` headings; inline markup, links, images, code fences stripped | First `#` or filename |

HTML → text: skip `script`, `style`, `head`; block elements produce paragraph breaks;
footnote reference markers (`<sup>` containing only digits/symbols, `epub:type="noteref"`) dropped.

Cleanup (all formats): normalize whitespace, join line-break hyphenation (`\w-\n\w`), drop
lines consisting only of a page number (PDF), drop chapters empty after cleanup. If zero
chapters remain → error.

Errors:
- EPUB with `META-INF/encryption.xml` referencing content, or MOBI the library reports as
  encrypted → "This book is DRM-protected; lectr only reads DRM-free files."
- PDF yielding no text → "No extractable text (scanned PDF?). OCR is not supported."
- Corrupt archive / parse failure → error naming file and format.

To verify during planning: `mobi` library API and output shape for AZW3.

## 5. TTS and model

### Model files

- Source: kokoro-onnx GitHub release `model-files-v1.1`: `kokoro-v1.0.onnx`, `voices-v1.0.bin`.
- Stored in `model_dir` (default `platformdirs.user_data_dir("lectr")/models`).
- SHA-256 of each file pinned in `tts.py`. Download with `urllib.request` to `<name>.part`,
  verify hash, then `os.replace` to the final name. Hash mismatch → delete and error.
- Percentage progress on stderr unless `--quiet`.
- Missing model and download fails → error suggesting `lectr model download` or `--model-dir`.

### Synthesis

- Load `Kokoro(model_path, voices_path)` once per run.
- Validate `voice` against the loaded voice list before any synthesis.
- Per chapter: `kokoro.create(text, voice=..., speed=..., lang="en-us")`. If kokoro-onnx does not
  split long input internally, lectr chunks at paragraph then sentence boundaries and
  concatenates results. (Verify during planning.)
- Output float32 samples at the model's sample rate (24 kHz) → converted to 16-bit PCM.
- 1.0 s of silence appended after each chapter.

To verify during planning: whether espeak-ng is bundled via a kokoro-onnx dependency or must be
installed system-wide (affects Windows install steps and Homebrew `depends_on`).

## 6. Pipeline, cache, resume

- Cache dir: `cache_dir/<key>/` where `key = sha256(book bytes + voice + speed + lectr version)[:16]`.
- Chapter `i` (1-based, zero-padded to 3 digits) written with stdlib `wave` to `NNN.wav.part`,
  then `os.replace` → `NNN.wav`. Only `NNN.wav` counts as complete; stray `.part` files are redone.
- On start: report `Resuming: X/Y chapters cached` when X > 0; skip cached chapters.
- `--chapters` limits which chapters are synthesized and assembled.
- `--no-resume` deletes `cache_dir/<key>/` first.
- After successful assembly delete `cache_dir/<key>/` unless `keep_cache`. On assembly failure
  keep it.
- Progress per chapter: `[15/32] The Crossing … 4m12s audio in 38s`.
- Ctrl-C → exit code 130 with "Progress saved; rerun the same command to resume."

## 7. Audio assembly

All ffmpeg/ffprobe calls use `subprocess.run([...])` with an argument list and no shell, so
titles and paths are never interpreted by a shell.

### Preflight

`shutil.which("ffmpeg")` checked at the start of `convert`, before synthesis. Missing → error with
`brew install ffmpeg` / `apt install ffmpeg` / `winget install ffmpeg`.

### Part planning (M4B)

- Chapter durations from WAV headers (`wave` module).
- Greedy in reading order: start a new part when adding the next chapter would exceed
  `max_part_hours`.
- A chapter longer than the limit is its own part, with a warning.
- One part → `<Title>.m4b`. N parts → `<Title> - Part i of N.m4b`.

### M4B (per part)

1. ffmpeg concat list of the part's WAVs.
2. FFMETADATA file: `title`, `artist`=author, `album`=title (+ ` - Part i of N`), and one
   `[CHAPTER]` per chapter with `TIMEBASE=1/1000`, `START`, `END`, `title`. Values escaped for
   `=`, `;`, `#`, `\`, newline.
3. Single ffmpeg run: AAC mono at `bitrate`, cover as attached picture when present, metadata
   mapped, `-movflags +faststart`, written to a temp name in the output dir, then renamed.

### MP3

- Output directory `<Title>/`; files `NN - <Chapter Title>.mp3`.
- Tags: title, artist, album, track `n/total`, cover.
- Filenames sanitized: `<>:"/\|?*` and control chars replaced, trailing dots/spaces trimmed,
  length capped.

### Output safety and errors

- Existing output and not `overwrite` → error before synthesis.
- ffmpeg non-zero exit → show last ~20 lines of stderr; cache retained.

To verify during planning: exact ffmpeg arguments for M4B cover attachment and MP3 ID3 cover
tagging (from ffmpeg docs).

## 8. Testing

TDD throughout. Default test run needs neither the model nor the network.

- **Unit:** readers (fixtures generated in tests: EPUB via `zipfile`, PDFs with/without outline,
  TXT, MD, DRM-flagged EPUB); config precedence/validation; wizard with patched `input()`;
  pipeline with fake TTS (resume, `.part` recovery, cache-key changes, cleanup); part planning
  edges; metadata escaping; filename sanitizing; model download with fake HTTP (hash mismatch,
  interruption).
- **MOBI:** committed DRM-free fixture only if a clearly licensed sample is available;
  otherwise stub the `mobi` library in unit tests.
- **Integration** (auto-skip without ffmpeg): assemble fake WAVs → M4B, verify with `ffprobe`
  (chapter count/times, tags, cover); multi-part split; MP3 tags.
- **E2E** (`-m e2e`, off by default): real Kokoro on a tiny TXT → playable M4B.
- **Gates:** `ruff check`, `ruff format --check`, `mypy --strict` on `src/`, coverage ≥ 80%.

## 9. Packaging, distribution, CI

> **Amended 2026-10-02:** CI, release, versioning, supply chain, and repository settings are
> specified in `docs/specs/2026-10-02-devops-design.md`, which replaces the PyPI, Homebrew
> workflow, CI, and Dependabot bullets below where they differ. In short: releases run on merge
> to `main` (not on pushed `v*` tags), CI covers four platforms on Python 3.13 only, and
> `requirements.lock` is a release asset rather than a committed file.

- `uv init --package` layout, `uv_build` backend, `[project.scripts] lectr = "lectr.cli:main"`,
  committed `uv.lock`, SemVer starting `0.1.0`.
- Runtime deps: `kokoro-onnx`, `mobi`, `pypdf`, `PyYAML`, `platformdirs`.
  Dev deps: `pytest`, `pytest-cov`, `ruff`, `mypy`. Versions pinned.
- `requires-python` set to the range for which `onnxruntime` ships wheels on all target
  platforms (verify during planning).
- **PyPI:** `uv build` + `uv publish` from GitHub Actions on `v*` tags using trusted publishing (no
  stored token). Users: `uv tool install lectr`.
- **Homebrew:** separate repo `rgoshen/homebrew-tap`, `Formula/lectr.rb` with `depends_on`
  `ffmpeg`, `python@3.x`, and `espeak-ng` if needed. `onnxruntime` has no sdist, so the formula
  installs published wheels into a private virtualenv; confirm the approved pattern from current
  Homebrew docs. Release workflow opens a PR bumping `url`/`sha256`; human merges.
- **CI (every PR):** matrix ubuntu/macos/windows × supported Pythons with `astral-sh/setup-uv`
  caching; ffmpeg installed per runner; ruff → format check → mypy → pytest+coverage, fail fast.
- Dependabot for Python deps and GitHub Actions.
- GitFlow (`main`, `develop`, `feature/*`, `bugfix/*`, `chore/*`, `release/*`, `hotfix/*`),
  Conventional Commits, `SUMMARY.md` entry per commit,
  `TODO.md` for planned work.

## 10. Documentation deliverables

From `~/.claude/templates/`: `README.md` (install via uv and Homebrew, external prerequisites per
OS, usage, config/wizard, troubleshooting), `CONTRIBUTING.md` (uv dev setup, tests, GitFlow,
commit rules), `LICENSE.md` (GPL-3.0 full text). Also `ARCHITECTURE.md` and ADRs:
Kokoro TTS; GPL-3.0 for MOBI support; chapter cache pipeline; M4B part splitting; YAML config
with flag precedence; release on merge to `main` (added 2026-10-02 by the DevOps spec).

## 11. Risks

| Risk | Mitigation |
|---|---|
| Homebrew formula with binary-only `onnxruntime` | Own tap; verify pattern early; PyPI remains the universal path |
| espeak-ng install friction on Windows | Verify bundling; document per-OS steps |
| Messy PDF text (headers, columns) | Documented limitation; `--chapters` to skip; improve with real samples later |
| Long synthesis time on slow CPUs | Resume cache; per-chapter progress; measure and document real throughput |
| Player limits on long M4B | 12 h default split, well under the ~49.7 h 32-bit sample limit at 24 kHz |
| Model hosting URL changes | Pinned URL + hash; `--model-dir` for manual placement |

## 12. Planning verification results (2026-09-26)

Resolved "to verify" items; these amend the sections above.

| Item | Finding | Effect |
|---|---|---|
| espeak-ng | `kokoro-onnx` 0.6.1 depends on `espeakng-loader`, which ships the espeak-ng library and data in its wheels (macOS, Linux, Windows) | No system espeak-ng install; not a Homebrew dependency |
| Long input | `kokoro-onnx` splits input into ≤510-phoneme batches at sentence/clause/word boundaries | lectr passes whole chapters; no own chunking |
| Default voice | `af_heart` present; voices file has 54 voices, 28 English (`af_`, `am_`, `bf_`, `bm_`) | Voice validation uses the 28 English voices; `b*` voices use `lang="en-gb"` |
| Model files | GitHub release `model-files-v1.1` digests: `kokoro-v1.0.onnx` sha256 `beb0d184…df3a`, `voices-v1.0.bin` sha256 `bca610b8…bf7d` (voices hash confirmed by download) | Pinned in `tts.py` |
| Python range | Revised 2026-09-27: the latest `kokoro-onnx`, 0.6.1, declares `>=3.10,<3.14`, so Python 3.14 is not supported (upstream issue #187). All other pinned packages support 3.13. `onnxruntime` 1.30 cp313 wheels exist for macOS arm64 (≥14), Linux x86_64/aarch64, Windows amd64/arm64 | `requires-python = ">=3.13,<3.14"` |
| Intel Macs | Revised 2026-09-27: `onnxruntime` 1.30 publishes no macOS x86_64 wheels; the last release with them is 1.23.2. 1.30 Apple Silicon wheels need macOS 14+ | Intel Macs unsupported; no fork to the older 1.23.2. Formula requires `arch: :arm64` and Sonoma on macOS |
| `mobi` API | `mobi.extract(path) -> (tempdir, path)`; path is `mobi8/*.epub` (KF8/AZW3), `mobi7/book.html` (old MOBI, with `content.opf` + `toc.ncx`), or a PDF; encrypted books raise an exception whose message contains "encrypted" | AZW3 reuses the EPUB reader; old MOBI splits `book.html` at the NCX `filepos` anchors |
| PDF encryption | Owner-password-only AES PDFs open with an empty password only when `cryptography` is installed | Dependency is `pypdf[crypto]`; user-password PDFs are rejected as protected |
| ffmpeg | M4B: concat WAVs + FFMETADATA + attached JPEG verified with ffprobe on ffmpeg 9.0.2 (chapters, `=`/`;` escaping, tags, cover); MP3: `libmp3lame` + ID3v2.3 tags + attached cover verified | Exact arguments in the plan |
| Homebrew | Homebrew's Python helper forces source builds (`--no-binary :all:`), which fails for wheel-only `onnxruntime` | Tap formula creates a venv with uv and installs pinned requirements (`requirements.lock`, attached to each GitHub Release since 2026-10-02); verified manually before first release |

Structural refinement: `readers.py` becomes a `readers/` package (one module per format) and shared errors live in `errors.py`, to keep files small.
