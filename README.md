# Sane Pull Requests

[![ASCII-style boxy robot handing small PRs to a reviewer while a woman's head and raised arms poke out of a huge code pile.](assets/readme-hero-ascii-v7-preview.png)](assets/readme-hero-ascii-v7.png)

**Your agent can write a thousand lines. Someone still has to review them.**

Sane Pull Requests teaches coding agents to plan and deliver work in small, coherent PRs: aim for **300 added plus deleted lines**, stack branches where dependencies require it, and independently review each foundation before building on it.

Finish the feature. Let the reviewer keep their afternoon.

## Install

The commands below use the [skills CLI](https://github.com/vercel-labs/skills) and require **Node.js 22.20.0 or later**, with npm (`npx`).

```sh
npx skills add jlalbers/sane-pull-requests
```

By default, this installs for the current project. For a global Codex installation:

```sh
npx skills add jlalbers/sane-pull-requests --agent codex --global
```

The installed workflow needs Git, Python 3, and an agent that can delegate an independent review. The Python helper uses the standard library. No separate `ponytail` or `split-to-prs` installation is required.

## Use it

Ask your agent:

```text
Use sane-pull-requests to implement reconciliation previews.
```

Or invoke it explicitly in Codex:

```text
$sane-pull-requests Implement reconciliation previews.
```

It also works on a change that has already grown:

```text
Use sane-pull-requests to split my current branch into coherent review units.
Preserve all existing work.
```

The agent explains the plan and proceeds with authorized local branches and commits. Routine splits do not need another approval round. Explicit user and repository restrictions still apply; a request for a proposal stays a proposal. Pushes, PR publication, merges, and shared-history changes follow your existing authorization rules.

## What changes

You ask for a reconciliation preview. One possible delivery is an 800-line PR containing normalization, calculation, an API, and a page. The reviewer has to understand all four at once.

An illustrative split with Sane Pull Requests:

```text
main
└── codex/normalize-ledger         180 lines
    └── codex/reconciliation      240 lines
        └── codex/preview-api     160 lines
            └── codex/preview-ui  220 lines
```

Those sizes include each unit's tests and documentation. They illustrate review boundaries, not benchmark results.

Each branch works on its own declared parent. Each foundation gets an independent audit before dependent implementation begins. Reviewers can assess one contract at a time, with the preceding work already checked.

Dependencies determine the stack. Independent changes branch from the integration branch and can proceed in parallel. A small fix gets a small plan.

## The review budget

The count is **additions plus deletions against the immediate PR base**. Replacing 150 lines with 150 new lines uses the full 300-line budget. Tests, docs, configuration, generated text, and lockfiles count too. Non-text changes need separate inspection.

- **300 lines or fewer:** continue verification and independent audit. No size-specific permission needed.
- **301–500 lines:** split automatically if a coherent split would improve review. Otherwise, verify the complete candidate and get an independent assessment before requesting an exception. The request must explain the actual split considered and why it would impair review or leave an invalid intermediate state. The exception must be accepted before submission or dependent implementation.
- **More than 500 lines:** split automatically into coherent units, aiming for 300 or fewer each. If a necessary unit still exceeds 500, prepare and verify the smallest coherent candidate, get an independent decomposition assessment, and request the confirmation below.

Tests stay with the behavior they verify. Readable code stays readable. Broken intermediate states, artificial splits, and temporary scaffolding added just to hit a number defeat the point.

### The large-diff confession

An independently assessed exception above 500 lines requires this exact response before submission or dependent implementation:

> I understand that by continuing with this big change, I'm making life hell for the unfortunate pull request reviewer.

“Send it”, "LGTM", or "🚀" do not count.

After confirmation, the agent makes one brief joke about the review burden and continues. Proven mechanical changes skip the joke, but still need the confirmation and audit. A config file can change behavior; whitespace can be semantic.

Necessary correctness fixes and regression tests can retain an accepted exception within the same scope. They still need fresh review of the changed snapshot. A new commit alone is not a reason to make you recite the sentence again.

## Review before building higher

The independent reviewer reads the patch and connected code, checks the requested behavior, and assesses whether the review unit makes sense. The author resolves blockers before extending a dependent branch or marking the change ready for submission.

Review belongs to a particular snapshot and its context. When a parent changes, the agent checks affected descendants, remeasures, runs relevant checks, and refreshes review evidence. A clean rebase does not establish that the behavior still works.

If independent review is unavailable, the review gate stays unapproved. An agent does not become independent by rereading its own patch with a more serious expression.

## Keep unfinished behavior out of reach

A feature spanning several PRs needs a flag when an intermediate merge would expose unfinished behavior, or when rollout needs control. Safe internal groundwork can land without one.

When a flag is needed, the agent asks once where it should live:

- A **code constant** for a switch changed through code and deployment.
- An **environment variable** for deployment-level control, usually requiring a restart or redeployment.
- A **configuration manager**, such as Flagsmith or AWS AppConfig, for dynamic or targeted rollout.

It honors an existing choice, recommends a suitable existing mechanism, and guards every reachable entry point: UI, API, commands, jobs, and startup side effects. A hidden button cannot stop a worker that is already running.

Flags do not waive the review budget or make incompatible schema changes safe. The flag needs a safe default, an owner, enablement conditions, and a removal condition.

## What you get back

For each branch: its purpose, parent and dependents, line and file counts, verification, independent audit status, and any flag or accepted exception. Implemented, audited, submitted, and merged are separate states.

This is an agent workflow, with a read-only helper for measuring committed diffs. It is not a server-side merge rule. The helper reports dirty and untracked work separately; a size count cannot establish correctness or approval.

The behavior lives in [SKILL.md](SKILL.md), with a bundled [reviewer contract](references/reviewer.md) and [diff inspector](scripts/inspect_diff.py).

## Credit

The review approach draws on [Ponytail](https://github.com/DietrichGebert/ponytail): understand the code, solve the whole task, and keep the change as small as the job allows. Sane Pull Requests packages those principles into a self-contained workflow for review size, branch dependencies, and safe intermediate changes.
