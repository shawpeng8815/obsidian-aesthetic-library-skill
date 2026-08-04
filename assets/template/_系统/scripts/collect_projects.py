#!/usr/bin/env python3
"""从不同官网结构采集并标准化项目列表。"""

from __future__ import annotations

import html
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse, urlunparse

from audit_sources import fetch, parse_html, same_site


STATIC_PARTS = {
    "about", "contact", "contacts", "privacy", "terms", "career", "careers",
    "jobs", "services", "service", "studio", "team", "people", "info",
    "instagram", "facebook", "linkedin", "shop", "cart", "search", "tag",
    "category", "author", "feed", "rss", "sitemap.xml",
}
ASSET_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".pdf",
    ".zip", ".mp4", ".mov", ".mp3", ".woff", ".woff2", ".css", ".js",
}


@dataclass
class Item:
    url: str
    title: str
    published_at: str = ""
    cover_url: str = ""


def canonical_url(url: str) -> str:
    parsed = urlparse(url)
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


def parse_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        pass
    match = re.search(r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})", value)
    if match:
        try:
            return date(int(match[1]), int(match[2]), int(match[3])).isoformat()
        except ValueError:
            return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return ""


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def feed_items(source: dict) -> list[Item]:
    response = fetch(source["feed_url"])
    if response.status != 200:
        raise RuntimeError(f"Feed HTTP {response.status}")
    root = ET.fromstring(response.body)
    items: list[Item] = []
    for node in root.iter():
        if local_name(node.tag) not in {"item", "entry"}:
            continue
        title = ""
        link = ""
        published = ""
        for child in list(node):
            name = local_name(child.tag)
            if name == "title" and child.text:
                title = " ".join(child.text.split())
            elif name == "link":
                href = child.attrib.get("href", "")
                rel = child.attrib.get("rel", "alternate")
                if href and rel in {"alternate", ""}:
                    link = href
                elif child.text and not link:
                    link = child.text.strip()
            elif name in {"pubdate", "published", "updated", "date"} and child.text and not published:
                published = parse_date(child.text)
        if link:
            items.append(Item(canonical_url(link), title or title_from_url(link), published))
    return unique_items(items)


def sitemap_items(source: dict) -> list[Item]:
    response = fetch(source.get("sitemap_url") or source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"Sitemap HTTP {response.status}")
    text = response.body.decode("utf-8", "replace")
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", text, flags=re.I | re.S)
    child_sitemaps = [url.strip() for url in urls if urlparse(url.strip()).path.lower().endswith(".xml")]
    if child_sitemaps:
        expanded: list[str] = []
        for child in child_sitemaps[:12]:
            child_response = fetch(child)
            if child_response.status == 200:
                child_text = child_response.body.decode("utf-8", "replace")
                expanded.extend(re.findall(r"<loc>\s*(.*?)\s*</loc>", child_text, flags=re.I | re.S))
        if expanded:
            urls = expanded
    tokens = ("/work/", "/works/", "/project/", "/projects/", "/case/", "/cases/")
    return unique_items([
        Item(canonical_url(url.strip().replace("&amp;", "&")), title_from_url(url))
        for url in urls
        if any(token in urlparse(url).path.lower() for token in tokens)
    ])


