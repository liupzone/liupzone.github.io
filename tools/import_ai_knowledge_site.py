#!/usr/bin/env python3
"""Import rendered Awesome-AI-Pedia pages into the local AI knowledge section."""

import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote, urljoin

import markdown
from bs4 import BeautifulSoup


SITE_ROOT = Path(__file__).resolve().parents[1]
ARTICLE_ROOT = SITE_ROOT / "ai-knowledge"
DATA_OUTPUT = SITE_ROOT / "ai-knowledge-data.js"
SOURCE_SITE = "https://awesome-ai-pedia.github.io/Awesome-AI-Pedia/"
SOURCE_REPO = "https://github.com/Awesome-AI-Pedia/Awesome-AI-Pedia/blob/master/"
DEFAULT_THUMBNAIL = "assets/ai-knowledge-default.svg"


def article_id(path: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", path).strip("-").lower() or "article"


def source_url(path: str) -> str:
    return SOURCE_REPO + quote(path, safe="/")


def markdown_title(text: str, fallback: str) -> str:
    match = re.search(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE)
    return re.sub(r"[`*_]", "", match.group(1)).strip() if match else fallback


def localize_body(body_html: str, source_page_url: str) -> str:
    soup = BeautifulSoup(body_html, "html.parser")
    body_root = soup.find(class_="ai-body")
    if body_root:
        soup = body_root
        for nested in soup.select(".ai-body"):
            nested.unwrap()
    if soup.select_one(".vp-doc"):
        soup = soup.select_one(".vp-doc")
    for tag in soup.select("button.copy, .header-anchor, .line-numbers-wrapper"):
        tag.decompose()
    for tag in soup.select("pre span"):
        tag.unwrap()
    for tag in soup.select("span.lang"):
        tag.decompose()
    for tag in soup.find_all(True):
        for attribute in list(tag.attrs):
            if attribute.startswith("data-") or attribute in {"id", "tabindex"}:
                del tag.attrs[attribute]
    for tag in soup.select("[style]"):
        del tag["style"]
    for tag in soup.select("[class]"):
        classes = [name for name in tag.get("class", []) if name not in {"vp-doc", "vp-adaptive-theme", "line-numbers-mode", "external-link-icon-enabled"} and not name.startswith("_Awesome-AI-Pedia")]
        if classes:
            tag["class"] = classes
        else:
            del tag["class"]
    first_heading = soup.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    if first_heading:
        first_heading.decompose()
    for tag in soup.find_all(["a", "img"]):
        attribute = "href" if tag.name == "a" else "src"
        value = tag.get(attribute)
        if not value or value.startswith(("http://", "https://", "data:", "#", "mailto:")):
            continue
        tag[attribute] = urljoin(source_page_url, value)
    for tag in soup.find_all("a"):
        if tag.get("href", "").startswith(SOURCE_SITE):
            tag["target"] = "_blank"
            tag["rel"] = "noopener noreferrer"
    return "".join(str(child) for child in soup.contents)


def article_excerpt(body) -> str:
    for paragraph in body.find_all("p"):
        text = " ".join(paragraph.get_text(" ", strip=True).split())
        if len(text) >= 18:
            return text[:150] + ("…" if len(text) > 150 else "")
    text = " ".join(body.get_text(" ", strip=True).split())
    return text[:150] + ("…" if len(text) > 150 else "")


def article_thumbnail(body, source_page_url: str) -> str:
    image = body.find("img")
    if image and image.get("src"):
        return urljoin(source_page_url, image["src"])
    return DEFAULT_THUMBNAIL


def is_publishable(body, title: str) -> bool:
    text = " ".join(body.get_text(" ", strip=True).split())
    external_links = len(body.select('a[href^="http://"], a[href^="https://"]'))
    if title.strip().lower() == "index":
        return False
    if len(text) < 120:
        return False
    return not (len(text) < 260 and external_links >= 2)


def article_page(article: dict, body_html: str) -> str:
    title = escape(article["title"])
    category = escape(article["category"])
    path = escape(article["path"])
    href = escape(article["href"])
    image = escape(article.get("image", DEFAULT_THUMBNAIL).replace("assets/", "../assets/", 1))
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="description" content="{title} · AI知识库专栏" />
  <title>{title} · AI知识库专栏</title>
  <link rel="canonical" href="https://www.liupzone.cn/{href}" />
  <link rel="stylesheet" href="../campus-prep.css" />
  <style>
    .ai-article {{ max-width: 1040px; padding: 48px 20px 96px; }}
    .ai-article-header {{ max-width: 820px; padding-bottom: 26px; border-bottom: 1px solid var(--prep-line); }}
    .ai-article h1 {{ margin: 10px 0 13px; color: var(--prep-ink); font-size: clamp(30px, 4vw, 48px); line-height: 1.12; letter-spacing: -.035em; }}
    .ai-meta {{ margin: 0; color: var(--prep-muted); font-size: 12px; line-height: 1.9; }}
    .ai-source {{ margin: 6px 0 0; color: var(--prep-faint); font-size: 11px; line-height: 1.6; }}
    .ai-cover {{ display: block; width: min(100%, 820px); aspect-ratio: 2.4 / 1; margin: 24px 0 0; border: 1px solid var(--prep-line); border-radius: 10px; object-fit: cover; background: var(--prep-blue-soft); }}
    .ai-meta a {{ color: var(--prep-blue); }}
    .ai-reading-width {{ max-width: 820px; }}
    .ai-body {{ margin-top: 30px; padding: 0; color: var(--prep-ink); line-height: 1.9; overflow-wrap: anywhere; }}
    .ai-body h1, .ai-body h2, .ai-body h3, .ai-body h4 {{ line-height: 1.4; }}
    .ai-body h1 {{ margin: 36px 0 14px; font-size: 30px; }}
    .ai-body h2 {{ margin: 38px 0 14px; padding: 0 0 9px 13px; border-left: 3px solid var(--prep-blue); border-bottom: 1px solid var(--prep-line); font-size: 23px; }}
    .ai-body h3 {{ margin: 27px 0 9px; color: var(--prep-blue); font-size: 17px; }}
    .ai-body h4 {{ margin: 21px 0 7px; font-size: 15px; }}
    .ai-body p, .ai-body ul, .ai-body ol, .ai-body blockquote {{ margin: 13px 0; }}
    .ai-body ul, .ai-body ol {{ padding-left: 25px; }}
    .ai-body li {{ margin: 5px 0; }}
    .ai-body a {{ color: var(--prep-blue); }}
    .ai-body img {{ max-width: 100%; height: auto; }}
    .ai-body pre {{ position: relative; overflow-x: auto; margin: 17px 0; padding: 17px 19px; border: 1px solid #293552; border-radius: 9px; color: #e8eefc; background: #172033; font-size: 12px; line-height: 1.7; tab-size: 2; }}
    .ai-body code {{ padding: 2px 5px; border-radius: 4px; color: #a04f35; background: #fff1e9; font-size: .9em; }}
    .ai-body pre code {{ padding: 0; color: inherit; background: transparent; }}
    .ai-body table {{ width: 100%; margin: 17px 0; border-collapse: collapse; font-size: 13px; }}
    .ai-body th, .ai-body td {{ padding: 8px 10px; border: 1px solid var(--prep-line); text-align: left; }}
    .ai-body blockquote {{ margin: 18px 0; padding: 10px 16px; border-left: 3px solid var(--prep-orange); color: var(--prep-muted); background: #fff7f2; }}
    .ai-body hr {{ margin: 30px 0; border: 0; border-top: 1px solid var(--prep-line); }}
    body.dark .ai-body code {{ color: #ffc0a4; background: rgba(241, 154, 114, .13); }}
    body.dark .ai-body blockquote {{ background: rgba(241, 154, 114, .1); }}
    @media (max-width: 680px) {{ .ai-article {{ padding-top: 30px; padding-bottom: 60px; }} .ai-body {{ margin-top: 24px; }} .ai-body h2 {{ font-size: 20px; }} .ai-body h3 {{ font-size: 16px; }} .ai-body pre {{ margin-left: -2px; margin-right: -2px; padding: 14px; font-size: 11px; }} }}
  </style>
</head>
<body class="light">
  <header class="topbar shell"><a class="brand" href="../index.html" aria-label="liupzone 首页"><span class="mark" aria-hidden="true"></span><span><span class="brand-cn">liupzone</span><span class="brand-en">人生路标小站</span></span></a><nav class="nav" aria-label="主导航"><a href="../index.html">首页</a><a href="../campus-prep.html">校招稳稳拿OFFER</a><a href="../resources.html">宝藏资源</a><a href="../resources.html?category=考研">考研之路</a><a class="active" href="../ai-knowledge.html">AI知识库专栏</a><a href="../life.html">生活福利</a><button class="icon-btn" id="themeToggle" aria-label="切换主题" title="切换主题">☾</button></nav></header>
  <main class="ai-article shell"><header class="ai-article-header"><div class="eyebrow">AI KNOWLEDGE / {category}</div><h1>{title}</h1><p class="ai-meta">内容来源：Awesome-AI-Pedia 知识整理</p><img class="ai-cover" src="{image}" alt="{title}主题配图" /></header><article class="ai-body ai-reading-width">{body_html}</article></main>
  <script>document.getElementById('themeToggle').addEventListener('click',()=>{{const dark=document.body.classList.toggle('dark');document.body.classList.toggle('light',!dark);document.getElementById('themeToggle').textContent=dark?'☼':'☾';}});</script>
</body>
</html>
'''


def main() -> None:
    if len(sys.argv) not in {3, 4}:
        raise SystemExit("usage: import_ai_knowledge_site.py TREE_JSON RENDERED_DIR [FALLBACK_MARKDOWN]")
    tree = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    rendered_dir = Path(sys.argv[2])
    fallback_markdown = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    articles = []
    for item in tree["tree"]:
        path = item.get("path", "")
        if item.get("type") != "blob" or not path.endswith(".md"):
            continue
        if path in {"README.md", "CONTRIBUTING.md"} or path.startswith(".github/") or path.startswith("."):
            continue
        article = {
            "title": Path(path).stem,
            "category": path.split("/")[0] if "/" in path else "其他",
            "path": path,
            "source_url": source_url(path),
            "href": "ai-knowledge/" + article_id(path) + ".html",
        }
        local_source = SITE_ROOT.parent / "Awesome-AI-Pedia" / path
        if local_source.is_file():
            article["title"] = markdown_title(local_source.read_text(encoding="utf-8"), article["title"])
        rendered = rendered_dir / (article_id(path) + ".html")
        if rendered.exists():
            soup = BeautifulSoup(rendered.read_text(encoding="utf-8"), "html.parser")
            body = soup.select_one(".vp-doc")
            if body is None:
                raise SystemExit(f"missing VitePress body: {rendered}")
        elif fallback_markdown and fallback_markdown.is_file():
            body = BeautifulSoup(
                "<div class='vp-doc'>" + markdown.markdown(
                    fallback_markdown.read_text(encoding="utf-8"),
                    extensions=["fenced_code", "tables", "sane_lists"],
                    output_format="html5",
                ) + "</div>",
                "html.parser",
            )
        else:
            raise SystemExit(f"missing rendered article: {rendered}")
        if not is_publishable(body, article["title"]):
            continue
        source_page = SOURCE_SITE + quote(path[:-3], safe="/") + ".html"
        page_body = localize_body(str(body), source_page)
        target = SITE_ROOT / article["href"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(article_page(article, page_body), encoding="utf-8")
        article["url"] = article["href"]
        article["excerpt"] = article_excerpt(body)
        article["image"] = article_thumbnail(body, source_page)
        articles.append(article)

    articles.sort(key=lambda item: (item["category"], item["path"]))
    DATA_OUTPUT.write_text(
        "// Imported from rendered Awesome-AI-Pedia pages.\n"
        "window.aiKnowledgeArticles = " + json.dumps(articles, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"imported {len(articles)} local AI articles")


if __name__ == "__main__":
    main()
