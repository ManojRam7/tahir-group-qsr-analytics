"""Fail on likely private artifacts in tracked or publishable untracked files."""

import re
import subprocess
from pathlib import Path

BLOCKED_SUFFIXES = {".pdf", ".eml", ".msg", ".png", ".jpg", ".jpeg", ".xlsx", ".zip"}
PATTERNS = [
    re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}"),
    re.compile(
        "|".join(["/" + "Users/", "/mnt/" + "data/", r"mail\.google\.com/" + "mail/"]), re.I
    ),
    re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
]


def problems(path, contents):
    issues = []
    if path.suffix.lower() in BLOCKED_SUFFIXES or any(
        part in {"private", "source_material"} for part in path.parts
    ):
        issues.append("private/binary artifact type")
    for pattern in PATTERNS:
        if pattern.search(contents):
            issues.append("possible personal data, local source path or credential")
    return issues


def main():
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
        )
        .decode()
        .split("\0")
    )
    failures = []
    for name in sorted(set(names) - {""}):
        path = Path(name)
        if not path.is_file():
            continue
        for issue in problems(path, path.read_text(errors="replace")):
            failures.append(f"{path}: {issue}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("Publication guard passed; manual review remains required for new data.")


if __name__ == "__main__":
    main()
