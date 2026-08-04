#!/usr/bin/env python3
"""Create a portable Obsidian aesthetic library from the bundled template."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_DIR / "assets" / "template"
CATALOG_DIR = SKILL_DIR / "assets" / "catalogs"


def empty_catalog() -> dict:
    return {
        "schema_version": 2,
        "verified_at": "",
        "overrides": {},
        "sources": [],
        "collection_defaults": {
            "exclude_url_regex": [
                "/(?:about|contact|privacy|terms|careers?|jobs?|team|people|services?|news|journal|events?)(?:/|$)",
                "/(?:tagged|category|author|tags?)(?:/|$)",
            ]
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize an Obsidian aesthetic library")
    parser.add_argument("--target", required=True, help="New library folder")
    parser.add_argument(
        "--catalog",
        choices=("design-studios-52", "empty"),
        default="design-studios-52",
        help="Use the bundled starter catalog or start without sources",
    )
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty folder: {target}")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, target, dirs_exist_ok=True)

    for relative in (
        "工作室", "内容", "本周精选",
        "_系统/assets/studios", "_系统/assets/content",
    ):
        (target / relative).mkdir(parents=True, exist_ok=True)

    sources_path = target / "_系统" / "订阅源" / "工作室来源.json"
    if args.catalog == "empty":
        sources_path.write_text(
            json.dumps(empty_catalog(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        shutil.copy2(CATALOG_DIR / "design-studios-52.json", sources_path)

    print(f"Created: {target}")
    print(f"Catalog: {args.catalog}")
    print(f"Next: python3 '{target / '_系统' / 'manage.py'}' setup --workers 10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
