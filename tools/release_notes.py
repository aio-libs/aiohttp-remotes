"""Print the CHANGES.rst section of a release as Markdown for a GitHub release."""

import re
import sys
from pathlib import Path

HEADING = re.compile(r"^\d+\.\d+\.\d+\S* \(\d{4}-\d{2}-\d{2}\)$")
UNDERLINE = re.compile(r"^([=\-~^])\1+$")
ISSUE = re.compile(
    r"`#(\d+) <https://github\.com/aio-libs/aiohttp-remotes/issues/\1>`_"
)
USER = re.compile(r"`@([\w-]+) <https://github\.com/\1>`_")


def extract(changes: str, version: str) -> str:
    lines = changes.splitlines()
    start = None
    for i, line in enumerate(lines):
        if HEADING.match(line) and line.startswith(f"{version} ("):
            start = i + 2  # skip the title and its underline
            break
    if start is None:
        raise SystemExit(f"Version {version} is not found in CHANGES.rst")

    body: list[str] = []
    for i in range(start, len(lines)):
        line = lines[i]
        if HEADING.match(line):
            break
        if UNDERLINE.match(line):
            body[-1] = f"### {body[-1]}"
            continue
        line = ISSUE.sub(r"#\1", line)
        line = USER.sub(r"@\1", line)
        body.append(line)

    notes = "\n".join(body).strip()
    if not notes:
        raise SystemExit(f"Release notes for {version} are empty")
    return notes + "\n"


def main() -> None:
    version = sys.argv[1]
    changes = Path(sys.argv[2] if len(sys.argv) > 2 else "CHANGES.rst")
    sys.stdout.write(extract(changes.read_text(encoding="utf-8"), version))


if __name__ == "__main__":
    main()
