# Obsidian Aesthetic Library Skill

一个帮助 Codex 在 Obsidian 中建立设计审美库的 Skill。它把设计工作室订阅、项目基线、每周更新、阅读状态、标签筛选和编辑精选整合成一套轻量的本地工作流。

## 它能建立什么

- 设计工作室画廊：集中浏览和筛选关注的工作室。
- 设计内容画廊：按品牌、字体、视觉识别、概念等维度查找项目。
- 52 家工作室的起始目录，以及可扩展的订阅源配置。
- 老项目基线与每周新增同步，避免把历史内容误判为本周更新。
- 未读/已读管理、受控标签、AI 编辑评语和“本周精选”。
- 不依赖审美库文件夹名称的检查、修复和同步脚本。

## 使用条件

- Codex
- Obsidian（启用 Bases 核心插件）
- Python 3

## 安装

将仓库克隆到 Codex 的 Skills 目录：

```bash
git clone https://github.com/shawpeng8815/obsidian-aesthetic-library-skill.git ~/.codex/skills/obsidian-aesthetic-library-skill
```

重新打开 Codex 后，可以这样使用：

```text
使用 $obsidian-aesthetic-library-skill，在我的 Obsidian Vault 中建立一套设计审美库。
```

Codex 会询问目标路径，并让你选择使用内置的 52 家工作室目录或从空目录开始。

## 说明

仓库只包含可复用的模板、脚本、字段规范和起始目录，不包含抓取后的项目内容与图片。工作室官网、Feed 和页面结构可能变化，正式同步前应重新验证来源。

Skill 的完整执行规则见 [`SKILL.md`](SKILL.md)。