def first_image_url(value: object) -> str:
    if isinstance(value, dict):
        if isinstance(value.get("url"), str) and re.search(r"\.(?:jpe?g|png|webp|avif)(?:\?|$)", value["url"], re.I):
            return value["url"]
        for key in ("medium", "large", "thumbnail", "image", "cover", "media", "gallery", "preview", "formats", "data", "attributes"):
            if key in value:
                found = first_image_url(value[key])
                if found:
                    return found
        for child in value.values():
            found = first_image_url(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = first_image_url(child)
            if found:
                return found
    return ""


def api_items(source: dict) -> list[Item]:
    response = fetch(source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"API HTTP {response.status}")
    data = json.loads(response.body)
    adapter = source.get("adapter")
    items: list[Item] = []
    if adapter == "naeo":
        for row in data:
            item_id = str(row.get("id") or row.get("_id") or "")
            if not item_id:
                continue
            items.append(Item(
                f"{source['website']}?project={item_id}",
                row.get("title") or item_id,
                parse_date(row.get("createdAt", "")),
                first_image_url(row.get("cover") or row),
            ))
    elif adapter == "workbyworks":
        for row in data.get("data", []):
            attrs = row.get("attributes", {})
            slug = attrs.get("slug") or str(row.get("id", ""))
            if not slug:
                continue
            items.append(Item(
                f"https://workbyworks.studio/works/{slug}",
                attrs.get("title") or title_from_url(slug),
                parse_date(attrs.get("date_for_sort") or attrs.get("publishedAt", "")),
                first_image_url(attrs.get("gallery") or attrs),
            ))
    elif adapter == "actual_source":
        for row in data:
            slug = row.get("slug", "")
            if not slug:
                continue
            items.append(Item(
                f"https://actualsource.work/projects/{slug}",
                row.get("title") or title_from_url(slug),
                "",
                first_image_url(row.get("media") or row),
            ))
    elif adapter == "mint":
        for row in data:
            slug = str(row.get("project_url") or row.get("url") or "").strip("/")
            if not slug:
                continue
            image = (
                row.get("thumb_meta", {})
                .get("thumbnail_crop", {})
                .get("imageModel", {})
            )
            image_hash = str(image.get("hash") or "")
            image_name = str(image.get("name") or "")
            cover = ""
            if image_hash and image_name:
                cover = f"https://freight.cargo.site/t/original/i/{image_hash}/{quote(image_name)}"
            items.append(Item(
                f"https://mintdesign.cn/{slug}",
                strip_tags(str(row.get("title_no_html") or row.get("title") or title_from_url(slug))),
                "",
                cover,
            ))
    elif adapter == "arena":
        for row in data.get("contents", []):
            item_id = row.get("id")
            if not item_id:
                continue
            items.append(Item(
                f"https://www.are.na/block/{item_id}",
                row.get("title") or row.get("generated_title") or f"Are.na Block {item_id}",
                parse_date(row.get("connected_at") or row.get("created_at", "")),
                first_image_url(row.get("image") or row),
            ))
    else:
        raise RuntimeError(f"未知 API adapter: {adapter}")
    return unique_items(items)


def omse_items(source: dict) -> list[Item]:
    response = fetch(source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"页面 HTTP {response.status}")
    text = response.body.decode("utf-8", "replace")
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text, re.S)
    if not match:
        raise RuntimeError("未找到 __NEXT_DATA__")
    data = json.loads(match.group(1))
    found: dict[str, Item] = {}

    def walk(value: object) -> None:
        if isinstance(value, dict):
            slug = value.get("slug")
            template = value.get("intendedTemplate") or value.get("template")
            url = str(value.get("url") or "")
            is_project = template == "project" or "/omse/work/" in url
            if slug and is_project:
                official = f"https://www.omse.co/work/{slug}"
                found.setdefault(slug, Item(
                    official,
                    str(value.get("title") or title_from_url(slug)),
                    parse_date(str(value.get("date") or "")),
                    first_image_url(value),
                ))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    return list(found.values())


def whatever_items(source: dict) -> list[Item]:
    response = fetch(source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"页面 HTTP {response.status}")
    text = response.body.decode("utf-8", "replace")
    match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', text, re.S)
    if not match:
        raise RuntimeError("未找到 __NEXT_DATA__")
    data = json.loads(match.group(1))
    works = data.get("props", {}).get("pageProps", {}).get("works", [])
    items: list[Item] = []
    for row in works:
        slug = str(row.get("slug") or "").strip()
        if not slug:
            continue
        items.append(Item(
            f"https://whatever.co/work/{slug}/",
            html.unescape(strip_tags(str(row.get("title") or title_from_url(slug)))),
            parse_date(str(row.get("date") or row.get("publishedAt") or "")),
            first_image_url(row),
        ))
    return unique_items(items)


def studio_mut_items(source: dict) -> list[Item]:
    response = fetch(source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"页面 HTTP {response.status}")
    text = response.body.decode("utf-8", "replace")
    match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', text, re.S)
    if not match:
        raise RuntimeError("未找到 __NEXT_DATA__")
    data = json.loads(match.group(1))
    sections = data.get("props", {}).get("pageProps", {}).get("sections", [])
    items: list[Item] = []
    for section in sections:
        section_title = str(section.get("title") or section.get("__typename") or "").strip()
        slides = section.get("slidesCollection", {}).get("items", [])
        for slide in slides:
            media = slide.get("media") if isinstance(slide.get("media"), dict) else slide
            asset_id = str(media.get("sys", {}).get("id") or "").strip()
            if not asset_id:
                continue
            title = str(slide.get("title") or media.get("title") or section_title or asset_id)
            items.append(Item(
                f"https://www.studiomut.com/?asset={asset_id}",
                strip_tags(title),
                "",
                first_image_url(media),
            ))
    return unique_items(items)


