#!/usr/bin/env python3
"""审美库的统一管理入口。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent / "scripts"


def run(script: str, *arguments: str) -> int:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *arguments]).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="审美库管理")
    parser.add_argument(
        "command",
        choices=("setup", "check", "fix", "sync", "baseline", "studios", "sources"),
        help="setup 初始建库；check 检查；fix 整理正文；sync 每周同步",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER)
    options = parser.parse_args()

    if options.command == "check":
        return run("check_library.py", *options.args)
    if options.command == "fix":
        return run("check_library.py", "--fix-content", *options.args)
    if options.command == "studios":
        return run("build_catalog.py", *options.args)
    if options.command == "sources":
        return run("audit_sources.py", *options.args)
    if options.command == "setup":
        result = run("build_catalog.py")
        if result:
            return result
        result = run("build_project_baseline.py", "--mode", "baseline", *options.args)
        return result or run("check_library.py")
    mode = "sync" if options.command == "sync" else "baseline"
    result = run("build_project_baseline.py", "--mode", mode, *options.args)
    return result or run("check_library.py")


if __name__ == "__main__":
    raise SystemExit(main())
