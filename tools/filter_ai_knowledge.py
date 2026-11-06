#!/usr/bin/env python3
"""Remove non-article entries from the already imported AI knowledge pages."""

import json
import re
from html import escape
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

from build_ai_knowledge import rewrite_markdown_links
from import_ai_knowledge_site import article_page, localize_body


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "ai-knowledge-data.js"
ARTICLE_ROOT = ROOT / "ai-knowledge"
SITEMAP = ROOT / "sitemap.xml"
SOURCE_DIR = ROOT.parent / "Awesome-AI-Pedia"
COVER_DIR = ROOT / "assets" / "ai-knowledge-covers"


def article_title(markdown_text: str, fallback: str) -> str:
    match = re.search(r"^#{1,6}\s+(.+?)\s*$", markdown_text, re.MULTILINE)
    return re.sub(r"[`*_]", "", match.group(1)).strip() if match else fallback


def article_cover(article: dict) -> str:
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", article["url"].split("/")[-1].replace(".html", "")).strip("-")
    target = COVER_DIR / f"{slug}.svg"
    palettes = {
        "claudeCode": ("#f08c68", "#332945", "CODE"), "cursor": ("#5d76e8", "#18264c", "CURSOR"),
        "codex": ("#55b69b", "#173b42", "CODEX"), "mcp": ("#d99b54", "#413025", "MCP"),
        "skills": ("#8d73c5", "#292344", "SKILLS"), "prompt": ("#d97391", "#402338", "PROMPT"),
        "AI视频": ("#54a8c8", "#183447", "VIDEO"), "rules": ("#6d92b9", "#203248", "RULES"),
    }
    accent, dark, label = palettes.get(article["category"], ("#e88b62", "#293552", "AI"))
    title = escape(article["title"][:28])
    category = escape(article["category"][:18])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 500" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">{category} 主题配图</desc>
<rect width="1200" height="500" fill="{dark}"/><path d="M0 410 C230 300 350 470 590 350 S970 250 1200 330 V500 H0Z" fill="{accent}" opacity=".22"/>
<circle cx="1000" cy="100" r="170" fill="{accent}" opacity=".16"/><path d="M770 0 L1200 0 L1200 500" fill="none" stroke="{accent}" stroke-width="2" opacity=".55"/>
<path d="M800 390 L1030 160 M910 430 L1130 210" stroke="{accent}" stroke-width="3" opacity=".7"/><text x="70" y="92" fill="{accent}" font-family="Arial,sans-serif" font-size="24" font-weight="700" letter-spacing="5">{label}</text><text x="70" y="180" fill="#f7f5ef" font-family="Arial,'Microsoft YaHei',sans-serif" font-size="42" font-weight="700">{title}</text><text x="70" y="235" fill="#c7cde0" font-family="Arial,'Microsoft YaHei',sans-serif" font-size="20">{category} · AI Knowledge</text><rect x="70" y="278" width="110" height="5" rx="2" fill="{accent}"/></svg>'''
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8")
    return f"assets/ai-knowledge-covers/{target.name}"


def keep_article(article: dict) -> bool:
    page = ROOT / article["url"]
    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
    body = soup.select_one(".ai-body")
    text = " ".join(body.get_text(" ", strip=True).split()) if body else ""
    external_links = len(body.select('a[href^="http://"], a[href^="https://"]')) if body else 0
    title = article["title"].strip().lower()
    if title == "index":
        return False
    if len(text) < 120:
        return False
    if len(text) < 260 and external_links >= 2:
        return False
    return True


def main() -> None:
    match = re.search(r"window\.aiKnowledgeArticles\s*=\s*(\[.*\]);", DATA.read_text(encoding="utf-8"), re.S)
    if not match:
        raise SystemExit("AI article data not found")
    articles = json.loads(match.group(1))
    kept = [article for article in articles if keep_article(article)]
    removed = [article for article in articles if article not in kept]
    for article in kept:
        target = ROOT / article["url"]
        source_file = SOURCE_DIR / article["path"]
        if source_file.is_file():
            source_text = source_file.read_text(encoding="utf-8")
            article["title"] = article_title(source_text, article["title"])
            article["image"] = article_cover(article)
            rendered = markdown.markdown(
                rewrite_markdown_links(source_text, article["path"]),
                extensions=["fenced_code", "tables", "sane_lists"],
                output_format="html5",
            )
            clean_body = localize_body(rendered, "https://awesome-ai-pedia.github.io/Awesome-AI-Pedia/" + article["path"])
        else:
            soup = BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser")
            body = soup.select_one(".ai-body")
            source_page = "https://awesome-ai-pedia.github.io/Awesome-AI-Pedia/" + article["path"]
            clean_body = localize_body(str(body), source_page)
        target.write_text(article_page(article, clean_body), encoding="utf-8")
    for article in removed:
        target = ROOT / article["url"]
        if target.is_file():
            target.unlink()
    DATA.write_text(
        "// Imported from rendered Awesome-AI-Pedia pages.\n"
        "window.aiKnowledgeArticles = " + json.dumps(kept, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    sitemap = SITEMAP.read_text(encoding="utf-8")
    for article in removed:
        sitemap = sitemap.replace(f"  <url><loc>https://www.liupzone.cn/{article['url']}</loc></url>\n", "")
    SITEMAP.write_text(sitemap, encoding="utf-8")
    print(f"kept {len(kept)} knowledge articles; removed {len(removed)} non-article entries")


if __name__ == "__main__":
    main()
