# Repository Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make GitHub enforce lectr's GitFlow rules (PR required, merge commits only, no force-push, immutable `v*` tags) and add the repo hygiene files, before v1 implementation starts.

**Architecture:** Rulesets are JSON files in `.github/rulesets/`, applied with `gh api` so the live settings are reviewable and re-appliable. Everything else is static GitHub configuration (Dependabot, CODEOWNERS, PR and issue templates) plus a CONTRIBUTING update. No application code.

**Tech Stack:** GitHub rulesets REST API, `gh` CLI, Dependabot, GitHub issue forms (YAML).

**Spec:** `docs/specs/2026-10-02-devops-design.md` §4.1 and §9.

## Global Constraints

- Branch `chore/repo-guardrails` from `develop`; PR into `develop` with a merge commit (`gh pr create --base develop`).
- Conventional Commits; prepend a `SUMMARY.md` entry before every commit (template in `docs/plans/2026-09-26-lectr-v1.md` Global Constraints); no `Co-Authored-By` or AI-generation trailers.
- Every `gh api` call that changes the live repository (POST/PUT/PATCH) changes shared settings: ask the maintainer and wait for an explicit yes before each one.
- `required_approving_review_count` is `0`: a sole maintainer cannot approve their own PR.
- Required status checks are **not** added here; CI does not exist yet, so required checks would block every PR. v1 plan Task 1b adds them.
- Validate YAML with `yaml.safe_load` and JSON with `json.load` (both via `uvx`/stdlib); never pip.

## Review Focus

1. The guardrails PR itself must still be mergeable after the branch ruleset is applied: it needs a PR (it is one) and a merge commit; no checks are required yet.
2. A `v*` tag ruleset must not block tag **creation**, because the release workflow creates the tag (`docs/specs/2026-10-02-devops-design.md` §4.4).
3. Dependabot PRs must target `develop`, not `main`.
4. Issue forms must ask for `lectr --version`, OS and architecture, and the input format, because platform support is narrow (macOS arm64 14+, Linux x86_64/aarch64, Windows x86_64).
5. CONTRIBUTING must stop claiming "at least one review is required"; for the maintainer's own PRs that is impossible.

---

### Task 1: Rulesets and repository settings

**Files:**
- Create: `.github/rulesets/branches.json`, `.github/rulesets/tags.json`
- Modify: `CONTRIBUTING.md` (new "Repository settings" section; §5 review wording)

**Interfaces:**
- Produces: ruleset names `protect-main-develop` and `protect-release-tags` (v1 plan Task 1b updates `protect-main-develop` by name).

- [ ] **Step 1: Branch**

```bash
cd /Users/richardgoshen/workspaces/python_workspace/lectr
git switch develop && git pull --ff-only origin develop
git switch -c chore/repo-guardrails
```

- [ ] **Step 2: Write `.github/rulesets/branches.json`**

```json
{
  "name": "protect-main-develop",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["refs/heads/main", "refs/heads/develop"], "exclude": [] }
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["merge"]
      }
    },
    { "type": "non_fast_forward" },
    { "type": "deletion" }
  ]
}
```

- [ ] **Step 3: Write `.github/rulesets/tags.json`**

```json
{
  "name": "protect-release-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["refs/tags/v*"], "exclude": [] }
  },
  "rules": [
    { "type": "update", "parameters": { "update_allows_fetch_and_merge": false } },
    { "type": "deletion" }
  ]
}
```

- [ ] **Step 4: Validate both files parse**

Run: `python3 -c "import json; [json.load(open(f)) for f in ('.github/rulesets/branches.json', '.github/rulesets/tags.json')]; print('ok')"`
Expected: `ok`

- [ ] **Step 5: Document the settings in `CONTRIBUTING.md`**

In "### 5. Pull requests", replace the line `- At least one review is required; no self-approval or auto-merge.` with:

