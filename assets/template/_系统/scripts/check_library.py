#!/usr/bin/env python3
"""检查审美库的配置、卡片、资源、Bases 和项目基线。

默认只读；`--fix-content` 会把内容卡正文整理成统一的简洁结构，
并保留现有的“## 我的笔记”及其后内容。
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "_系统"
SOURCE_DIR = SYSTEM / "订阅源"
ASSET_DIR = SYSTEM / "assets"
SOURCES_PATH = SOURCE_DIR / "工作室来源.json"
RULES_PATH = SOURCE_DIR / "内容标签规则.json"
DB_PATH = SOURCE_DIR / "项目基线.sqlite3"


def split_note(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n?", text, flags=re.S)
    if not match:
        raise ValueError("缺少 YAML 属性区")
    return match.group(1), text[match.end():].lstrip("\n")


def scalar(frontmatter: str, key: str):
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", frontmatter)
    if not match:
        return None
    value = match.group(1)
    if value == "":
        return ""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        return value.strip("'\"")


def list_property(frontmatter: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*\n((?:  - .*\n?)*)", frontmatter)
    if not match:
        return []
    values = []
    for raw in re.findall(r"(?m)^  - (.*)$", match.group(1)):
        try:
            values.append(str(json.loads(raw)))
        except json.JSONDecodeError:
            values.append(raw.strip("'\""))
    return values


def wiki_target(value: object) -> str:
    match = re.search(r"\[\[([^\]|#]+)", str(value or ""))
    return match.group(1) if match else ""


def unique_asset_index() -> tuple[dict[str, Path], set[str]]:
    by_name: dict[str, Path] = {}
    duplicates: set[str] = set()
    for path in ASSET_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.name in by_name:
            duplicates.add(path.name)
        else:
            by_name[path.name] = path
    return by_name, duplicates


def render_content_body(path: Path, frontmatter: str, old_body: str) -> str:
    title = path.stem
    cover = wiki_target(scalar(frontmatter, "cover"))
    intro = str(scalar(frontmatter, "project_intro") or "")
    focus = str(scalar(frontmatter, "observation_focus") or "")
    comment = str(scalar(frontmatter, "editor_comment") or "")
    source_url = str(scalar(frontmatter, "source_url") or "")
    personal = ""
    personal_match = re.search(r"(?m)^## 我的笔记\s*$", old_body)
    if personal_match:
        personal = old_body[personal_match.start():].strip()
    parts = [f"# {title}"]
    if cover:
        parts.append(f"![[{cover}]]")
    parts.extend(["## 项目导读", intro, "## 观察重点", focus])
    if comment:
        parts.extend(["## 编辑短评", comment])
    if source_url:
        parts.append(f"[查看官方项目]({source_url})")
    if personal:
        parts.append(personal)
    return "\n\n".join(parts).strip() + "\n"


class Check:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="审美库完整性检查")
    parser.add_argument("--fix-content", action="store_true", help="整理内容卡正文")
    args = parser.parse_args()
    check = Check()

    try:
        payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
        sources = payload["sources"]
    except Exception as exc:
        print(f"❌ 工作室配置无法读取：{exc}")
        return 1

    if payload.get("schema_version") != 2:
        check.error("工作室配置 schema_version 应为 2")
    required_source = {
        "id", "name", "region", "website", "content_url", "studio_intro",
        "disciplines", "positioning", "observation_value", "method_traits",
        "media_structure", "collection_rule",
    }
    for source in sources:
        missing = sorted(key for key in required_source if not source.get(key))
        if missing:
            check.error(f"{source.get('name', '?')}: 配置缺少 {', '.join(missing)}")
    for field in ("id", "name", "website"):
        counts = Counter(str(source.get(field, "")) for source in sources)
        duplicates = sorted(value for value, count in counts.items() if count > 1)
        if duplicates:
            check.error(f"工作室 {field} 重复：{duplicates}")
    check.stats.append(f"工作室来源 {len(sources)}")

    asset_index, duplicate_assets = unique_asset_index()
    referenced_assets: set[str] = set()
    if duplicate_assets:
        check.error(f"重名资源：{sorted(duplicate_assets)}")

    studio_paths = sorted((ROOT / "工作室").glob("*.md"))
    expected_studio_files = {
        re.sub(r"[\\?*<>|]", "-", source["name"].replace(" / ", " ").replace("/", "-").replace(":", "-")).strip(". ")
        for source in sources
    }
    actual_studio_files = {path.stem for path in studio_paths}
    if expected_studio_files != actual_studio_files:
        check.error(
            f"工作室卡不匹配：缺少 {sorted(expected_studio_files - actual_studio_files)}，"
            f"多出 {sorted(actual_studio_files - expected_studio_files)}"
        )
    for path in studio_paths:
        try:
            fm, _ = split_note(path)
        except ValueError as exc:
            check.error(f"{path.name}: {exc}")
            continue
        for key in ("region", "positioning", "observation_value", "media_structure", "studio_intro", "website", "cover"):
            if not scalar(fm, key):
                check.error(f"{path.name}: 缺少 {key}")
        for key in ("disciplines", "method_traits"):
            if not list_property(fm, key):
                check.error(f"{path.name}: 缺少 {key}")
        cover = wiki_target(scalar(fm, "cover"))
        if cover:
            referenced_assets.add(cover)
        if cover and cover not in asset_index:
            check.error(f"{path.name}: 封面不存在 {cover}")
    check.stats.append(f"工作室卡 {len(studio_paths)}")

    tag_rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    allowed_disciplines = {item["tag"] for item in tag_rules["discipline_rules"]}
    allowed_concepts = {item["tag"] for item in tag_rules["concept_rules"]}
    content_paths = sorted((ROOT / "内容").glob("*.md"))
    source_urls: list[str] = []
    represented: set[str] = set()
    selected: list[tuple[str, int, str]] = []
    # 工作室卡和内容卡的封面都必须能被 Obsidian 唯一解析。
    for path in content_paths:
        try:
            fm, body = split_note(path)
        except ValueError as exc:
            check.error(f"{path.name}: {exc}")
            continue
        for key in ("studio", "read", "project_intro", "observation_focus", "source_url", "cover"):
            if scalar(fm, key) in {None, ""}:
                check.error(f"{path.name}: 缺少 {key}")
        studio_target = wiki_target(scalar(fm, "studio"))
        if studio_target:
            represented.add(studio_target)
            if studio_target not in actual_studio_files:
                check.error(f"{path.name}: 工作室链接不存在 {studio_target}")
        url = str(scalar(fm, "source_url") or "")
        if url:
            source_urls.append(url.rstrip("/"))
        cover = wiki_target(scalar(fm, "cover"))
        if cover:
            referenced_assets.add(cover)
            if cover not in asset_index:
                check.error(f"{path.name}: 封面不存在 {cover}")
        disciplines = list_property(fm, "discipline_tags")
        concepts = list_property(fm, "concept_tags")
        unknown_d = sorted(set(disciplines) - allowed_disciplines)
        unknown_c = sorted(set(concepts) - allowed_concepts)
        if unknown_d or unknown_c:
            check.error(f"{path.name}: 未知标签 {unknown_d + unknown_c}")
        if len(disciplines) > 4 or len(concepts) > tag_rules["concept_limit"]:
            check.error(f"{path.name}: 标签数量超过上限")
        status = str(scalar(fm, "editorial_status") or "")
        if status == "本周精选":
            issue = str(scalar(fm, "featured_issue") or "")
            order = scalar(fm, "featured_order")
            comment = str(scalar(fm, "editor_comment") or "")
            if not issue or not isinstance(order, int) or not comment:
                check.error(f"{path.name}: 精选字段不完整")
            else:
                selected.append((issue, order, path.stem))
        expected_body = render_content_body(path, fm, body)
        if args.fix_content and body != expected_body:
            path.write_text(f"---\n{fm}\n---\n\n{expected_body}", encoding="utf-8")
            body = expected_body
        if body != expected_body:
            check.error(f"{path.name}: 正文与属性不同步（可运行 check --fix-content）")
        if "中文翻译" in body or "project-intro-zh" in body:
            check.error(f"{path.name}: 存在多余的翻译标记")
    duplicates = sorted(url for url, count in Counter(source_urls).items() if count > 1)
    if duplicates:
        check.error(f"内容原文 URL 重复：{duplicates}")
    if content_paths and len(represented) < len(sources):
        missing = sorted(expected_studio_files - represented)
        check.warn(f"尚无基础样本的工作室：{', '.join(missing)}")
    elif sources and not content_paths:
        check.warn("内容画廊尚未建立基础样本")
    check.stats.append(f"内容卡 {len(content_paths)}，已覆盖工作室 {len(represented)}/{len(sources)}")

    issue_groups: dict[str, list[tuple[int, str]]] = {}
    for issue, order, title in selected:
        issue_groups.setdefault(issue, []).append((order, title))
    for issue, cards in issue_groups.items():
        limit = 15 if issue == "第 01 期" else 10
        orders = [order for order, _ in cards]
        if len(cards) > limit:
            check.error(f"{issue}: 精选 {len(cards)} 条，超过上限 {limit}")
        if sorted(orders) != list(range(1, len(cards) + 1)):
            check.error(f"{issue}: featured_order 不连续")
        issue_notes = sorted((ROOT / "本周精选").glob(f"{issue}*.md"))
        if not issue_notes:
            check.error(f"{issue}: 缺少本期精选文档")
        else:
            issue_text = issue_notes[0].read_text(encoding="utf-8")
            linked = {
                target for target in re.findall(r"\[\[([^\]|#]+)", issue_text)
                if target in {path.stem for path in content_paths}
            }
            expected = {title for _, title in cards}
            if linked != expected:
                check.error(
                    f"{issue}: 精选文档与卡片不一致，缺少 {sorted(expected - linked)}，"
                    f"多出 {sorted(linked - expected)}"
                )
    check.stats.append(f"本周精选 {len(selected)}")

    for path in asset_index.values():
        head = path.read_bytes()[:16]
        valid = (
            head.startswith(b"\xff\xd8\xff")
            or head.startswith(b"\x89PNG\r\n\x1a\n")
            or (path.suffix.lower() == ".svg" and b"<svg" in path.read_bytes()[:512])
        )
        if not valid:
            check.error(f"无法识别的图片资源：{path.name}")
    orphan_assets = sorted(set(asset_index) - referenced_assets)
    if orphan_assets:
        check.warn(f"未被卡片引用的资源：{', '.join(orphan_assets)}")
    check.stats.append(f"图片资源 {len(asset_index)}")

    content_base = (ROOT / "设计内容画廊.base").read_text(encoding="utf-8")
    studio_base = (ROOT / "设计工作室画廊.base").read_text(encoding="utf-8")
    if 'file.inFolder(this.file.folder + "/内容")' not in content_base:
        check.error("设计内容画廊未使用相对路径限定内容目录")
    if 'file.inFolder(this.file.folder + "/工作室")' not in studio_base:
        check.error("设计工作室画廊未使用相对路径限定工作室目录")
    if "审美库测试" in content_base + studio_base:
        check.error("Bases 仍包含旧目录名“审美库测试”")

    try:
        connection = sqlite3.connect(DB_PATH)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        source_state = connection.execute("SELECT COUNT(*) FROM source_state").fetchone()[0]
        baseline_count = connection.execute("SELECT COUNT(*) FROM baseline_items").fetchone()[0]
        latest = connection.execute(
            "SELECT error_count FROM crawl_runs WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1"
        ).fetchone()
        connection.close()
        if integrity != "ok" or foreign_keys:
            check.error("项目基线数据库完整性检查失败")
        if source_state != len(sources):
            check.error(f"项目基线工作室数 {source_state} ≠ 配置数 {len(sources)}")
        if latest and latest[0]:
            check.warn(f"最近一次同步有 {latest[0]} 个来源错误，建议重试")
        check.stats.append(f"项目基线 {baseline_count}")
    except Exception as exc:
        check.error(f"项目基线数据库检查失败：{exc}")

    for name in ("本周新增候选.json", "来源变更提醒.json"):
        try:
            json.loads((SOURCE_DIR / name).read_text(encoding="utf-8"))
        except Exception as exc:
            check.error(f"{name} 无法读取：{exc}")

    for item in check.stats:
        print(f"✓ {item}")
    for item in check.warnings:
        print(f"⚠ {item}")
    for item in check.errors:
        print(f"✗ {item}")
    print(f"\n结果：{len(check.errors)} 个错误，{len(check.warnings)} 个提醒")
    return 1 if check.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
