#!/usr/bin/env python3
"""Inspect a committed, parent-relative Git diff without changing the repository."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


class InspectionError(Exception):
    pass


def git(repo, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", LC_ALL="C")
    result = subprocess.run(
        ["git", "-C", str(repo), *args], env=env, capture_output=True, check=False
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise InspectionError(message or f"git {args[0]} failed ({result.returncode})")
    return result.stdout


def decode(value):
    return value.decode("utf-8", "surrogateescape")


def resolve(repo, ref):
    return decode(git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}")).strip()


def compare(repo, base_ref, head_sha, limit):
    base_sha = resolve(repo, base_ref)
    bases = decode(git(repo, "merge-base", "--all", base_sha, head_sha)).splitlines()
    if len(bases) != 1:
        raise InspectionError("Comparison requires exactly one merge base")
    merge_base = bases[0]
    options = (
        "-z", "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative", "--find-renames=50%",
        "--ignore-submodules=none", merge_base, head_sha, "--",
    )
    # NUL delimiters preserve tabs, newlines, and arbitrary bytes in Git paths.
    stats = git(repo, "diff", "--numstat", *options).split(b"\0")
    counts = {}
    index = 0
    while index < len(stats) - 1:
        added, deleted, path = stats[index].split(b"\t", 2)
        index += 1
        old_path = None
        if not path:
            old_path, path = stats[index:index + 2]
            index += 2
        counts[(old_path, path)] = (
            None if added == b"-" else int(added),
            None if deleted == b"-" else int(deleted),
        )

    raw = git(repo, "diff", "--raw", "--abbrev=40", *options).split(b"\0")
    files = []
    index = 0
    while index < len(raw) - 1:
        old_mode, new_mode, _, _, status = raw[index][1:].split()
        path = raw[index + 1]
        old_path = None
        index += 2
        if status[:1] in (b"R", b"C"):
            old_path, path = path, raw[index]
            index += 1
        added, deleted = counts.pop((old_path, path))
        files.append({
            "path": decode(path),
            "old_path": decode(old_path) if old_path is not None else None,
            "status": decode(status),
            "added_lines": added,
            "deleted_lines": deleted,
            "binary": added is None or deleted is None,
            "old_mode": decode(old_mode),
            "new_mode": decode(new_mode),
            "mode_changed": old_mode != new_mode,
            "submodule": b"160000" in (old_mode, new_mode),
        })
    if counts:
        raise InspectionError("Raw diff and line statistics disagree")
    added = sum(item["added_lines"] or 0 for item in files)
    deleted = sum(item["deleted_lines"] or 0 for item in files)
    unknown = [item["path"] for item in files if item["binary"] or item["submodule"]]
    total = added + deleted
    return {
        "base": {"ref": base_ref, "commit": base_sha},
        "head_commit": head_sha,
        "merge_base": merge_base,
        "comparison": "three-dot (merge base to head)",
        "limit": limit,
        "added_lines": added,
        "deleted_lines": deleted,
        "changed_lines": total,
        "file_count": len(files),
        "files": files,
        "text_budget_status": "within" if total <= limit else "over",
        "within_budget": False if total > limit else (None if unknown else True),
        "unmeasurable_paths": unknown,
        "review_required": bool(unknown),
    }


def worktree_status(repo):
    tokens = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=none").split(b"\0")
    entries = []
    index = 0
    while index < len(tokens) - 1:
        code = decode(tokens[index][:2])
        path = decode(tokens[index][3:])
        index += 1
        old_path = None
        if "R" in code or "C" in code:
            old_path = decode(tokens[index])
            index += 1
        entries.append({"code": code, "path": path, "old_path": old_path})
    return {"dirty": bool(entries), "untracked": [e["path"] for e in entries if e["code"] == "??"], "entries": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", required=True, help="Immediate parent branch/ref")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--integration", help="Also report cumulative diff against this ref")
    parser.add_argument("--check", action="store_true", help="Exit 1 if primary diff is over budget, unmeasurable, or worktree is dirty")
    args = parser.parse_args()
    try:
        if args.limit < 0:
            raise InspectionError("Line limit must be nonnegative")
        head_sha = resolve(args.repo, args.head)
        report = compare(args.repo, args.base, head_sha, args.limit)
        report.update({
            "schema_version": 1,
            "repo": decode(git(args.repo, "rev-parse", "--show-toplevel")).strip(),
            "head_ref": args.head,
            "scope": "Committed snapshots only; staged, unstaged and untracked changes are not counted",
            "worktree": worktree_status(args.repo),
            "limitations": "Line counts do not certify atomicity, correctness, audit approval or completeness; binary/submodule changes require separate review",
        })
        if args.integration:
            report["cumulative"] = compare(args.repo, args.integration, head_sha, args.limit)
        failed = report["within_budget"] is not True or report["worktree"]["dirty"]
        report["check_passed"] = not failed
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return 1 if args.check and failed else 0
    except (InspectionError, OSError, ValueError, KeyError, IndexError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
