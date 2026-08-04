#!/usr/bin/env python3
"""建立和同步设计工作室的永久项目账本。

这个脚本只更新机器基线，不生成 Obsidian 公开内容卡。
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from collect_projects import Item, canonical_url, collect_source


ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = ROOT / "_系统" / "订阅源" / "工作室来源.json"
DB_PATH = ROOT / "_系统" / "订阅源" / "项目基线.sqlite3"
REPORT_PATH = ROOT / "_系统" / "订阅源" / "项目基线报告.md"
NEW_ITEMS_PATH = ROOT / "_系统" / "订阅源" / "本周新增候选.json"
SOURCE_ALERTS_PATH = ROOT / "_系统" / "订阅源" / "来源变更提醒.json"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_sources() -> list[dict]:
    payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    overrides = payload.get("overrides", {})
    sources: list[dict] = []
    for raw in payload["sources"]:
        source = dict(raw)
        source.update(overrides.get(source["id"], {}))
        if source.get("subscription_enabled", True):
            sources.append(source)
    return sources


def load_rules(sources: list[dict]) -> tuple[list[str], dict[str, dict]]:
    payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    rules = {source["id"]: source.get("collection_rule", {}) for source in sources}
    missing = sorted(source_id for source_id, rule in rules.items() if not rule)
    if missing:
        raise RuntimeError(f"工作室缺少 collection_rule：{missing}")
    defaults = payload.get("collection_defaults", {}).get("exclude_url_regex", [])
    return defaults, rules


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS crawl_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            source_count INTEGER NOT NULL DEFAULT 0,
            success_count INTEGER NOT NULL DEFAULT 0,
            ready_count INTEGER NOT NULL DEFAULT 0,
            new_project_count INTEGER NOT NULL DEFAULT 0,
            error_count INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS source_state (
            studio_id TEXT PRIMARY KEY,
            studio_name TEXT NOT NULL,
            rules_status TEXT NOT NULL,
            baseline_at TEXT,
            last_success_at TEXT,
            last_fetched_count INTEGER NOT NULL DEFAULT 0,
            last_project_count INTEGER NOT NULL DEFAULT 0,
            last_status TEXT NOT NULL DEFAULT 'pending',
            last_error TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS source_runs (
            run_id INTEGER NOT NULL,
            studio_id TEXT NOT NULL,
            fetched_count INTEGER NOT NULL DEFAULT 0,
            project_count INTEGER NOT NULL DEFAULT 0,
            review_count INTEGER NOT NULL DEFAULT 0,
            excluded_count INTEGER NOT NULL DEFAULT 0,
            new_project_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            message TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (run_id, studio_id),
            FOREIGN KEY (run_id) REFERENCES crawl_runs(id)
        );
        CREATE TABLE IF NOT EXISTS baseline_items (
            studio_id TEXT NOT NULL,
            studio_name TEXT NOT NULL,
            canonical_url TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            source_published_at TEXT NOT NULL DEFAULT '',
            project_year TEXT NOT NULL DEFAULT '',
            cover_url TEXT NOT NULL DEFAULT '',
            classification TEXT NOT NULL,
            classification_reason TEXT NOT NULL DEFAULT '',
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            first_run_id INTEGER NOT NULL,
            last_run_id INTEGER NOT NULL,
            PRIMARY KEY (studio_id, canonical_url),
            FOREIGN KEY (first_run_id) REFERENCES crawl_runs(id),
            FOREIGN KEY (last_run_id) REFERENCES crawl_runs(id)
        );
        CREATE INDEX IF NOT EXISTS idx_baseline_classification
            ON baseline_items(classification, studio_id);
        """
    )


def matches(patterns: list[str], value: str) -> bool:
    return any(re.search(pattern, value, flags=re.I) for pattern in patterns)


def classify_item(
    source: dict,
    item: Item,
    default_excludes: list[str],
    rule: dict,
) -> tuple[str, str]:
    url = canonical_url(item.url)
    path = urlparse(url).path or "/"
    if matches(default_excludes + rule.get("exclude_url_regex", []), path):
        return "excluded", "命中非项目排除规则"
    if rule.get("status") != "verified":
        return "review", rule.get("reason", "该来源缺少已验证的项目识别规则")
    include_paths = rule.get("include_path_regex", [])
    include_urls = rule.get("include_url_regex", [])
    if include_paths and matches(include_paths, path):
        return "project", "命中已验证的项目路径规则"
    if include_urls and matches(include_urls, url):
        return "project", "命中已验证的项目 URL 规则"
    return "excluded", "未命中该工作室的项目识别规则"


def source_anomaly(previous_count: int, current_count: int) -> bool:
    if previous_count < 10:
        return False
    return current_count < max(2, int(previous_count * 0.4))


