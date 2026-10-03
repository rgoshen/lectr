# lectr DevOps design

- **Date:** 2026-10-02
- **Status:** Approved design; spec review gaps closed (§10 records changes found while planning)
- **Amends:** `docs/specs/2026-09-26-lectr-design.md` §9 and `docs/plans/2026-09-26-lectr-v1.md`
  Tasks 15 and 16. Where this document and those disagree, this document wins.

> **Revised 2026-10-02:** Spec-gap audit and DevOps review findings R1–R22 closed (R7, R8, R17,
> R18, R22 per the maintainer: recommended options). Fixes are tagged `[Rxx]` inline; see the
> revision changelog at the end.

## 1. Intent

lectr is a local CLI with one maintainer. Nothing is deployed and there are no servers, so
"DevOps" here means: every change is checked on every supported OS, the GitFlow rules in
`CLAUDE.md` are enforced by GitHub instead of by memory, and a release reaches PyPI only through
the reviewed `release/*` or `hotfix/*` path, with provenance, an SBOM, and a license gate.

**Success criteria**

1. No branch can reach `main` or `develop` without a PR, green required checks, and a merge commit.
2. Every PR runs lint, format, types, tests with the 80% coverage gate on macOS arm64,
   Linux x86_64, Linux aarch64, and Windows AMD64, plus a vulnerability audit, a license gate, and
   a workflow security lint.
3. A merge to `main` whose version is not yet tagged publishes exactly once: PyPI (with PEP 740
   attestations) and a GitHub Release (tag, artifacts, `requirements.lock`, SBOM, build
   provenance). A merge whose version is already tagged does nothing. The Homebrew tap is updated
   by hand from the release assets (§4.5) [R22].
4. Every release job can be re-run after a partial failure without manual cleanup.
5. No new project dependencies. Tools run through `uvx` at exact versions.

**Out of scope (deliberately):** CodeQL, OpenSSF Scorecard, caching the model in e2e, e2e on
every PR or every OS, Homebrew bottles, an automated tap PR [R22], required PR approvals (a sole
maintainer cannot approve their own PR), canary or blue-green releases, SLOs, and infrastructure
as code. Revisit CodeQL or Scorecard if a second maintainer joins, and tap automation if manual
updates become a burden.

## 2. Decisions taken during brainstorming and review

| Question | Decision | Why |
|---|---|---|
| When does DevOps land? | Repo guardrails now on `chore/repo-guardrails`; CI moves to right after v1 Task 1; release stays last | Tasks 2–14 get a cross-OS check on every push; release automation needs a package to release |
| Supply-chain depth | Lean: audit, license gate, workflow lint, SBOM, build provenance, PyPI attestations | Meets the global `CLAUDE.md` §6; GPL-3.0 compatibility is a hard constraint, so a license gate is not optional |
| `requirements.lock` | Generated in the release job and attached to the GitHub Release; not committed | A committed derived file would turn every Dependabot `uv.lock` PR red |
| Versioning | python-semantic-release (PSR), one local `version` run on `release/*` and `hotfix/*` branches; never tags [R18] | Versions and `CHANGELOG.md` follow Conventional Commits; tagging is left to the release workflow |
| Release trigger | Push to `main`, skipped when the version is already tagged | Only reviewed release and hotfix merges reach `main`; no manual tag step; re-runs are harmless |
| Signing [R17] | Keep both PEP 740 attestations and GitHub build provenance | PEP 740 covers PyPI files only; the formula downloads `requirements.lock` from the GitHub Release, which only build provenance lets anyone verify |
| Homebrew tap [R22] | Updated by hand with `render.sh` from the release assets; no release job, no tap token | One formula, a few releases a year; removes a job, an environment, a secret, and its expiry |

## 3. Verified facts (2026-10-02)

