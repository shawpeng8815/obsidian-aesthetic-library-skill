#!/usr/bin/env python3
"""根据单一工作室配置生成 Obsidian 工作室卡和封面。"""

from __future__ import annotations

import concurrent.futures
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = ROOT / "_系统" / "订阅源" / "工作室来源.json"
STUDIOS_DIR = ROOT / "工作室"
ASSETS_DIR = ROOT / "_系统" / "assets" / "studios"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"


def yaml_string(value: object) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def safe_filename(name: str) -> str:
    name = name.replace(" / ", " ").replace("/", "-").replace(":", "-")
    return re.sub(r"[\\?*<>|]", "-", name).strip(". ")


def fallback_svg(source: dict, path: Path) -> None:
    name = html.escape(source["name"])
    region = html.escape(source["region"])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
<rect width="1200" height="675" fill="#171717"/>
<rect x="46" y="46" width="1108" height="583" rx="12" fill="none" stroke="#454545" stroke-width="2"/>
<text x="78" y="342" fill="#f2f2f2" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="700">{name}</text>
<text x="80" y="405" fill="#a8a8a8" font-family="Arial, Helvetica, sans-serif" font-size="26">{region} · DESIGN STUDIO</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def download_cover(source: dict) -> tuple[str, str]:
    jpg_path = ASSETS_DIR / f"studio-{source['id']}.jpg"
    svg_path = ASSETS_DIR / f"studio-{source['id']}.svg"
    pentagram_cover = ROOT / "_系统" / "assets" / "studios" / "studio-pentagram.png"
    if source["id"] == "pentagram" and pentagram_cover.exists():
        return source["id"], pentagram_cover.name
    if jpg_path.exists() and jpg_path.stat().st_size > 1000:
        return source["id"], jpg_path.name
    if svg_path.exists() and svg_path.stat().st_size > 1000:
        return source["id"], svg_path.name
    url = source.get("cover_url", "")
    if url and not jpg_path.exists():
        with tempfile.NamedTemporaryFile(suffix=".image") as temp:
            curl = subprocess.run([
                "curl", "-L", "--silent", "--show-error", "--max-time", "30",
                "--max-filesize", "15000000", "-A", USER_AGENT, "-o", temp.name, url,
            ], capture_output=True)
            if curl.returncode == 0 and Path(temp.name).stat().st_size > 1000:
                sips = subprocess.run([
                    "sips", "-s", "format", "jpeg", "-Z", "1200", temp.name,
                    "--out", str(jpg_path),
                ], capture_output=True)
                if sips.returncode == 0 and jpg_path.exists() and jpg_path.stat().st_size > 1000:
                    return source["id"], jpg_path.name
                jpg_path.unlink(missing_ok=True)
    fallback_svg(source, svg_path)
    return source["id"], svg_path.name


def source_card(source: dict, cover_name: str) -> str:
    content_url = source.get("content_url", source["website"])
    disciplines = source.get("disciplines", [])
    method_traits = source.get("method_traits", [])
    lines = [
        "---",
        "type: design-studio",
        f"region: {yaml_string(source['region'])}",
        f"positioning: {yaml_string(source.get('positioning', ''))}",
        f"observation_value: {yaml_string(source.get('observation_value', ''))}",
        f"media_structure: {yaml_string(source.get('media_structure', ''))}",
        "method_traits:",
        *[f"  - {yaml_string(item)}" for item in method_traits],
        f"studio_intro: {yaml_string(source.get('studio_intro', ''))}",
        "disciplines:",
        *[f"  - {yaml_string(item)}" for item in disciplines],
        f"website: {yaml_string(source['website'])}",
        f"cover: \"[[{cover_name}]]\"",
        "---",
        "",
        f"# {source['name']}",
        "",
        f"![{source['name']} 官网封面]({cover_name})",
        "",
        "## 观察档案",
        "",
        source.get("positioning", ""),
        "",
        f"- 观察价值：{source.get('observation_value', '')}",
        f"- 方法特征：{' / '.join(method_traits)}",
        f"- 媒介结构：{source.get('media_structure', '')}",
        "",
        "> 观察价值、方法特征和媒介结构是为审美观察做的编辑判断，不是工作室官方标签。",
        "",
        "## 工作室简介",
        "",
        source.get("studio_intro", ""),
        "",
        f"- 官网项目方向：{' / '.join(disciplines)}",
        "",
    ]
    lines.extend([
        "## 官方来源",
        "",
        f"- [官方网站]({source['website']})",
        f"- [内容入口]({content_url})",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    overrides = payload.get("overrides", {})
    sources: list[dict] = []
    for raw in payload["sources"]:
        source = dict(raw)
        source.update(overrides.get(source["id"], {}))
        sources.append(source)

    STUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        cover_map = dict(executor.map(download_cover, sources))

    for source in sources:
        path = STUDIOS_DIR / f"{safe_filename(source['name'])}.md"
        path.write_text(source_card(source, cover_map[source["id"]]), encoding="utf-8")
    jpg_count = len(list(ASSETS_DIR.glob("*.jpg")))
    svg_count = len(list(ASSETS_DIR.glob("*.svg")))
    print(f"studio cards: {len(list(STUDIOS_DIR.glob('*.md')))}")
    png_count = len(list(ASSETS_DIR.glob("*.png")))
    print(f"covers: {jpg_count} jpg + {png_count} png + {svg_count} svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
