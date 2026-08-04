# Library schema

Read this file when adding sources, creating content cards, changing fields, or diagnosing a Base view.

## Folder contract

```text
library/
├─ 设计工作室画廊.base
├─ 设计内容画廊.base
├─ 工作室/
├─ 内容/
├─ 本周精选/
└─ _系统/
   ├─ manage.py
   ├─ assets/{studios,content}/
   ├─ scripts/
   └─ 订阅源/
```

Keep public reading surfaces outside `_系统`. Keep collection rules, databases, reports, and candidates inside it.

## Studio source

Store all source, profile, gallery, and collection fields in the single file `_系统/订阅源/工作室来源.json`.

Required fields per source:

- Identity: `id`, `name`, `region`, `website`, `content_url`
- Gallery: `studio_intro`, `disciplines`, `positioning`, `observation_value`, `method_traits`, `media_structure`
- Collection: `subscription_method`, adapter fields when needed, and `collection_rule`

Use a verified project rule only when an official URL or ID reliably represents one project. Use `watch_only` when a site exposes media blocks, a homepage, or an ungrouped archive. Never present a media block as a project.

## Studio note

The generator writes these public properties:

```yaml
type: design-studio
region: ""
positioning: ""
observation_value: ""
media_structure: ""
method_traits: []
studio_intro: ""
disciplines: []
website: ""
cover: "[[asset.jpg]]"
```

## Content note

Use this minimal property set:

```yaml
studio: "[[Studio note|Display name]]"
published_at: "" # leave blank unless the official source gives a date
read: false
project_intro: "Original official introduction followed directly by Chinese translation when needed."
observation_focus: "A specific visual question worth observing."
discipline_tags: []
concept_tags: []
editorial_status: "基础样本"
source_url: "https://official.example/project"
cover: "[[asset.jpg]]"
```

Add `featured_issue`, `featured_order`, and `editor_comment` only after selection. Keep a user's personal writing under `## 我的笔记`; the formatter preserves that section.

## Base rules

Scope Bases relative to their own location:

```yaml
file.inFolder(this.file.folder + "/内容")
file.inFolder(this.file.folder + "/工作室")
```

Never write a vault name, absolute path, or library folder name into a Base filter. Use `contains` for list-property filters such as design fields and concept tags.