```md
- Pull requests from contributors are reviewed by the maintainer before merging. GitHub
  enforces a pull request, passing CI checks, and a merge commit (no squash or rebase) on
  `main` and `develop`; there is no auto-merge.
```

Also in "### 2. Branch (GitFlow)", after the `bugfix/*` line inside the code block add
`git checkout -b chore/<short-description>      # tooling, docs, repo settings`, and change
"(slow, downloads ~300 MB)" to "(slow, downloads ~350 MB)".

Append before "## Reporting Issues":

````md
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

# Merge commits only
gh api --method PATCH repos/rgoshen/lectr -F allow_squash_merge=false -F allow_rebase_merge=false
```
````

- [ ] **Step 6: Commit**

SUMMARY.md entry — Change Type: Feature; Scope: repository settings; Summary: branch ruleset (PR required, merge commits only, no force-push or deletion on `main`/`develop`) and tag ruleset (`v*` cannot be moved or deleted) as JSON, with the `gh api` commands in CONTRIBUTING; CONTRIBUTING no longer claims a required review; Rationale: GitFlow rules were documented but unenforced; required checks wait for CI (v1 Task 1b); References: Spec docs/specs/2026-10-02-devops-design.md §4.1.

```bash
git add .github/rulesets CONTRIBUTING.md SUMMARY.md
git commit -m "chore(repo): add branch and tag rulesets"
```

---

### Task 2: Dependabot, CODEOWNERS, PR and issue templates

**Files:**
- Create: `.github/dependabot.yml`, `.github/CODEOWNERS`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/bug.yml`, `.github/ISSUE_TEMPLATE/feature.yml`, `.github/ISSUE_TEMPLATE/config.yml`

- [ ] **Step 1: Write `.github/dependabot.yml`**

```yaml
version: 2
updates:
  - package-ecosystem: uv
    directory: /
    target-branch: develop
    commit-message:
      prefix: "chore(deps)"  # Conventional Commits [R19]
    schedule:
      interval: monthly
    groups:
      python:
        patterns: ["*"]
  - package-ecosystem: github-actions
    directory: /
    target-branch: develop
    commit-message:
      prefix: "chore(deps)"  # Conventional Commits [R19]
    schedule:
      interval: monthly
    groups:
      actions:
        patterns: ["*"]
```

- [ ] **Step 2: Write `.github/CODEOWNERS`**

```
* @rgoshen
```

- [ ] **Step 3: Write `.github/pull_request_template.md`**

Adapted from `~/.claude/templates/PULL_REQUEST_TEMPLATE.md` to this project (no TLS or crypto-algorithm items, which do not apply to a local CLI):

```md
## Description

<!-- What changed and why. Link the issue, spec, or ADR. -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation
- [ ] Refactor
- [ ] Tests
- [ ] CI / tooling

## Testing

- [ ] `uv run pytest --cov=lectr` passes (coverage at least 80%)
- [ ] `uv run ruff check`, `uv run ruff format --check`, `uv run mypy src` are clean
- [ ] `uv run pytest -m e2e` run locally (only if synthesis or audio changed)

## Checklist

- [ ] `SUMMARY.md` entry prepended for each commit
- [ ] Conventional Commit messages, no co-author or AI-generation trailers
- [ ] New dependencies (if any) are GPL-3.0-compatible and pinned
- [ ] README / docs updated for user-visible changes

## Risks

<!-- What could break, on which platform, and how to roll back. -->

Closes #
```

- [ ] **Step 4: Write `.github/ISSUE_TEMPLATE/bug.yml`**