| Fact | Consequence | Source |
|---|---|---|
| Latest: `actions/checkout` v7.0.1, `actions/upload-artifact` v7.0.1, `actions/download-artifact` v8.0.1, `astral-sh/setup-uv` v10.2.0 (no `v10` moving tag), `actions/attest-build-provenance` v4.2.2 | The v1 plan's versions are current (pinned by SHA, §10) | [checkout](https://github.com/actions/checkout/releases), [upload-artifact](https://github.com/actions/upload-artifact/releases), [download-artifact](https://github.com/actions/download-artifact/releases), [setup-uv](https://github.com/astral-sh/setup-uv/releases), [attest-build-provenance](https://github.com/actions/attest-build-provenance#usage) |
| `uv publish` uploads attestation files found in `dist/` but does not create them; uv's guide adds `astral-sh/attest-action` (v0.0.6) | The v1 plan's publish job would ship no provenance | [uv package guide](https://github.com/astral-sh/uv/blob/main/docs/guides/package.md#uploading-attestations-with-your-package), [attest-action](https://github.com/astral-sh/attest-action/releases) |
| `uv audit` and `uv export --format cyclonedx1.5` are preview in uv 0.12.22 | Use stable `pip-audit` 2.10.1 and `cyclonedx-bom` 7.5.0 | [uv changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md), [pip-audit](https://pypi.org/project/pip-audit/), [cyclonedx-bom](https://pypi.org/project/cyclonedx-bom/) |
| pip-audit's `--require-hashes` and `--disable-pip` require `-r <file>`; without `-r` it audits its own environment | Export to a file and pass `-r` [R3] | [pip-audit `_cli.py`](https://github.com/pypa/pip-audit/blob/main/pip_audit/_cli.py) |
| A called workflow can keep or reduce the caller's token permissions, never raise them, and fails at parse time otherwise; its `github` context (`ref`, `workflow`) is the caller's | `ci` job grants `contents: read` [R1]; CI's concurrency group includes `github.workflow`, and ci.yml does not also run on push to `main` [R2] | [Reusing workflow configurations](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations), [runner#4151](https://github.com/actions/runner/issues/4151) |
| Dependabot targets the default branch unless `target-branch` is set; `target-branch` applies to version updates only | `target-branch: develop` [R4]; security-update PRs still target `main` and are retargeted by hand | [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference) |
| `dependency-review-action` reading license data from `uv.lock` is unverified | License gate uses `pip-licenses` 5.5.5 instead | [dependency-review-action](https://github.com/actions/dependency-review-action#configuration-options), [pip-licenses](https://pypi.org/project/pip-licenses/) |
| Dependabot `package-ecosystem: uv` is GA | Keep it | [Dependabot ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories) |
| No runner image ships ffmpeg | Keep the per-OS install steps, including release `e2e` [R5] | [runner-images](https://github.com/actions/runner-images#available-images) |
| Homebrew allows network access in `def install` unless the formula opts out or defines `fetch` | The formula's `uv pip install` works; do not add a `fetch` method | [formula_installer.rb](https://github.com/Homebrew/brew/blob/master/Library/Homebrew/formula_installer.rb) |
| Rulesets on a free public repo support required checks, required PR, merge-method restriction, force-push blocking, and tag rules | Guardrails are rulesets, not classic branch protection | [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [Available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| PSR 10.7.0: `version --print` (prints the current version when nothing is releasable); `--no-commit --no-tag --no-push --no-vcs-release --skip-build --no-changelog`; release groups by branch regex; `allow_zero_version` defaults to false; default `commit_message` is not a Conventional Commit; the uv guide re-locks with `build_command` | Groups for `release/*` and `hotfix/*`; `allow_zero_version = true`; `commit_message` and `build_command` set [R11, R18] | [PSR commands](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/api/commands.rst), [configuration](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/configuration/configuration.rst), [multibranch](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/concepts/multibranch_releases.rst), [uv integration](https://github.com/python-semantic-release/python-semantic-release/blob/master/docs/configuration/configuration-guides/uv_integration.rst) |
| Repo state: public; no rulesets; squash and rebase merges allowed; no `pypi` environment; `rgoshen/homebrew-tap` does not exist; `lectr` unclaimed on PyPI and Homebrew core; secret scanning, push protection, Dependabot security updates on | Guardrails and hand-off steps below | `gh api repos/rgoshen/lectr`, PyPI and formulae.brew.sh JSON APIs (2026-10-02) |

## 4. Components

### 4.1 Repo guardrails (`chore/repo-guardrails`, now)

| File | Purpose |
|---|---|
| `.github/rulesets/branches.json` | Targets `main` and `develop`: pull request required (0 approvals), allowed merge method `merge` only, block force pushes, block deletion. `required_status_checks` is added in §4.2's final step with `strict_required_status_checks_policy: false`, so a `main` → `develop` back-merge needs no update first [R15] |
| `.github/rulesets/tags.json` | Targets `refs/tags/v*`: block update and deletion. Creation stays open so the release job can create the tag. A wrong tag is fixed by temporarily disabling this ruleset (maintainer approval) [R15] |
| `.github/CODEOWNERS` | `* @rgoshen` (review requests only; no approvals required) |
| `.github/pull_request_template.md` | From `~/.claude/templates/PULL_REQUEST_TEMPLATE.md` |
| `.github/ISSUE_TEMPLATE/bug.yml`, `feature.yml` | Bug form: lectr version, OS and architecture, book format, command, output. Feature form: problem, proposal |
| `.github/dependabot.yml` | `uv` and `github-actions`, monthly, `target-branch: develop` [R4], `commit-message.prefix: "chore(deps)"` [R19], each with one group matching `*` |
| `CONTRIBUTING.md` | "Repository settings" section with the `gh api` commands that apply the rulesets and disable squash and rebase merges |

Rulesets live in the repo as JSON so the settings are reviewable and re-appliable; applying them
changes the live repo and needs the maintainer's explicit approval.

### 4.2 CI (`.github/workflows/ci.yml`; v1 plan Task 1b, moved from Task 15)

- Triggers: `pull_request`, `push` to `develop`, `workflow_call`. Not `push` to `main`:
  release.yml calls this workflow on every merge to `main`, and a second copy would only repeat
  it [R2].
- `permissions: contents: read`;
  `concurrency: {group: ci-${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true}`.
  When called, `github.workflow` is the caller's name, so a release run never shares a group
  with a standalone CI run [R2]. Every job has a timeout; every checkout `persist-credentials: false`.
- Every action is pinned by commit SHA (§10) [R10].
- **`test`**, matrix `os: [ubuntu-latest, ubuntu-24.04-arm, macos-latest, windows-latest]`,
  `fail-fast: false` so one OS failing does not hide the others [R21]: setup-uv with cache and
  Python 3.13 → install ffmpeg (apt / brew / choco) → `uv sync --locked` → `ruff check` →
  `ruff format --check` → `mypy src` → `pytest --cov=lectr --cov-report=term-missing`
  (the `fail_under = 80` gate applies).
- **`supply-chain`**, `ubuntu-latest`:
  - Vulnerabilities: `uv export --no-dev --no-emit-project --locked --format requirements-txt`
    to a file, then `uvx pip-audit==2.10.1 -r <file> --require-hashes --disable-pip` [R3].
  - Licenses: `uv sync --locked --no-dev`, then `uvx pip-licenses==5.5.5` against the project
    interpreter with `--allow-only` set to the exact strings for §6's list.
  - Workflows: `uvx zizmor==1.30.1 .github/workflows`; any finding fails the job. No token is
    needed: the planning run reported no findings without one [R20].
  - Known limit: both gates see the Linux resolution only; packages gated by macOS or Windows
    markers are checked by reading the Dependabot PR [R16].
- Final step (after the first CI run on the draft v1 PR): add the reported check names
  (`test (<os>)` ×4 and `supply-chain`; no `ci /` prefix on PR runs) to `branches.json` as
  required status checks and re-apply it.

### 4.3 Versioning (`[tool.semantic_release]` in `pyproject.toml`)

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
tag_format = "v{version}"
commit_message = "chore(release): v{version}"
allow_zero_version = true
major_on_zero = false
build_command = "uv lock --upgrade-package lectr && git add uv.lock"

[tool.semantic_release.branches.release]
match = "^(release|hotfix)/.+$"
prerelease = false

[tool.semantic_release.changelog.default_templates]
mask_initial_release = false
```

`commit_message` keeps PSR's commit a Conventional Commit (the default is not one) [R11];
`build_command` re-locks inside the PSR run, as in PSR's uv guide, so the version bump and
`uv.lock` land in one commit [R18]; `mask_initial_release = false` because the default first
changelog says only "Initial Release". PSR runs as
`uvx --from python-semantic-release==10.7.0 semantic-release`. It is a maintainer tool, not a
dependency. Release runbook (CONTRIBUTING) [R18]:

1. From an up-to-date `develop`, `git switch -c release/next`; for a hotfix, from `main`,
   `git switch -c hotfix/next` [R11]. (PSR refuses non-release branches, so the version is
   computed on a branch that matches the release group.)
2. `semantic-release version --print` → `X.Y.Z`. Stop if `git describe --tags --abbrev=0`
   prints `vX.Y.Z`: nothing is releasable [R11].
3. Prepend the SUMMARY.md entry and commit it as `docs(release): summary for vX.Y.Z`.
4. `semantic-release version --no-tag --no-push --no-vcs-release`: stamps `pyproject.toml`,
   runs `build_command`, writes `CHANGELOG.md`, commits as `chore(release): vX.Y.Z`.
5. Push, open PR `release/next` (or `hotfix/next`) → `main`, merge with a merge commit, then open
   and merge a `main` → `develop` PR.

### 4.4 Release (`.github/workflows/release.yml`; replaces v1 plan Task 16's workflow)

Trigger: `push` to `main`. Top-level `permissions: {}`; each job requests only what it needs.
`concurrency: {group: release, cancel-in-progress: false}` (§10) [R9]. Every action is pinned by
full commit SHA with the version in a trailing comment. Every job that reads the repo starts with
checkout (`persist-credentials: false`) and setup-uv [R5, R6].

| Job | Needs | Timeout | Does |
|---|---|---|---|
| `check` | — | 5 | `v=$(uv version --short)`; `git ls-remote --exit-code --tags origin "refs/tags/v$v"` (works on a shallow checkout) [R6]; output `release=false` if the tag exists, else `release=true`, and always `version=$v`. Every later job has `if: needs.check.outputs.release == 'true'` |
| `ci` | check | — | `uses: $/.github/workflows/ci.yml` with job `permissions: {contents: read}` [R1] |
| `build` | check | 15 | `uv build`; extract the `CHANGELOG.md` section (fail if missing); export `requirements.lock`; generate `sbom.cdx.json` with `cyclonedx-bom==7.5.0` (`cyclonedx-py environment`); smoke-test what Homebrew installs: a fresh venv, `uv pip install --require-hashes -r requirements.lock`, then `uv pip install --no-deps` the sdist, then `lectr --version`, `lectr voices`, and `import kokoro_onnx, onnxruntime` [R7]; `actions/attest` build provenance over `dist/*` and the lock, and an SBOM attestation (`id-token: write`, `attestations: write`); upload artifacts |
| `e2e` | check | 30 | `sudo apt-get install -y ffmpeg` [R5]; `uv sync --locked`; `uv run pytest -m e2e -v` |
| `publish` | ci, build, e2e | 15 | Environment `pypi` (deployment branch `main`); `id-token: write`; download artifact; `astral-sh/attest-action` on `dist/*`; `uv publish --trusted-publishing always --check-url https://pypi.org/simple/ dist/*` |
| `github-release` | check, publish | 10 | `contents: write`; download the uploaded artifacts, never re-export [R13]; if the release exists, `gh release upload … --clobber` so a half-finished upload completes on re-run [R14]; otherwise `gh release create v$v --target $GITHUB_SHA` with the extracted notes, attaching `dist/*`, `requirements.lock`, `sbom.cdx.json` |

Values from contexts reach `run:` steps only through `env:`, never inline `${{ }}`. There is no
`homebrew` job [R22].

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

Tap update, by hand after each GitHub Release (CONTRIBUTING) [R22]: `gh release download` the
sdist and `requirements.lock`, render with `packaging/homebrew/render.sh`, commit to a
`lectr-X.Y.Z` branch of `rgoshen/homebrew-tap`, open and merge the PR, then confirm with
`brew install rgoshen/tap/lectr && brew test lectr`. The checksums come from the released,
attested assets [R13].

## 5. Failure handling and rollback

| Failure | Behavior | Recovery |
|---|---|---|
| CI red on the merge commit | `publish` never runs; no tag | Fix via `hotfix/next`. PSR computes from the last *tag*, so the hotfix may produce the same `X.Y.Z` again; the Task 16 dry run checks that `CHANGELOG.md` keeps one section for it [R8] |
| `publish` fails | Nothing public changed | Re-run failed jobs |
| `github-release` fails after PyPI publish | PyPI has the version; no tag yet, so `check` still says `release=true` | **Re-run failed jobs only.** A full re-run rebuilds `dist/`, and PyPI never accepts a different file under a filename it already has [R8] |
| Bad release shipped | — | Yank on pypi.org, revert the tap formula, ship a hotfix with the next patch version |
| Wrong tag created | Tag ruleset blocks deletion | Temporarily disable `tags.json` (maintainer approval), delete the tag, re-enable [R15] |

## 6. License allow-list

Runtime dependencies must be GPL-3.0-only compatible. Allowed (SPDX intent): MIT, BSD-2-Clause,
BSD-3-Clause, ISC, Apache-2.0, PSF-2.0, MPL-2.0, LGPL-2.1-or-later, LGPL-3.0-or-later,
GPL-2.0-or-later, GPL-3.0-only, GPL-3.0-or-later. The plan records the exact strings
`pip-licenses` reports for the current lock; an unknown string fails the gate and is resolved by
reading that package's license, never by widening the list blindly.

## 7. Open items resolved during planning (resolved; results in §10)

1. A dry run of the §4.3 runbook on a scratch repo to confirm the PSR commands. **Re-run needed:**
   the single `version` run with `build_command` [R18] replaced the dry-run-verified three-run
   sequence; v1 plan Task 16 Step 6 repeats the dry run, including the hotfix case in §5 [R8].
2. Exact `pip-licenses` flag to inspect the project venv rather than its own `uvx` environment,
   and the license strings it reports for the current runtime lock.
3. Whether `zizmor` findings on the v1 plan's workflow text need fixes beyond §4.2 and §4.4.
4. The CHANGELOG section extraction for release notes (PSR's changelog format).

## 8. Changes to existing documents (done 2026-10-02)

- v1 plan: Task 15 moves to directly after Task 1 and is replaced by §4.2; Task 16's workflow and
  formula are replaced by §4.4 and §4.5, without the `homebrew` job [R22]; the `requirements.lock`
  file and its sync check are removed from Tasks 1 and 15; the hand-off checklist becomes §9;
  changelog row A2 is marked superseded by V1; ADR-006 "Release on merge to main" is written in
  Task 16, next to the workflow it explains. (No "101 tests" figure exists in the repo, so there
  was nothing to reconcile [R12].)
- Design spec §9: points to this document.
- README: Windows ARM and Intel Macs listed as unsupported.

## 9. Maintainer hand-off (each step needs explicit approval; not automated)

1. Apply `.github/rulesets/*.json` and disable squash and rebase merges (commands in CONTRIBUTING).
2. Create `rgoshen/homebrew-tap` with a README on `main`.
3. On pypi.org, add a **pending** trusted publisher: project `lectr`, repo `rgoshen/lectr`,
   workflow `release.yml`, environment `pypi`.
4. Create environment `pypi` with deployment branch `main`. (No `homebrew` environment or tap
   token [R22].)

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
| Tap token | ~~Environment `homebrew` secret instead of a repository secret~~ Superseded: no tap token at all [R22] | zizmor `secrets-outside-env` no longer applies |
| Release notes | Extracted from `CHANGELOG.md` in `build` (fails before publishing if the section is missing) and passed as an artifact | A missing section must stop the release before PyPI, not after |
| Dependabot config | Whether Dependabot reads `dependabot.yml` from `develop` or only the default branch (`main`) is unverified | Guardrails plan Task 3 Step 4 checks it after merge |

## Revision changelog

Findings from the spec-gap audit (`spec-gap-auditor`), an adversarial review
(`architecture-critic`), and a DevOps review checked against GitHub, pip-audit, zizmor, and PSR
sources (`devops-engineer`). "Plan" means it was already fixed in the 2026-10-02 planning commits.

| ID | Summary | Where closed |
|----|---------|--------------|
| R1 | Called CI workflow could not get `contents: read` under `permissions: {}` | Plan; §3, §4.4 |
| R2 | CI ran twice on merges to `main` and could share a concurrency group with the release's CI | Plan (group); ci.yml push trigger now `develop` only; §3, §4.2 |
| R3 | pip-audit read stdin, which it does not support | Plan; §3, §4.2 |
| R4 | Dependabot PRs would target `main` | Plan; §3, §4.1 |
| R5 | Release `e2e` lacked setup and ffmpeg | Plan; §4.4 |
| R6 | `check` lacked checkout; tag test needs `ls-remote` | Plan; §4.4 |
| R7 | Smoke test used a `uvx` wheel (fresh PyPI resolution) instead of what Homebrew installs | Plan Task 16 Step 3; §4.4 |
| R8 | Failure table gave the wrong reason a full re-run fails, and assumed a hotfix keeps the version | §5, §7 |
| R9 | Release workflow had no concurrency group or timeouts | Plan; §4.4 |
| R10 | Tag-pinned ci.yml would fail its own zizmor step | Plan; §4.2 |
| R11 | PSR commit message, nothing-to-release stop, `hotfix/next` | Plan (message); plan Task 16 Step 6; §4.3 |
| R12 | §8 cited a "101 tests" figure that does not exist | §8 |
| R13 | Tap checksums must come from the released artifacts, not a re-export | Plan; §4.4, §4.5 |
| R14 | Partial GitHub Release upload was not completed on re-run | Plan; §4.4 |
| R15 | Non-strict required checks; wrong-tag recovery | Plan (non-strict); §4.1, §5 |
| R16 | License and audit gates see Linux only | §4.2 |
| R17 | Keep both PEP 740 and build provenance | §2 |
| R18 | One PSR `version` run with `build_command`; no branch rename | Plan Task 1 `pyproject.toml`, Task 16 Step 6; §2, §4.3, §7 |
| R19 | Dependabot `commit-message.prefix: "chore(deps)"` | Guardrails plan Task 3 Step 1; §4.1 |
| R20 | zizmor token question: none needed, findings fail the job | §4.2 |
| R21 | CI matrix `fail-fast: false` | Plan Task 1b; §4.2 |
| R22 | Homebrew tap updated by hand; `homebrew` job, environment, token, and hand-off step removed | Plan Task 16 Steps 3, 5, 6, 8, 9; §1, §2, §4.4, §4.5, §9, §10 |
