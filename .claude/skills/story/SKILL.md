---
name: story
description: Work one lectr v1 story issue from blocker check to a green PR into feature/lectr-v1.
argument-hint: <issue-number>
disable-model-invocation: true
---

# Story #$ARGUMENTS

Take issue #$ARGUMENTS of `rgoshen/lectr` (GitHub Project 5) to a green PR, then stop. The issue body is the brief: plan link and scoped steps, branch rule, needs, shared files, and its "Done when" list. The linked task in `docs/plans/2026-09-26-lectr-v1.md` is the source of truth for code, tests, commit messages, and `SUMMARY.md` content; its Global Constraints bind every step.

The shell returns to the main checkout after every command, so prefix each command with `cd <worktree> &&` to keep commits on the story's branch.

## 1. Gate

Run `gh issue view $ARGUMENTS --json title,body,state,labels,blockedBy`. Stop and report the reason when the issue is closed, is labelled `epic`, says "Maintainer only", or has any `blockedBy` issue still `OPEN` (name each one).

Done when: the issue is an open story with every blocker `CLOSED`.

## 2. Workspace

Follow the brief's "How to work it":

- **Direct** (Tasks 1 and 1b commit on `feature/lectr-v1`): Task 1 creates the branch with plan Step 1. Use the worktree that already has `feature/lectr-v1` checked out (`git worktree list`), or add one for it.
- **Sub-branch** (every other story): the branch is `feature/v1-<task>-<slug>`. If it already exists (a rerun, or a sibling PR merged first), reuse it: rebase on `origin/feature/lectr-v1`, resolve `SUMMARY.md` by keeping both entries newest first, and push with `--force-with-lease`. Otherwise run `git fetch origin` and `git worktree add -b <branch> <path> origin/feature/lectr-v1`, with `<path>` under a `lectr-worktrees/` folder next to the main checkout.

Then set the project status:

```bash
gh project item-edit 5 --owner rgoshen --url https://github.com/rgoshen/lectr/issues/$ARGUMENTS \
  --field Status --value "In Progress"
```

Done when: the worktree is on the right branch, based on the latest `origin/feature/lectr-v1`, and the item shows In Progress.

## 3. Build

Run the brief's plan steps (only the steps it scopes for split Tasks 14 and 16) in the step 2 worktree with superpowers:subagent-driven-development, which the plan names as its required sub-skill. Commit with the plan's message (or the brief's, for split tasks), a prepended `SUMMARY.md` entry, and no trailer lines.

Done when: every scoped plan step is done, and `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, and `uv run mypy src` pass in the worktree.

## 4. PR

- **Direct**: push `feature/lectr-v1`. Task 1b continues with plan Steps 4 to 6, asking the maintainer before opening the umbrella PR and before the `gh api` call.
- **Sub-branch**: push the branch and run `gh pr create --base feature/lectr-v1`, titled with the commit subject. Fill `.github/pull_request_template.md` and replace its `Closes #` line with `Part of #$ARGUMENTS`: GitHub ignores closing keywords on PRs that target a branch other than `main`.

Run `gh pr checks --watch`. On a red check, fix it in the worktree, commit (with its own `SUMMARY.md` entry), push, and watch again. If no checks appear because CI (#15) has not reached `feature/lectr-v1` yet, report that; the PR gets checks once it is rebased after #15 merges.

Done when: the four `test` jobs and `supply-chain` are green, or the missing CI is reported.

## 5. Report

Your run ends at the open PR; the maintainer reviews and merges. Report:

- PR URL and check results
- each "Done when" item from the brief, met or not and why
- every deviation from the plan
- for the maintainer, after merging: `gh issue close $ARGUMENTS` (the PR cannot close it) and `git worktree remove <path>`