def strip_tags(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def html_media_items(source: dict) -> list[Item]:
    response = fetch(source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"页面 HTTP {response.status}")
    text = response.body.decode("utf-8", "replace")
    adapter = source.get("adapter")
    items: list[Item] = []
    if adapter == "uma":
        pattern = re.compile(r'<img[^>]+src="([^"]*ph_pj(\d+)_pc\.[^"]+)"[^>]+alt="([^"]+)"', re.I)
        for image_url, number, title in pattern.findall(text):
            items.append(Item(
                f"{source['website']}?project={number}",
                html.unescape(title),
                "",
                response.final_url.rstrip("/") + "/" + image_url.lstrip("/"),
            ))
    elif adapter == "other_means":
        slides = re.findall(r'<div class="swiper-slide">(.*?)</div>\s*</div>?', text, re.I | re.S)
        for index, slide in enumerate(slides):
            srcset = re.search(r'srcset="([^"]+)"', slide, re.I)
            caption = re.search(r'<figcaption>\s*<p>(.*?)</p>', slide, re.I | re.S)
            if not caption:
                continue
            title = strip_tags(caption.group(1))
            cover = srcset.group(1).split(",")[0].strip().split(" ")[0] if srcset else ""
            slug = hashlib.sha1(title.encode()).hexdigest()[:10]
            items.append(Item(f"{source['website']}?project={slug}", title, "", cover))
        for title in re.findall(r'<span class="item-title">\s*(.*?)\s*</span>', text, re.I | re.S):
            clean = strip_tags(title)
            slug = hashlib.sha1(clean.encode()).hexdigest()[:10]
            items.append(Item(f"{source['website']}?project={slug}", clean))
    elif adapter == "mouthwash":
        starts = list(re.finditer(
            r'<a\s+href="([^"]*/project/[^"]+)"\s+class="work-card"',
            text,
            re.I,
        ))
        for index, match in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            block = text[match.start():end]
            title_match = re.search(
                r'class="work-card-title"[^>]*>\s*(.*?)\s*</div>',
                block,
                re.I | re.S,
            )
            cover_match = re.search(r'data-srcset="([^"]+)"', block, re.I)
            url = canonical_url(urljoin(response.final_url, html.unescape(match.group(1))))
            title = strip_tags(title_match.group(1)) if title_match else title_from_url(url)
            cover = ""
            if cover_match:
                cover = html.unescape(cover_match.group(1)).split(",")[0].strip().split(" ")[0]
            items.append(Item(url, title, "", cover))
    elif adapter == "polymode":
        starts = list(re.finditer(
            r'<a\s+href="([^"]*/project/[^"]+)"\s+class="project-grid__link"',
            text,
            re.I,
        ))
        for index, match in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            block = text[match.start():end]
            title_match = re.search(
                r'class="project-grid__title[^"]*"[^>]*>\s*(.*?)\s*</h2>',
                block,
                re.I | re.S,
            )
            cover_match = re.search(r'data-src="([^"]+)"', block, re.I)
            url = canonical_url(html.unescape(match.group(1)))
            title = strip_tags(title_match.group(1)) if title_match else title_from_url(url)
            cover = html.unescape(cover_match.group(1)) if cover_match else ""
            items.append(Item(url, title, "", cover))
    else:
        raise RuntimeError(f"未知 HTML adapter: {adapter}")
    return unique_items(items)


def title_from_url(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    slug = re.sub(r"[-_]+", " ", slug)
    return " ".join(part.capitalize() for part in slug.split()) or "Untitled"


def page_items(source: dict) -> list[Item]:
    response = fetch(source["content_url"])
    if response.status != 200:
        raise RuntimeError(f"页面 HTTP {response.status}")
    parser = parse_html(response)
    current = canonical_url(response.final_url)
    homepage = canonical_url(source["site_final_url"] if source.get("site_final_url") else source["website"])
    candidates: list[Item] = []
    for raw_url, text in parser.links:
        if not raw_url.startswith(("http://", "https://")) or not same_site(raw_url, response.final_url):
            continue
        url = canonical_url(raw_url)
        if url in {current, homepage}:
            continue
        parsed = urlparse(url)
        if Path(parsed.path.lower()).suffix in ASSET_EXTENSIONS:
            continue
        parts = {part.lower() for part in parsed.path.split("/") if part}
        if not parts or parts & STATIC_PARTS:
            continue
        title = " ".join(text.split()) or title_from_url(url)
        if len(title) < 2:
            continue
        candidates.append(Item(url, title))
    return unique_items(candidates)


def unique_items(items: list[Item]) -> list[Item]:
    result: dict[str, Item] = {}
    for item in items:
        result.setdefault(canonical_url(item.url), item)
    return list(result.values())


def collect_source(source: dict) -> tuple[str, list[Item], str]:
    try:
        method = source.get("subscription_method", "")
        if method == "feed":
            items = feed_items(source)
        elif method == "sitemap":
            items = sitemap_items(source)
        elif method == "api":
            items = api_items(source)
        elif method == "embedded_data" and source.get("adapter") == "omse":
            items = omse_items(source)
        elif method == "embedded_data" and source.get("adapter") == "whatever":
            items = whatever_items(source)
        elif method == "embedded_data" and source.get("adapter") == "studio_mut":
            items = studio_mut_items(source)
        elif method == "html_media":
            items = html_media_items(source)
        else:
            items = page_items(source)
        return source["id"], items, ""
    except Exception as exc:  # 单站异常不应中断其他 52 家
        return source["id"], [], str(exc)
