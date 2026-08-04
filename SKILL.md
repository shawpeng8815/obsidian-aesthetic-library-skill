---
name: obsidian-aesthetic-library
description: Build, initialize, maintain, repair, or package a lightweight Obsidian design aesthetic library with Bases galleries, studio subscriptions, a permanent project baseline, read status, controlled tags, AI editorial review, and weekly featured issues. Use when Codex is asked to create a design inspiration library or studio-watching system, migrate or rename such a library, diagnose unrelated Base cards or missing images, process weekly design candidates, or turn this workflow into a reusable local vault structure.
---

# Obsidian aesthetic library

Create a portable library with two public surfaces—studio discovery and project reading—while keeping collection machinery under `_系统`.

## Start a new library

1. Confirm the target Obsidian Vault path and whether to use the bundled `design-studios-52` catalog or an empty catalog.
2. Refuse to initialize over a non-empty target. For an existing library, audit and migrate it instead.
3. Run:

```bash
python3 scripts/init_library.py --target "/absolute/path/to/library" --catalog design-studios-52
```

4. Re-check current official source availability before treating the bundled catalog as live truth. The catalog is a dated starting point; domains, APIs, feeds, and site structures can change.
5. Establish studio cards and the historical ledger:

```bash
python3 "/absolute/path/to/library/_系统/manage.py" setup --workers 10
```

This command may access official websites. Do not put historical projects into the public content gallery.

## Maintain an existing library

Locate its own `_系统/manage.py`; never rely on the Vault name or library folder name.

```bash
python3 "/absolute/path/to/library/_系统/manage.py" check
python3 "/absolute/path/to/library/_系统/manage.py" sync --workers 10
```

Use `fix` only to reconcile generated content-card bodies with properties. It preserves a section beginning with `## 我的笔记`. Back up an existing library before broad migrations.

## Add or change sources

Read [references/library-schema.md](references/library-schema.md) before changing fields or Base filters.

- Keep one source configuration file: `_系统/订阅源/工作室来源.json`.
- Prefer official project pages, APIs, feeds, sitemaps, or an official channel linked by the studio.
- Verify exact project boundaries before setting `collection_rule.status` to `verified`.
- Use `watch_only` for ungrouped media, homepages, and ambiguous archives.
- Leave official dates blank when unavailable.

After source changes, run `studios`, then `baseline` for newly added sources before the next `sync`. This prevents old projects from appearing as weekly additions.

## Process weekly candidates

Read [references/editorial-workflow.md](references/editorial-workflow.md) before evaluating or publishing candidates.

1. Run `sync` and inspect `本周新增候选.json`, `来源变更提醒.json`, and `项目基线报告.md`.
2. Verify each candidate on its official page.
3. Draft tags, an observation focus, and an editorial comment from visible evidence.
4. Generate a public content card only after editorial approval.
5. Keep weekly synchronization and publishing as separate actions.

## Validate the result

Run `manage.py check`, then inspect both `.base` files in Obsidian when UI access is available. Confirm:

- Studio and content counts match their folders.
- No README, dashboard, or system note appears as a card.
- Every card resolves one cover image.
- Opening a content card shows the same image, introduction, observation focus, and optional editor comment.
- Featured issue links and card metadata agree.
- Renaming the library folder does not break either Base.

Keep downloaded covers, generated databases, and harvested project notes out of the distributable Skill. Package only the template, scripts, schema, and optional source catalogs.
