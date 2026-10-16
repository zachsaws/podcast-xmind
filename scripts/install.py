#!/usr/bin/env python3
"""Install only the reviewed local skill. Never replace an existing installation."""
import argparse
import os
import shutil
from pathlib import Path


def install(base):
    source = Path(__file__).resolve().parents[1] / "skills" / "podcast-xmind"
    destination = Path(base).expanduser() / source.name
    if os.path.lexists(destination):
        raise FileExistsError(f"Refusing to replace existing path: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["codex", "claude"], default="codex")
    parser.add_argument("--dest", type=Path, help="Skills parent directory (overrides --agent)")
    args = parser.parse_args()
    base = args.dest or Path.home() / (".agents" if args.agent == "codex" else ".claude") / "skills"
    try:
        print(install(base))
    except OSError as exc:
        parser.exit(1, str(exc) + "\n")
