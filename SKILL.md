---
name: sane-pull-requests
description: Plan, implement, and submit small reviewable changes using dependency-based branches, independent audits, and safe intermediate behavior. Use for feature work or changes that may span multiple PRs, or when explicitly asked to keep a change reviewable.
---

# Sane Pull Requests

Deliver the requested behavior in coherent review units, targeting **300 added plus deleted lines per PR**. Keep each intermediate state working. A small diff is a review budget, not a reason to omit tests, compress readable code, add unnecessary abstractions, or move required work into a later PR.

## Plan the review units

Inspect the request, repository guidance, current Git state, relevant callers, existing tests, and any established flag mechanism. Preserve existing user work and follow the repository's branch and publication conventions.

For work that needs multiple changes, make a short plan giving each unit's purpose, parent, expected scope, verification, and behavior after merge. For a small single change, a sentence is enough. Prefer complete behavioral slices; separate unrelated refactoring. Keep related tests with their behavior. Do not create an elaborate stack plan for a trivial fix.

This skill supplies the complete split workflow; no companion splitting skill is required. When another splitting skill such as `split-to-prs` is also loaded, apply this workflow's split and approval policy instead of adding its generic split-plan approval step. An authorized implementation or splitting task includes coherent local branches and commits: explain the plan and proceed without another confirmation. Honor explicit user or repository restrictions, including required plan approval, and keep proposal-only tasks read-only. Before reorganizing existing work, preserve a recoverable snapshot that includes untracked files. Size exceptions, independent audits, and authorization for publication remain separate gates.

Use descriptive branch names, following repository conventions (otherwise `codex/<change>`). Stack B on A only if B actually depends on A. Independent work branches from the integration branch and can proceed in parallel in separate workspaces. Do not change the user's merge or publication policy.

Each branch must build and pass relevant checks on its declared parent without needing a future child. A slice can be incomplete as a feature while remaining safe as a deployed intermediate state.

## Implement and measure

Implement one review unit at a time. Aim below 300 to leave room for tests and review fixes; remeasure as scope changes.

The budget is **gross additions plus deletions against the immediate PR base**, not net growth, the last commit, or the cumulative stack against main. Include tests, documentation, configuration, generated text, and lockfiles. Show non-text changes explicitly. Do not silently exempt large files or hide churn with diff filters.

For a committed snapshot, run the bundled read-only helper:

```sh
python3 <skill-dir>/scripts/inspect_diff.py --repo <repo> --base <parent> --head HEAD --integration <integration-branch>
```

Read the output and also inspect the patch. Dirty or untracked work is not included in the measured commit; do not present that count as the whole pending change. Before committing, inspect tracked changes and enumerate new files. For publication, confirm that the hosting service's displayed PR base and diff match the intended unit. Report cumulative size as context, not as the per-PR gate.

Apply these bands to each branch's measured change:

- **300 lines or fewer:** No size-specific action. Continue normal verification and independent audit.
- **301–500 lines:** First identify whether a coherent split would improve review. If so, split without asking, targeting 300 or fewer per branch. Otherwise, prepare and verify the complete candidate and have an independent reviewer assess the proposed exception before asking the user. Present the actual size, the concrete split considered, and why that split would impair review or produce an invalid intermediate state. Request an exception before submission or dependent implementation.
- **More than 500 lines:** Split automatically into coherent branches, targeting 300 or fewer per branch. If a necessary review unit still exceeds 500, prepare and verify the smallest coherent candidate and have an independent reviewer assess why further decomposition fails. Report its actual size, the splits considered, and why no valid decomposition keeps that unit within 500 lines. Do not invent artificial splits or silently exceed the limit. Require the exact confirmation below before submission or dependent implementation.

Never separate behavior from its necessary tests, create a broken intermediate state, or introduce needless scaffolding merely to reach a band. Apply these bands again to each resulting branch; 500 is not the planning target. A flag does not justify an otherwise incoherent split.

For an independently reviewed exception above 500 lines, ask the user to confirm with this exact phrase:

> I understand that by continuing with this big change, I'm making life hell for the unfortunate pull request reviewer.

After that confirmation, make one brief, playful comment about the diff's review burden, then continue the authorized work. For example: “The reviewer's scroll wheel has filed a complaint. Let's make the review notes useful.” Keep it about the change, not the developer. Skip the comment for verified mechanical changes, such as reproducible generated output or formatting demonstrated to preserve behavior. A configuration file or whitespace-only appearance is not sufficient evidence: configuration can change behavior, and whitespace can be semantic. Mechanical changes still require measurement, decomposition assessment, confirmation, and audit.

