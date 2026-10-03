# lectr DevOps design

- **Date:** 2026-10-02
- **Status:** Approved design, pending spec review (§10 records changes found while planning)
- **Amends:** `docs/specs/2026-09-26-lectr-design.md` §9 and `docs/plans/2026-09-26-lectr-v1.md`
  Tasks 15 and 16. Where this document and those disagree, this document wins.

## 1. Intent

lectr is a local CLI with one maintainer. Nothing is deployed and there are no servers, so
"DevOps" here means: every change is checked on every supported OS, the GitFlow rules in
`CLAUDE.md` are enforced by GitHub instead of by memory, and a release reaches PyPI and the
Homebrew tap only through the reviewed `release/*` or `hotfix/*` path, with provenance, an SBOM,
and a license gate.

**Success criteria**

1. No branch can reach `main` or `develop` without a PR, green required checks, and a merge commit.
2. Every PR runs lint, format, types, tests with the 80% coverage gate on macOS arm64,
   Linux x86_64, Linux aarch64, and Windows AMD64, plus a vulnerability audit, a license gate, and
   a workflow security lint.
3. A merge to `main` whose version is not yet tagged publishes exactly once: PyPI (with PEP 740
   attestations), a GitHub Release (tag, artifacts, `requirements.lock`, SBOM, build provenance),
   and a PR to `rgoshen/homebrew-tap`. A merge whose version is already tagged does nothing.
4. Every release job can be re-run after a partial failure without manual cleanup.
5. No new project dependencies. Tools run through `uvx` at exact versions.

**Out of scope (deliberately):** CodeQL, OpenSSF Scorecard, caching the model in e2e, e2e on
every PR or every OS, Homebrew bottles, required PR approvals (a sole maintainer cannot approve
their own PR), canary or blue-green releases, SLOs, and infrastructure as code. Revisit CodeQL
or Scorecard if a second maintainer joins.

## 2. Decisions taken during brainstorming

| Question | Decision | Why |
|---|---|---|
| When does DevOps land? | Repo guardrails now on `chore/repo-guardrails`; CI moves to right after v1 Task 1; release stays last | Tasks 2–14 get a cross-OS check on every push; release automation needs a package to release |
| Supply-chain depth | Lean: audit, license gate, workflow lint, SBOM, build provenance, PyPI attestations | Meets the global `CLAUDE.md` §6; GPL-3.0 compatibility is a hard constraint, so a license gate is not optional |
| `requirements.lock` | Generated in the release job and attached to the GitHub Release; not committed | A committed derived file would turn every Dependabot `uv.lock` PR red |
| Versioning | python-semantic-release (PSR), run locally on `release/*` and `hotfix/*` branches; never tags | Versions and `CHANGELOG.md` follow Conventional Commits; tagging is left to the release workflow |
| Release trigger | Push to `main`, skipped when the version is already tagged | Only reviewed release and hotfix merges reach `main`; no manual tag step; re-runs are harmless |

## 3. Verified facts (2026-10-02)