def upsert_item(
    connection: sqlite3.Connection,
    run_id: int,
    timestamp: str,
    source: dict,
    item: Item,
    classification: str,
    reason: str,
) -> bool:
    url = canonical_url(item.url)
    exists = connection.execute(
        "SELECT 1 FROM baseline_items WHERE studio_id = ? AND canonical_url = ?",
        (source["id"], url),
    ).fetchone()
    if exists:
        connection.execute(
            """
            UPDATE baseline_items
            SET studio_name = ?, title = ?, source_published_at = ?, cover_url = ?,
                classification = ?, classification_reason = ?, last_seen_at = ?, last_run_id = ?
            WHERE studio_id = ? AND canonical_url = ?
            """,
            (
                source["name"], item.title or "", item.published_at or "", item.cover_url or "",
                classification, reason, timestamp, run_id, source["id"], url,
            ),
        )
        return False
    project_year = item.published_at[:4] if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", item.published_at or "") else ""
    connection.execute(
        """
        INSERT INTO baseline_items (
            studio_id, studio_name, canonical_url, title, source_published_at, project_year,
            cover_url, classification, classification_reason, first_seen_at, last_seen_at,
            first_run_id, last_run_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source["id"], source["name"], url, item.title or "", item.published_at or "",
            project_year, item.cover_url or "", classification, reason, timestamp, timestamp,
            run_id, run_id,
        ),
    )
    return True


def write_report(
    connection: sqlite3.Connection,
    run_id: int,
    mode: str,
    timestamp: str,
) -> None:
    rows = connection.execute(
        """
        SELECT sr.studio_id, ss.studio_name, ss.rules_status, sr.fetched_count,
               sr.project_count, sr.review_count, sr.excluded_count,
               sr.new_project_count, sr.status, sr.message
        FROM source_runs sr
        JOIN source_state ss ON ss.studio_id = sr.studio_id
        WHERE sr.run_id = ?
        ORDER BY ss.studio_name COLLATE NOCASE
        """,
        (run_id,),
    ).fetchall()
    cumulative_projects = connection.execute(
        "SELECT COUNT(*) FROM baseline_items WHERE classification = 'project'"
    ).fetchone()[0]
    cumulative_review = connection.execute(
        "SELECT COUNT(*) FROM baseline_items WHERE classification = 'review'"
    ).fetchone()[0]
    ready = sum(row[8] == "ready" for row in rows)
    watch_only = sum(row[8] == "watch_only" for row in rows)
    needs_adapter = sum(row[8] == "needs_adapter" for row in rows)
    errors = sum(row[8] in {"error", "anomaly", "empty"} for row in rows)
    lines = [
        "# 项目基线报告",
        "",
        f"- 运行时间：{timestamp}",
        f"- 运行模式：`{mode}`",
        f"- 来源总数：{len(rows)}",
        f"- 已建立可用项目基线：{ready}",
        f"- 来源变更监控（无稳定项目结构）：{watch_only}",
        f"- 需要专用采集器：{needs_adapter}",
        f"- 错误或异常：{errors}",
        f"- 永久账本中的有效项目：{cumulative_projects}",
        f"- 待人工核验候选：{cumulative_review}",
        "",
        "| 工作室 | 规则 | 本次采集 | 有效项目 | 待核验 | 排除 | 新项目 | 状态 | 说明 |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        _, name, rule_status, fetched, projects, review, excluded, new, status, message = row
        clean = (message or "").replace("|", "\\|")
        lines.append(
            f"| {name} | {rule_status} | {fetched} | {projects} | {review} | "
            f"{excluded} | {new} | {status} | {clean} |"
        )
    lines.extend([
        "",
        "## 状态含义",
        "",
        "- `ready`：当前采集器和项目 URL 规则可以建立基线。",
        "- `watch_only`：官网无法稳定划分独立项目，只监控新链接或媒体变更。",
        "- `needs_adapter`：可以访问网站，当前返回内容还不能稳定识别为独立项目。",
        "- `anomaly`：本次采集数量异常下降，该站永久账本没有更新。",
        "- `error`：本次访问或解析失败，该站永久账本没有更新。",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "sync"), default="sync")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--only-source", action="append", default=[])
    args = parser.parse_args()

    sources = load_sources()
    if args.only_source:
        requested = set(args.only_source)
        sources = [source for source in sources if source["id"] in requested]
    all_sources = load_sources()
    default_excludes, rules = load_rules(all_sources)
    timestamp = now_iso()

    connection = sqlite3.connect(DB_PATH)
    init_db(connection)
    cursor = connection.execute(
        "INSERT INTO crawl_runs(mode, started_at, source_count) VALUES (?, ?, ?)",
        (args.mode, timestamp, len(sources)),
    )
    run_id = int(cursor.lastrowid)
    connection.commit()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(collect_source, sources))

    source_map = {source["id"]: source for source in sources}
    new_candidates: list[dict] = []
    source_alerts: list[dict] = []
    success_count = 0
    ready_count = 0
    error_count = 0

    for studio_id, items, error in results:
        source = source_map[studio_id]
        rule = rules[studio_id]
        previous = connection.execute(
            "SELECT last_fetched_count, baseline_at FROM source_state WHERE studio_id = ?",
            (studio_id,),
        ).fetchone()
        previous_count = int(previous[0]) if previous else 0
        baseline_at = previous[1] if previous else None
        connection.execute(
            """
            INSERT INTO source_state(studio_id, studio_name, rules_status)
            VALUES (?, ?, ?)
            ON CONFLICT(studio_id) DO UPDATE SET
                studio_name = excluded.studio_name,
                rules_status = excluded.rules_status
            """,
            (studio_id, source["name"], rule.get("status", "missing")),
        )

        if error:
            error_count += 1
            status = "error"
            message = error
            counts = (0, 0, 0)
        elif args.mode == "sync" and source_anomaly(previous_count, len(items)):
            error_count += 1
            status = "anomaly"
            message = f"采集数量从 {previous_count} 降至 {len(items)}，拒绝更新账本"
            counts = (0, 0, 0)
        else:
            classified: list[tuple[Item, str, str]] = []
            for item in items:
                classification, reason = classify_item(source, item, default_excludes, rule)
                classified.append((item, classification, reason))
            project_count = sum(value == "project" for _, value, _ in classified)
            review_count = sum(value == "review" for _, value, _ in classified)
            excluded_count = sum(value == "excluded" for _, value, _ in classified)
            counts = (project_count, review_count, excluded_count)
            if rule.get("status") == "watch_only":
                status = "watch_only"
                message = rule.get("reason", "")
            elif rule.get("status") != "verified":
                status = "needs_adapter"
                message = rule.get("reason", "")
            elif project_count == 0:
                status = "empty"
                message = "已验证规则没有命中任何项目"
                error_count += 1
            else:
                status = "ready"
                message = ""
                ready_count += 1
            new_count = 0
            for item, classification, reason in classified:
                inserted = upsert_item(
                    connection, run_id, timestamp, source, item, classification, reason
                )
                if inserted and classification == "project" and args.mode == "sync" and baseline_at:
                    new_count += 1
                    new_candidates.append({
                        "studio_id": studio_id,
                        "studio_name": source["name"],
                        "title": item.title,
                        "source_url": canonical_url(item.url),
                        "source_published_at": item.published_at,
                        "first_seen_at": timestamp,
                        "editorial_status": "pending",
                    })
                if (
                    inserted
                    and classification == "review"
                    and rule.get("status") == "watch_only"
                    and args.mode == "sync"
                    and baseline_at
                ):
                    source_alerts.append({
                        "studio_id": studio_id,
                        "studio_name": source["name"],
                        "title": item.title,
                        "source_url": canonical_url(item.url),
                        "first_seen_at": timestamp,
                        "reason": rule.get("reason", ""),
                    })
            success_count += 1
            connection.execute(
                """
                UPDATE source_state
                SET baseline_at = COALESCE(baseline_at, ?), last_success_at = ?,
                    last_fetched_count = ?, last_project_count = ?, last_status = ?, last_error = ''
                WHERE studio_id = ?
                """,
                (timestamp, timestamp, len(items), project_count, status, studio_id),
            )
            connection.execute(
                """
                INSERT INTO source_runs(
                    run_id, studio_id, fetched_count, project_count, review_count,
                    excluded_count, new_project_count, status, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id, studio_id, len(items), project_count, review_count,
                    excluded_count, new_count, status, message,
                ),
            )
            continue

        project_count, review_count, excluded_count = counts
        connection.execute(
            "UPDATE source_state SET last_status = ?, last_error = ? WHERE studio_id = ?",
            (status, message, studio_id),
        )
        connection.execute(
            """
            INSERT INTO source_runs(
                run_id, studio_id, fetched_count, project_count, review_count,
                excluded_count, new_project_count, status, message
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                run_id, studio_id, len(items), project_count, review_count,
                excluded_count, status, message,
            ),
        )

    finished = now_iso()
    connection.execute(
        """
        UPDATE crawl_runs
        SET finished_at = ?, success_count = ?, ready_count = ?,
            new_project_count = ?, error_count = ?
        WHERE id = ?
        """,
        (finished, success_count, ready_count, len(new_candidates), error_count, run_id),
    )
    connection.commit()
    write_report(connection, run_id, args.mode, finished)
    connection.close()

    NEW_ITEMS_PATH.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": run_id,
                "generated_at": finished,
                "items": new_candidates,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    SOURCE_ALERTS_PATH.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": run_id,
                "generated_at": finished,
                "items": source_alerts,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"run_id: {run_id}")
    print(f"ready sources: {ready_count}/{len(sources)}")
    print(f"new project candidates: {len(new_candidates)}")
    print(f"watch-only alerts: {len(source_alerts)}")
    print(f"errors or anomalies: {error_count}")
    print(f"database: {DB_PATH}")
    print(f"report: {REPORT_PATH}")
    return 0 if error_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
