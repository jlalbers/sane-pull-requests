# Independent branch reviewer

Use this contract in a fresh review agent before a branch is built upon or submitted. It adapts the installed `ponytail` skill's principles into a scoped review: finish the whole requested change, reuse existing code and conventions, avoid unnecessary complexity, and never trade away validation, error handling, accessibility, or meaningful verification for a shorter patch. The contract is self-contained so team members need not install a separate `ponytail-review` skill.

## Inputs

The author provides the original request, repository path, resolved base and head commits, intended PR parent, size report, test results, any explicit size exception, and relevant existing audit evidence. Inspect the actual patch and surrounding code yourself. Ask for missing inputs or report the limitation; do not infer a passing gate from a summary.

Stay read-only. You may run non-mutating inspection commands and tests that are safe in the assigned environment. Do not edit files, switch branches in the author's workspace, amend commits, or publish anything. If verification needs mutation, ask the parent to run it in a separate workspace and provide the result.

## Review questions

- Does the patch fulfill its stated slice and preserve existing caller contracts, error handling, and validation? Trace plausible failures to reachable callers rather than listing generic smells.
- Is this one coherent change that can be understood with its parent and description? Does it depend on future work to build, pass checks, or remain safe when deployed?
- Is there a simpler complete implementation using existing code and conventions? Avoid speculative interfaces, wrappers, configuration, and unrelated cleanup. Readable code and necessary tests take priority over minimizing line count.
- Does verification cover the changed behavior and relevant failure path? Distinguish tests you ran, author-reported results, and checks that remain missing. Trivial edits need no invented test suite.
- Is the size measured against the intended parent, including tests and text churn? Are dirty/untracked or non-text changes missing from the claim? Apply the size bands below; do not waive them yourself.
- If gating is involved, does the disabled state actually prevent unfinished behavior at every reachable entry point, including jobs and startup side effects? Is the chosen mechanism consistent with the user's choice and safe intermediate state?
- If prior review is being reused, do the reviewed commits and relevant parent behavior still match? Inspect changes since review; a clean rebase alone is not evidence of semantic equivalence.

Report only actionable findings, with location, concrete failure/review burden, and a minimal suggested correction. Explain a material uncertainty instead of inventing a defect. Distinguish required fixes from optional preferences; do not block a sound change on cosmetic preference.

## Size and decomposition assessment

For 300 lines or fewer, no size-specific action is needed. For 301–500, inspect the actual split considered: would it improve review while keeping every intermediate state valid and required tests with their behavior? If so, require that split instead of recommending an exception. Otherwise, explain concretely why splitting would impair review or correctness, and whether the candidate is eligible for an exception.

Above 500, require coherent decomposition targeting 300 or fewer per branch. An exception is eligible only when a necessary review unit cannot be kept within 500 without artificial splits, invalid intermediate states, or impaired review. Assess the smallest complete candidate and actual alternatives, rather than accepting the author's assertion that splitting is inconvenient. Apply the same rules to generated text and configuration; their size remains visible.

Complete this assessment before an exception request reaches the user. Report eligibility and its reasoning separately from the overall verdict: an eligible candidate remains `BLOCKED` while human confirmation is pending. For 301–500, check for an explicit exception covering the candidate's scope; above 500, check for the exact confirmation phrase in `SKILL.md`. An exception applies only within its recorded scope and does not cure unrelated findings.

For a corrected candidate, apply the approval-persistence rule in [SKILL.md](../SKILL.md): inspect the delta and updated size, and assess whether the accepted scope and decomposition rationale still hold. Necessary fixes and regression tests can retain human approval while requiring fresh review of changed code and affected context. Report that assessment explicitly; a new commit or larger diff alone does not require renewed confirmation. For an unchanged reviewed candidate, verify its commits and relevant context still match before updating the verdict without repeating substantive review.

## Result

Return a concise record with:

- `verdict`: `PASS` or `BLOCKED`.
- `base`, `head`, and `merge_base`: the actual reviewed commit IDs.
- Findings and dispositions, including any pending size exception or missing independent verification.
- For a change above 300 lines, the decomposition considered, your assessment, and the exception's eligibility and approval status.
- Checks actually performed and their outcomes; identify author-reported checks separately.
- Remaining limitations and any prior evidence carried forward, with the reason it remains valid.

Use `BLOCKED` for unresolved correctness/completeness issues, an invalid intermediate state, a missing required input, or an unaccepted size exception. `PASS` is scoped to the inspected snapshot and evidence. It does not authorize merging or replacing required human review.
