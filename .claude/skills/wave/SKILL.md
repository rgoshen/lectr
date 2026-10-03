---
name: wave
description: Run every ready story in one lectr v1 wave in parallel, one subagent per story.
argument-hint: <wave-number>
disable-model-invocation: true
---

# Wave $ARGUMENTS

Run every ready story in Wave $ARGUMENTS of GitHub Project 5 at once. Each subagent works one story by following `.claude/skills/story/SKILL.md`; this skill picks the stories, dispatches them, and reports.

## 1. Pick

List the wave's open items:

```bash
gh project item-list 5 --owner rgoshen --format json --limit 100 \
  --jq '.items[] | select(.wave == "Wave $ARGUMENTS" and .status != "Done") | .content.number'
```

Run the story skill's Gate on each one (`gh issue view <N> --json title,body,state,labels,blockedBy`). A story is ready when it passes; otherwise it is skipped, with the Gate's reason. Stop and report if none are ready.

Done when: every listed story is either ready or skipped with a reason.

## 2. Dispatch

Send one `general-purpose` Agent call per ready story, all in a single message so they run concurrently, each with `model: "sonnet"` (the maintainer's CLAUDE.md assigns implementation to Sonnet). Leave `isolation` unset: Claude Code bases those worktrees on `main`, and each story makes its own worktree from `origin/feature/lectr-v1`.

Prompt for each subagent, with `<N>` filled in:

> Read `.claude/skills/story/SKILL.md` and follow it for issue #<N>, reading every `$ARGUMENTS` in it as `<N>`. You cannot reach the maintainer. Where the story or the plan says to ask the maintainer, or a decision gate stops, end there and return the question with your branch, worktree path, and last commit. Return the story's step 5 report.

Done when: every dispatched subagent has returned.

## 3. Report

Give one row per story: issue, PR URL, checks, and outcome (PR open, waiting on a maintainer question, or skipped with its reason). Then relay each returned question to the maintainer.

Every PR in the wave prepends to `SUMMARY.md`, so after the maintainer merges one, the rest conflict. Recommend merging one at a time; `/story <N>` rebases an existing PR and reruns its checks.