```yaml
name: Bug report
description: Something lectr did wrong
labels: [bug]
body:
  - type: input
    id: version
    attributes:
      label: lectr version
      description: Output of `lectr --version`
    validations:
      required: true
  - type: dropdown
    id: platform
    attributes:
      label: Platform
      options:
        - macOS (Apple Silicon)
        - Linux x86_64
        - Linux aarch64
        - Windows x86_64
        - Other (unsupported)
    validations:
      required: true
  - type: dropdown
    id: format
    attributes:
      label: Book format
      options: [EPUB, PDF, MOBI, AZW3, TXT, Markdown, Not format-specific]
    validations:
      required: true
  - type: textarea
    id: command
    attributes:
      label: Command you ran
      render: shell
    validations:
      required: true
  - type: textarea
    id: behavior
    attributes:
      label: Expected and actual behavior, with the error output
    validations:
      required: true
  - type: markdown
    attributes:
      value: Please do not attach copyrighted books; describe the file or share a small, freely licensed sample.
```

- [ ] **Step 5: Write `.github/ISSUE_TEMPLATE/feature.yml` and `config.yml`**

`feature.yml`:

```yaml
name: Feature request
description: Suggest an improvement
labels: [enhancement]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What are you trying to do, and what gets in the way?
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposal
    validations:
      required: false
```

`config.yml`:

```yaml
blank_issues_enabled: false
```

- [ ] **Step 6: Validate the YAML files**

Run: `uvx --with pyyaml==6.0.3 python -c "import yaml, glob; [yaml.safe_load(open(f)) for f in ['.github/dependabot.yml', *glob.glob('.github/ISSUE_TEMPLATE/*.yml')]]; print('ok')"`
Expected: `ok`

- [ ] **Step 7: Commit**

SUMMARY.md entry — Change Type: Feature; Scope: repository hygiene; Summary: monthly grouped Dependabot updates for uv and GitHub Actions targeting `develop`; CODEOWNERS; project PR template; bug and feature issue forms; Rationale: one Dependabot PR per ecosystem instead of one per package; issue forms capture the platform details that matter for lectr's narrow platform support; References: Spec docs/specs/2026-10-02-devops-design.md §4.1.

```bash
git add .github SUMMARY.md
git commit -m "chore(repo): add dependabot, codeowners, and templates"
```

---

### Task 3: Open the PR and apply the settings

- [ ] **Step 1: Push and open the PR (ask first)**

```bash
git push -u origin chore/repo-guardrails
gh pr create --base develop --title "chore(repo): add rulesets, dependabot, and templates" --body-file - <<'EOF'
Adds branch and tag rulesets as JSON, Dependabot (grouped, monthly, targeting develop),
CODEOWNERS, a PR template, and issue forms. Rulesets are applied separately with the
commands in CONTRIBUTING.md. Required status checks come with CI (v1 plan Task 1b).

Spec: docs/specs/2026-10-02-devops-design.md §4.1
EOF
```

- [ ] **Step 2: Apply rulesets and merge settings (ask first; each command changes the live repo)**

Run the three create/patch commands from the CONTRIBUTING "Repository settings" section.
Then verify:

```bash
gh api repos/rgoshen/lectr/rulesets --jq '.[].name'
gh api repos/rgoshen/lectr --jq '{squash: .allow_squash_merge, rebase: .allow_rebase_merge, merge: .allow_merge_commit}'
```

Expected: `protect-main-develop` and `protect-release-tags`; `{"squash":false,"rebase":false,"merge":true}`.

If the API rejects `allowed_merge_methods` on this personal repository, remove that key from
`branches.json`, re-run, and note it in SUMMARY.md: the repo-level PATCH above still limits
merges to merge commits.

- [ ] **Step 3: Merge the PR with a merge commit**

```bash
gh pr merge --merge --delete-branch
```

Expected: merged; the ruleset did not block it (no required checks yet).

- [ ] **Step 4: Confirm Dependabot picked up the config**

Whether Dependabot reads `dependabot.yml` from `develop` or only from the default branch
(`main`) is unverified. After merging, check:

```bash
gh api repos/rgoshen/lectr/dependabot/alerts --jq 'length' >/dev/null && echo "dependabot api ok"
```

and open the repository's **Insights → Dependency graph → Dependabot** tab. If it shows no
configuration, Dependabot only reads `main`; it will start after the first release merges
`develop` into `main`. Record which case applies in SUMMARY.md.