| Fact | Consequence | Source |
|---|---|---|
| Latest: `actions/checkout` v7.0.1, `actions/upload-artifact` v7.0.1, `actions/download-artifact` v8.0.1, `astral-sh/setup-uv` v10.2.0 (no `v10` moving tag), `actions/attest-build-provenance` v4.2.2 | The v1 plan's tags are current | [checkout](https://github.com/actions/checkout/releases), [upload-artifact](https://github.com/actions/upload-artifact/releases), [download-artifact](https://github.com/actions/download-artifact/releases), [setup-uv](https://github.com/astral-sh/setup-uv/releases), [attest-build-provenance](https://github.com/actions/attest-build-provenance#usage) |
| `uv publish` uploads attestation files found in `dist/` but does not create them; uv's guide adds `astral-sh/attest-action` (v0.0.6) | The v1 plan's publish job would ship no provenance | [uv package guide](https://github.com/astral-sh/uv/blob/main/docs/guides/package.md#uploading-attestations-with-your-package), [attest-action](https://github.com/astral-sh/attest-action/releases) |
| `uv audit` and `uv export --format cyclonedx1.5` are preview in uv 0.12.22 | Use stable `pip-audit` 2.10.1 and `cyclonedx-bom` 7.5.0 | [uv changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md), [pip-audit](https://pypi.org/project/pip-audit/), [cyclonedx-bom](https://pypi.org/project/cyclonedx-bom/) |
| `dependency-review-action` reading license data from `uv.lock` is unverified | License gate uses `pip-licenses` 5.5.5 instead | [dependency-review-action](https://github.com/actions/dependency-review-action#configuration-options), [pip-licenses](https://pypi.org/project/pip-licenses/) |
| Dependabot `package-ecosystem: uv` is GA | Keep it | [Dependabot ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories) |
| No runner image ships ffmpeg | Keep the per-OS install steps | [runner-images](https://github.com/actions/runner-images#available-images) |
| Homebrew allows network access in `def install` unless the formula opts out or defines `fetch` | The formula's `uv pip install` works; do not add a `fetch` method | [formula_installer.rb](https://github.com/Homebrew/brew/blob/master/Library/Homebrew/formula_installer.rb) |
| Rulesets on a free public repo support required checks, required PR, merge-method restriction, force-push blocking, and tag rules | Guardrails are rulesets, not classic branch protection | [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [Available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| PSR 10.7.0: `version --print`, `--no-commit --no-tag --no-push --no-vcs-release --skip-build --no-changelog`; release groups by branch regex; `allow_zero_version` defaults to false; uv guide re-locks and stages `uv.lock` before the PSR commit | Configure groups for `release/*` and `hotfix/*`; set `allow_zero_version = true` | [PSR commands](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/api/commands.rst), [multibranch](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/concepts/multibranch_releases.rst), [uv integration](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/configuration/configuration-guides/uv_integration.rst) |
| Repo state: public; no rulesets; squash and rebase merges allowed; no `pypi` environment; `rgoshen/homebrew-tap` does not exist; secret scanning, push protection, Dependabot security updates on | Guardrails and hand-off steps below | `gh api repos/rgoshen/lectr` (2026-10-02) |

## 4. Components

### 4.1 Repo guardrails (`chore/repo-guardrails`, now)

| File | Purpose |
|---|---|
| `.github/rulesets/branches.json` | Targets `main` and `develop`: pull request required (0 approvals), allowed merge method `merge` only, block force pushes, block deletion. `required_status_checks` is added in §4.2's final step |
| `.github/rulesets/tags.json` | Targets `refs/tags/v*`: block update and deletion. Creation stays open so the release job can create the tag |
| `.github/CODEOWNERS` | `* @rgoshen` (review requests only; no approvals required) |
| `.github/pull_request_template.md` | From `~/.claude/templates/PULL_REQUEST_TEMPLATE.md` |
| `.github/ISSUE_TEMPLATE/bug.yml`, `feature.yml` | Bug form: lectr version, OS and architecture, book format, command, output. Feature form: problem, proposal |
| `.github/dependabot.yml` | `uv` and `github-actions`, monthly, `target-branch: develop`, each with one group matching `*` |
| `CONTRIBUTING.md` | "Repository settings" section with the `gh api` commands that apply the rulesets and disable squash and rebase merges |

Rulesets live in the repo as JSON so the settings are reviewable and re-appliable; applying them
changes the live repo and needs the maintainer's explicit approval.

### 4.2 CI (`.github/workflows/ci.yml`; v1 plan Task 1b, moved from Task 15)

- Triggers: `pull_request`, `push` to `main` and `develop`, `workflow_call`.
- `permissions: contents: read`; `concurrency: {group: ci-${{ github.ref }}, cancel-in-progress: true}`;
  every job `timeout-minutes: 30`; every checkout `persist-credentials: false`.
- **`test`**, matrix `os: [ubuntu-latest, ubuntu-24.04-arm, macos-latest, windows-latest]`,
  `fail-fast: true`: setup-uv with cache and Python 3.13 → install ffmpeg (apt / brew / choco) →
  `uv sync --locked` → `ruff check` → `ruff format --check` → `mypy src` →
  `pytest --cov=lectr --cov-report=term-missing` (the `fail_under = 80` gate applies).
- **`supply-chain`**, `ubuntu-latest`:
  - Vulnerabilities: `uv export --no-dev --no-emit-project --locked --format requirements-txt`
    piped to `uvx pip-audit==2.10.1 --require-hashes --disable-pip`.
  - Licenses: `uv sync --locked --no-dev`, then `uvx pip-licenses==5.5.5` against the project
    interpreter with `--allow-only` set to the GPL-3.0-compatible list in §6.
  - Workflows: `uvx zizmor==1.30.1 .github/workflows`.
- Final step (after the first CI run on the draft v1 PR): add the reported check names to
  `branches.json` as required status checks and re-apply it.

### 4.3 Versioning (`[tool.semantic_release]` in `pyproject.toml`)

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
tag_format = "v{version}"
allow_zero_version = true
major_on_zero = false

[tool.semantic_release.branches.release]
match = "^(release|hotfix)/.+$"
prerelease = false
```

Also set `commit_message = "chore(release): v{version}"` (the default is not a Conventional
Commit) and `[tool.semantic_release.changelog.default_templates] mask_initial_release = false`
(the default first changelog says only "Initial Release"). PSR runs as
`uvx --from python-semantic-release==10.7.0 semantic-release`. It is a maintainer
tool, not a dependency. Release runbook (CONTRIBUTING):

1. From an up-to-date `develop`: `git switch -c release/next`, then
   `semantic-release version --print` → `X.Y.Z`. (PSR refuses non-release branches, so the
   version is computed on a branch that matches the release group.)
2. `git branch -m release/X.Y.Z`.
3. `semantic-release version --skip-build --no-commit --no-tag --no-changelog` (stamps pyproject).
4. `uv lock --upgrade-package lectr`; prepend the SUMMARY.md entry; `git add uv.lock SUMMARY.md`.
5. `semantic-release version --skip-build --no-tag --no-push --no-vcs-release` (writes
   `CHANGELOG.md`, commits everything staged).
6. Push, open PR `release/X.Y.Z` → `main`, merge with a merge commit, then merge `main` back into
   `develop`. Hotfixes: same steps from `main` on `hotfix/X.Y.Z`.

### 4.4 Release (`.github/workflows/release.yml`; replaces v1 plan Task 16's workflow)

Trigger: `push` to `main`. Top-level `permissions: {}`; each job requests only what it needs.
Every action is pinned by full commit SHA with the version in a trailing comment.

| Job | Needs | Does |
|---|---|---|
| `check` | — | `v=$(uv version --short)`; output `release=false` if `refs/tags/v$v` exists on origin, else `release=true` and `version=$v`. Every later job has `if: needs.check.outputs.release == 'true'` |
| `ci` | check | `uses: $/.github/workflows/ci.yml` |
| `build` | check | `uv build`; smoke test the artifact with `uvx --from dist/lectr-$v-py3-none-any.whl lectr voices`; extract the `CHANGELOG.md` section (fail if missing); export `requirements.lock`; generate `sbom.cdx.json` with `cyclonedx-bom==7.5.0` (`cyclonedx-py environment`); `actions/attest` build provenance over `dist/*` and the lock, and an SBOM attestation (`id-token: write`, `attestations: write`); upload artifacts |
| `e2e` | check | Real model on Linux: `uv sync --locked`, `pytest -m e2e -v` |
| `publish` | ci, build, e2e | Environment `pypi` (deployment branch `main`); `id-token: write`; download artifact; `astral-sh/attest-action` on `dist/*`; `uv publish --trusted-publishing always --check-url https://pypi.org/simple/ dist/*` |
| `github-release` | publish | `contents: write`; `gh release create v$v --target $GITHUB_SHA` with the `CHANGELOG.md` section for `$v` as notes, attaching `dist/*`, `requirements.lock`, `sbom.cdx.json`. Skip creation if the release exists (re-run safety) |
| `homebrew` | github-release | Environment `homebrew`; render the formula; clone the tap with `HOMEBREW_TAP_TOKEN`; `git push -f origin lectr-$v`; `gh pr view lectr-$v \|\| gh pr create` |

Values from contexts reach `run:` steps only through `env:`, never inline `${{ }}`.

### 4.5 Homebrew formula (`packaging/homebrew/lectr.rb.template`)

Changes from v1 plan Task 16:

- `resource "requirements"` URL becomes
  `https://github.com/rgoshen/lectr/releases/download/v{{VERSION}}/requirements.lock`.
- `install` sets `ENV["UV_CACHE_DIR"] = buildpath/"uv-cache"` and `ENV["UV_PYTHON_DOWNLOADS"] = "never"`.
- `test do` adds `system libexec/"bin/python", "-c", "import kokoro_onnx, onnxruntime"` so the
  native library is loaded once.
- Local verification gate (v1 Task 16 Step 2) also checks that `libexec/pyvenv.cfg` `home` points
  at `opt/python@3.13`, not a versioned Cellar path, so `brew upgrade python@3.13` does not break
  lectr.
- Comment citation for the Sonoma requirement changes from `[A2]` to `[V1]`.

## 5. Failure handling and rollback

| Failure | Behavior | Recovery |
|---|---|---|
| CI red on the merge commit | `publish` never runs | Fix via `hotfix/*`; same version re-runs because it is still untagged |
| `publish` fails | Nothing public changed | Re-run failed jobs |
| `github-release` or `homebrew` fails after PyPI publish | PyPI has the version; no tag yet, or tag without tap PR | "Re-run failed jobs" only. A full re-run rebuilds a different sdist and `--check-url` would reject it |
| Bad release shipped | — | Yank on pypi.org, close or revert the tap PR, ship `hotfix/X.Y.Z+1` |
| `HOMEBREW_TAP_TOKEN` expired | `homebrew` job fails | Rotate the token, re-run failed jobs. Calendar reminder at creation |

## 6. License allow-list

Runtime dependencies must be GPL-3.0-only compatible. Allowed (SPDX intent): MIT, BSD-2-Clause,
BSD-3-Clause, ISC, Apache-2.0, PSF-2.0, MPL-2.0, LGPL-2.1-or-later, LGPL-3.0-or-later,
GPL-2.0-or-later, GPL-3.0-only, GPL-3.0-or-later. The plan records the exact strings
`pip-licenses` reports for the current lock; an unknown string fails the gate and is resolved by
reading that package's license, never by widening the list blindly.

## 7. Open items resolved during planning (resolved; results in §10)

1. A dry run of the §4.3 runbook on a scratch repo to confirm the PSR commands and that the
   staged `uv.lock` and SUMMARY.md land in PSR's commit.
2. Exact `pip-licenses` flag to inspect the project venv rather than its own `uvx` environment,
   and the license strings it reports for the current runtime lock.
3. Whether `zizmor` findings on the v1 plan's workflow text need fixes beyond §4.2 and §4.4.
4. The CHANGELOG section extraction for release notes (PSR's changelog format).

## 8. Changes to existing documents (done 2026-10-02)

- v1 plan: Task 15 moves to directly after Task 1 and is replaced by §4.2; Task 16's workflow and
  formula are replaced by §4.4 and §4.5; the `requirements.lock` file and its sync check are
  removed from Tasks 1 and 15; the hand-off checklist becomes §9; changelog row A2 is marked
  superseded by V1; "121 tests" vs "101 tests" is reconciled; ADR-006 "Release on merge to main"
  is written in Task 16, next to the workflow it explains.
- Design spec §9: points to this document.
- README: Windows ARM and Intel Macs listed as unsupported.

## 9. Maintainer hand-off (each step needs explicit approval; not automated)

1. Apply `.github/rulesets/*.json` and disable squash and rebase merges (commands in CONTRIBUTING).
2. Create `rgoshen/homebrew-tap` with a README on `main`.
3. On pypi.org, add a **pending** trusted publisher: project `lectr`, repo `rgoshen/lectr`,
   workflow `release.yml`, environment `pypi`.
4. Create environments `pypi` and `homebrew`, each with deployment branch `main`.
5. Create the fine-grained `HOMEBREW_TAP_TOKEN` (contents and pull requests write on the tap only)
   as a secret of environment `homebrew` (deployment branch `main`), and set an expiry reminder.

## 10. Changes found while planning (2026-10-02)

Verified by dry runs (scratch project with the v1 `pyproject.toml`, uv 0.12.22) and by linting the
drafted workflows with zizmor 1.30.1. These amend §4–§9; the v1 plan has the exact code.

| Item | Change | Why |
|---|---|---|
| Action pinning | Every action in **both** workflows is pinned by commit SHA | zizmor's default policy fails on tag pins; with grouped monthly Dependabot PRs the extra churn is one PR a month |
| Reusable workflow call | `uses: $/.github/workflows/ci.yml` | zizmor `self-repository`; GitHub supports `$/` for reusable workflows since [2026-07-30](https://github.blog/changelog/2026-07-30-reference-same-repository-actions-with-self-repository-syntax/). actionlint 1.7.12 does not recognize it yet and is not a gate |
| Provenance | `actions/attest` v4.2.2 instead of the `attest-build-provenance` wrapper, plus a second `actions/attest` call with `sbom-path` for an SBOM attestation | The wrapper's README recommends `actions/attest` for new workflows |
| SBOM | `cyclonedx-py environment` on the build runner's runtime venv, not `cyclonedx-py requirements requirements.lock` | Environment mode records licenses and the dependency graph; requirements mode has neither. Trade-off: only the Linux x86_64 package set |
| License gate | Exact strings, `--ignore-packages espeakng-loader kokoro-onnx` | Both report `UNKNOWN`: kokoro-onnx ships an MIT LICENSE file without metadata; espeakng-loader has no metadata and bundles GPL-3.0-or-later espeak-ng |
| pip-audit input | Exported file, not stdin | `-r -` is rejected |
| PSR | First `--print` gives 0.1.0 from tags (pyproject version ignored); needs an `origin` remote | Dry run |
| Release concurrency | `concurrency: {group: release, cancel-in-progress: false}` | Two quick merges must not race or cancel a half-done release |
| Tap token | Environment `homebrew` secret instead of a repository secret | zizmor `secrets-outside-env`: only `main` can read it |
| Release notes | Extracted from `CHANGELOG.md` in `build` (fails before publishing if the section is missing) and passed as an artifact | A missing section must stop the release before PyPI, not after |
| Dependabot config | Whether Dependabot reads `dependabot.yml` from `develop` or only the default branch (`main`) is unverified | Guardrails plan Task 3 Step 4 checks it after merge |
