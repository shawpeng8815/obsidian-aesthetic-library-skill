#!/usr/bin/env python3
"""核验设计工作室官网，发现 Feed、内容入口和站点封面。"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = ROOT / "_系统" / "订阅源" / "工作室来源.json"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
)
MARKER = "\n__OBSIDIAN_SOURCE_AUDIT__"
COMMON_FEEDS = ("feed", "feed.xml", "rss", "rss.xml", "atom.xml", "index.xml")
INDEX_NAMES = {
    "work", "works", "project", "projects", "case", "cases", "portfolio",
    "news", "journal", "stories", "archive", "all", "creative-studio",
}


@dataclass
class Response:
    requested_url: str
    final_url: str
    status: int
    content_type: str
    body: bytes
    error: str = ""


def fetch(url: str, timeout: int = 25, attempts: int = 2) -> Response:
    fmt = MARKER + "%{http_code}|%{url_effective}|%{content_type}"
    command = [
        "curl", "-L", "--silent", "--show-error", "--compressed",
        "--connect-timeout", "8", "--max-time", str(timeout),
        "--max-redirs", "10", "--max-filesize", "12000000",
        "-A", USER_AGENT, "-w", fmt, url,
    ]
    response = Response(url, url, 0, "", b"", "")
    for attempt in range(attempts):
        result = subprocess.run(command, capture_output=True)
        output = result.stdout
        marker = output.rfind(MARKER.encode())
        if marker == -1:
            response = Response(
                url, url, 0, "", output,
                result.stderr.decode("utf-8", "replace").strip(),
            )
        else:
            body = output[:marker]
            meta = output[marker + len(MARKER):].decode("utf-8", "replace")
            status_text, final_url, content_type = (meta.split("|", 2) + ["", ""])[:3]
            try:
                status = int(status_text)
            except ValueError:
                status = 0
            response = Response(
                url, final_url or url, status, content_type, body,
                result.stderr.decode("utf-8", "replace").strip(),
            )
        if response.status not in {0, 429} and response.status < 500:
            return response
        if attempt + 1 < attempts:
            time.sleep(0.5)
    return response


class DiscoveryParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.in_title = False
        self.links: list[tuple[str, str]] = []
        self.feed_links: list[tuple[str, str]] = []
        self.og_image = ""
        self.image_candidates: list[str] = []
        self._anchor_href = ""
        self._anchor_text: list[str] = []

    def handle_starttag(self, tag: str, attrs_list):
        attrs = {str(k).lower(): (v or "") for k, v in attrs_list}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            key = (attrs.get("property") or attrs.get("name") or "").lower()
            if key in {"og:image", "twitter:image", "twitter:image:src"} and not self.og_image:
                self.og_image = urljoin(self.base_url, attrs.get("content", ""))
        elif tag == "link":
            rel = attrs.get("rel", "").lower()
            mime = attrs.get("type", "").lower()
            href = attrs.get("href", "")
            if "alternate" in rel and href and any(x in mime for x in ("rss", "atom", "feed+json")):
                self.feed_links.append((urljoin(self.base_url, href), mime))
        elif tag == "a":
            self._anchor_href = urljoin(self.base_url, attrs.get("href", ""))
            self._anchor_text = []
        elif tag in {"img", "source"}:
            raw = (
                attrs.get("src") or attrs.get("data-src") or
                attrs.get("data-lazy-src") or attrs.get("srcset", "").split(",")[0].strip().split(" ")[0]
            )
            if raw:
                candidate = urljoin(self.base_url, raw)
                low = candidate.lower()
                if not any(token in low for token in ("logo", "icon", "favicon", "avatar", ".svg")):
                    self.image_candidates.append(candidate)

    def handle_data(self, data: str):
        if self.in_title:
            self.title_parts.append(data)
        if self._anchor_href:
            self._anchor_text.append(data)

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "a" and self._anchor_href:
            text = " ".join(" ".join(self._anchor_text).split())
            self.links.append((self._anchor_href, text))
            self._anchor_href = ""
            self._anchor_text = []

    @property
    def title(self) -> str:
        return " ".join(" ".join(self.title_parts).split())

    @property
    def cover_image(self) -> str:
        return self.og_image or (self.image_candidates[0] if self.image_candidates else "")


def parse_html(response: Response) -> DiscoveryParser:
    parser = DiscoveryParser(response.final_url)
    parser.feed(response.body.decode("utf-8", "replace"))
    return parser


def same_site(a: str, b: str) -> bool:
    host_a = urlparse(a).netloc.lower().removeprefix("www.")
    host_b = urlparse(b).netloc.lower().removeprefix("www.")
    return host_a == host_b


def content_score(url: str, text: str, base_url: str) -> int:
    if not same_site(url, base_url):
        return -100
    path = urlparse(url).path.lower().rstrip("/")
    haystack = f"{path} {text.lower()}"
    if not path or path in {"/#", "#"}:
        return -20
    positive = {
        "work": 13, "works": 14, "project": 13, "projects": 15,
        "case": 10, "cases": 12, "portfolio": 13, "news": 9,
        "journal": 8, "stories": 7, "archive": 6, "selected": 4,
        "仕事": 12, "実績": 12, "作品": 12, "项目": 12, "項目": 12,
    }
    negative = {
        "about": -9, "contact": -12, "shop": -9, "career": -10,
        "privacy": -15, "terms": -15, "instagram": -20, "service": -5,
    }
    score = 0
    for token, weight in positive.items():
        if token in haystack:
            score += weight
    for token, weight in negative.items():
        if token in haystack:
            score += weight
    parts = [part for part in path.split("/") if part]
    depth = len(parts)
    if depth == 1:
        score += 25 if parts[0].lower() in INDEX_NAMES else 3
    elif depth >= 2:
        # 订阅监控必须优先选列表页；具体项目页即使锚文本含有 Work，仍要显著降权。
        score -= 12 * (depth - 1)
    return score


def choose_content_url(parser: DiscoveryParser, base_url: str) -> str:
    candidates: dict[str, int] = {}
    for url, text in parser.links:
        clean = url.split("#", 1)[0]
        score = content_score(clean, text, base_url)
        candidates[clean] = max(candidates.get(clean, -100), score)
    if not candidates:
        return base_url
    url, score = max(candidates.items(), key=lambda item: (item[1], -len(item[0])))
    return url if score >= 7 else base_url


def is_index_url(url: str, homepage_url: str) -> bool:
    if url.rstrip("/") == homepage_url.rstrip("/"):
        return False
    parts = [part.lower() for part in urlparse(url).path.split("/") if part]
    return len(parts) == 1 and parts[0] in INDEX_NAMES


def discover_sitemap(homepage_url: str) -> tuple[str, list[str]]:
    root = f"{urlparse(homepage_url).scheme}://{urlparse(homepage_url).netloc}/"
    sitemap_url = urljoin(root, "sitemap.xml")
    response = fetch(sitemap_url, timeout=18)
    if response.status != 200 or b"<loc" not in response.body[:12000000].lower():
        return "", []
    text = response.body.decode("utf-8", "replace")
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", text, flags=re.I | re.S)
    urls = [re.sub(r"&amp;", "&", url.strip()) for url in urls]
    child_sitemaps = [url for url in urls if urlparse(url).path.lower().endswith(".xml")]
    if child_sitemaps:
        expanded: list[str] = []
        for child in child_sitemaps[:8]:
            child_response = fetch(child, timeout=18)
            if child_response.status != 200:
                continue
            child_text = child_response.body.decode("utf-8", "replace")
            expanded.extend(re.findall(r"<loc>\s*(.*?)\s*</loc>", child_text, flags=re.I | re.S))
        if expanded:
            urls = [re.sub(r"&amp;", "&", url.strip()) for url in expanded]
    return response.final_url, list(dict.fromkeys(urls))


def likely_project_urls(urls: list[str], homepage_url: str) -> list[str]:
    tokens = ("/work/", "/works/", "/project/", "/projects/", "/case/", "/cases/")
    return [
        url for url in urls
        if same_site(url, homepage_url) and any(token in urlparse(url).path.lower() for token in tokens)
    ]


def looks_like_feed(response: Response) -> tuple[bool, str]:
    start = response.body[:5000].lstrip().lower()
    content_type = response.content_type.lower()
    if response.status != 200:
        return False, ""
    if b"<rss" in start or b"<rdf:rdf" in start:
        return True, "RSS"
    if re.search(br"<feed(?:\s|>)", start):
        return True, "Atom"
    if "feed+json" in content_type and start.startswith(b"{"):
        return True, "JSON Feed"
    return False, ""


def discover_feed(parser: DiscoveryParser, homepage_url: str) -> tuple[str, str]:
    candidates: list[str] = []
    for url, _mime in parser.feed_links:
        if url not in candidates:
            candidates.append(url)
    root = f"{urlparse(homepage_url).scheme}://{urlparse(homepage_url).netloc}/"
    for path in COMMON_FEEDS:
        url = urljoin(root, path)
        if url not in candidates:
            candidates.append(url)
    for url in candidates:
        response = fetch(url, timeout=15)
        valid, feed_type = looks_like_feed(response)
        if valid:
            return response.final_url, feed_type
    return "", ""


def audit_source(source: dict) -> dict:
    result = dict(source)
    response = fetch(source["website"])
    result["source_checked_at"] = date.today().isoformat()
    result["site_http_status"] = response.status
    result["site_final_url"] = response.final_url
    if response.status != 200 or not response.body:
        result.update({
            "audit_status": "site_error",
            "subscription_method": "disabled",
            "subscription_status": f"官网检查失败：HTTP {response.status or '网络错误'}",
            "audit_error": response.error,
        })
        return result

    parser = parse_html(response)
    result.pop("audit_error", None)
    content_url = choose_content_url(parser, response.final_url)
    feed_url, feed_type = discover_feed(parser, response.final_url)
    sitemap_url, sitemap_urls = discover_sitemap(response.final_url)
    project_urls = likely_project_urls(sitemap_urls, response.final_url)
    result.update({
        "site_title": parser.title,
        "content_url": content_url,
        "cover_url": parser.cover_image,
        "feed_url": feed_url,
        "feed_type": feed_type,
        "sitemap_url": sitemap_url,
        "sitemap_item_count": len(project_urls),
    })
    if feed_url:
        result.update({
            "audit_status": "ready_rss",
            "subscription_method": "feed",
            "subscription_status": f"可订阅：{feed_type}",
        })
    elif is_index_url(content_url, response.final_url):
        result.update({
            "audit_status": "ready_page_monitor",
            "subscription_method": "page_monitor",
            "subscription_status": "无可用 Feed；监控作品/新闻页面",
        })
    elif sitemap_url and len(project_urls) >= 2:
        result.update({
            "audit_status": "ready_sitemap",
            "subscription_method": "sitemap",
            "subscription_status": f"无可用 Feed；监控 Sitemap 中的 {len(project_urls)} 个项目链接",
            "content_url": sitemap_url,
        })
    else:
        result.update({
            "audit_status": "manual_review",
            "subscription_method": "pending",
            "subscription_status": "官网正常；未自动识别稳定内容入口",
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    sources = payload["sources"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        audited = list(executor.map(audit_source, sources))
    overrides = payload.get("overrides", {})
    for source in audited:
        source.update(overrides.get(source["id"], {}))
    payload["audited_at"] = date.today().isoformat()
    payload["sources"] = audited
    temp_path = SOURCES_PATH.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(SOURCES_PATH)

    counts: dict[str, int] = {}
    for source in audited:
        status = source.get("audit_status", "unknown")
        counts[status] = counts.get(status, 0) + 1
        print(f"{source['name']}: {status} | {source.get('content_url', '')} | {source.get('feed_url', '')}")
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