Record any exception against the reviewed candidate's base/head, size, reason, and user's response. Distinguish the exception's accepted scope from the audit of a particular snapshot.

Carry existing approval forward for necessary correctness fixes and their regression tests within that scope, even when the commit or line count changes. Inspect the delta, remeasure, and record why the correction remains within the accepted purpose, constraints, and decomposition rationale. Refresh the audit before submission or dependent implementation; approval persistence does not carry a stale audit forward. Do not repeat the confirmation phrase or playful comment for an exception carried forward this way.

Apply the size bands afresh if work materially expands the accepted scope, invalidates the decomposition rationale, exceeds an explicit user-imposed limit, or crosses above 500 without the required exact confirmation. A new commit or increased line count alone does not establish a scope change. The exact phrase and playful comment apply only above 500 lines. An exception does not waive verification, independent audit, or publication permissions, and it does not mean the 300-line budget passed.

## Audit before building on a branch

Before dependent implementation or marking a branch ready for submission, delegate an independent review using [the reviewer contract](references/reviewer.md). Use fresh context without the author's reasoning history when supported. Supply the original requirement, repository and branch, resolved base/head commits, patch, relevant surrounding code, and verification results. Do not supply an intended verdict or tell the reviewer which defect to find. The reviewer is read-only and must not change the author's checkout.

Resolve blocking findings and have the changed result reviewed. Record the reviewed base/head and merge base, verdict, findings and dispositions, checks actually run, and limitations in the existing task/PR record. Local-only work can keep this record outside the product diff. `PASS` means no unresolved blockers for this reviewed snapshot; it is not human approval or proof of correctness.

Do not start dependent implementation until that snapshot passes and any size exception is accepted. Planning and unrelated implementation may continue. If an independent reviewer is unavailable, report the missing gate and keep the result unapproved; do not relabel self-review as independent review. If review cannot converge, surface the unresolved decision rather than repeatedly retrying or accepting it silently.

## Keep reviews current as the stack changes

Review applies to commits and context, not to a branch name forever. Before starting a child, verify that its parent still matches the reviewed snapshot. If a parent changes, inspect the changed behavior and update affected descendants before extending the stack.

After a rebase, conflict resolution, parent fix, merge, or PR-base change, remeasure the actual patch, run checks appropriate to the affected behavior, and refresh review evidence. A reviewer may carry forward a verdict after establishing patch equivalence and unchanged relevant context; do not automatically repeat a full review for metadata-only changes. Conflict resolutions or changed contracts require substantive review. Use the repository's merge strategy and preserve only the child's intended changes when restacking; do not assume a squash merge preserves ancestry.

## Gate unfinished behavior when necessary

A feature spanning several PRs does not automatically need a flag. A flag is needed when an intermediate merge would otherwise expose unfinished behavior, or the requested rollout needs control. A flag does not waive the size budget or make incompatible data/schema changes safe.

When gating is needed, ask **once per feature** whether the user wants a code constant, an environment variable, or a configuration-managed flag. Explain the repository's existing mechanism and recommend reusing it when suitable. Honor an existing explicit choice. Prepare independent work while the choice is pending, but do not implement a guessed mechanism.

- **Constant:** appropriate when a code change and deployment to switch state are acceptable.
- **Environment variable:** appropriate for deployment-level control; state changes usually require restarting or redeploying processes.
- **Configuration manager:** appropriate for dynamic or targeted rollout; scope any missing integration separately rather than silently introducing a service.

Prefer one release flag per feature where practical. Define a safe default, flag owner, enablement conditions, and removal condition. Test disabled behavior and the enabled behavior supported by the current slice; complete feature verification before activation. Trace every reachable entry point: HTTP handlers, jobs, startup/registration, and side effects. Hiding UI alone is not a backend guard. Reuse existing flag evaluation rather than building a framework for one flag.

## Handoff

Report each branch's purpose, parent/dependents, changed-line and file counts, checks, audit status, and any flag or accepted exception. Include a short stack map when useful. Distinguish implemented, audited, submitted, and merged states; report only what actually happened. Follow the user's authorization for pushes, PRs, and merges. This skill adds no authority to publish or rewrite shared history.
