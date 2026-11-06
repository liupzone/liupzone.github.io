#!/usr/bin/env python3
"""Build the AI knowledge directory from the source repository tree.

Pass a local source checkout as the second argument to mirror article bodies;
without it the generator still emits a complete, source-linked directory.
"""

import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote, urljoin

import markdown


OUTPUT = Path(__file__).resolve().parents[1] / "ai-knowledge-data.js"
SITE_ROOT = OUTPUT.parent
ARTICLE_ROOT = SITE_ROOT / "ai-knowledge"
RAW_REPO_URL = "https://raw.githubusercontent.com/Awesome-AI-Pedia/Awesome-AI-Pedia/master/"
SOURCE_REPO_URL = "https://github.com/Awesome-AI-Pedia/Awesome-AI-Pedia/blob/master/"
SOURCE_GIT = "git@github.com:Awesome-AI-Pedia/Awesome-AI-Pedia.git"


def article_id(path: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", path).strip("-").lower()
    return value or "article"


def rewrite_markdown_links(text: str, source_path: str) -> str:
    base_url = RAW_REPO_URL + quote(str(Path(source_path).parent).replace("\\", "/") + "/", safe="/%")

    def replace_image(match: re.Match[str]) -> str:
        target = match.group(2)
        if target.startswith(("http://", "https://", "data:")):
            return match.group(0)
        return match.group(1) + urljoin(base_url, target) + match.group(3)

    def replace_link(match: re.Match[str]) -> str:
        target = match.group(2)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        return match.group(1) + SOURCE_REPO_URL + quote(str(Path(source_path).parent / target).replace("\\", "/"), safe="/%#?") + match.group(3)

    text = re.sub(r"(!\[[^\]]*\]\()([^\)]+)(\))", replace_image, text)
    return re.sub(r"(?<!!)(\[[^\]]*\]\()([^\)]+)(\))", replace_link, text)


def is_publishable_source(text: str, title: str) -> bool:
    rendered = markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists"], output_format="html5")
    plain = " ".join(re.sub(r"<[^>]+>", " ", rendered).split())
    external_links = len(re.findall(r"<a\s[^>]*href=[\"']https?://", rendered, re.I))
    if title.strip().lower() == "index" or len(plain) < 120:
        return False
    return not (len(plain) < 260 and external_links >= 2)


def render_article(article: dict, source_text: str) -> None:
    title = article["title"]
    body = markdown.markdown(
        rewrite_markdown_links(source_text, article["path"]),
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )
    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="description" content="{escape(title)} · AI知识库专栏" />
  <title>{escape(title)} · AI知识库专栏</title>
  <link rel="canonical" href="https://www.liupzone.cn/{article["href"]}" />
  <link rel="stylesheet" href="../campus-prep.css" />
  <style>
    .ai-article {{ max-width: 1040px; padding: 48px 20px 96px; }}
    .ai-article-header {{ max-width: 820px; padding-bottom: 26px; border-bottom: 1px solid var(--prep-line); }}
    .ai-article h1 {{ margin: 10px 0 13px; color: var(--prep-ink); font-size: clamp(30px, 4vw, 48px); line-height: 1.12; letter-spacing: -.035em; }}
    .ai-meta {{ margin: 0; color: var(--prep-muted); font-size: 12px; line-height: 1.9; }}
    .ai-source {{ margin: 6px 0 0; color: var(--prep-faint); font-size: 11px; line-height: 1.6; }}
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
  <main class="ai-article shell"><header class="ai-article-header"><div class="eyebrow">AI KNOWLEDGE / {escape(article["category"])}</div><h1>{escape(title)}</h1><p class="ai-meta">原始路径：{escape(article["path"])} · <a href="{escape(article["source_url"])}" target="_blank" rel="noopener noreferrer">查看 GitHub 源文件 ↗</a></p><p class="ai-source">源仓库：{SOURCE_GIT}</p></header><article class="ai-body ai-reading-width">{body}</article></main>
  <script>document.getElementById('themeToggle').addEventListener('click',()=>{{const dark=document.body.classList.toggle('dark');document.body.classList.toggle('light',!dark);document.getElementById('themeToggle').textContent=dark?'☼':'☾';}});</script>
</body>
</html>
'''
    target = SITE_ROOT / article["href"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")


def main() -> None:
    if len(sys.argv) not in {2, 3}:
        raise SystemExit("usage: build_ai_knowledge.py TREE_JSON [SOURCE_DIR]")

    tree = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    source_dir = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    articles = []
    for item in tree["tree"]:
        path = item.get("path", "")
        if item.get("type") != "blob" or not path.endswith(".md"):
            continue
        if path in {"README.md", "CONTRIBUTING.md"} or path.startswith(".github/"):
            continue
        parts = path.split("/")
        if parts[0].startswith("."):
            continue
        if Path(parts[-1]).stem.strip().lower() == "index":
            continue
        category = parts[0] if len(parts) > 1 else "其他"
        title = Path(parts[-1]).stem
        article = {
            "title": title,
            "category": category,
            "path": path,
            "source_url": SOURCE_REPO_URL + quote(path, safe="/"),
        }
        article["href"] = "ai-knowledge/" + article_id(path) + ".html"
        article["url"] = article["href"] if source_dir else article["source_url"]
        if source_dir:
            source_file = source_dir / path
            if not source_file.is_file():
                raise SystemExit(f"missing source Markdown: {source_file}")
            if not is_publishable_source(source_file.read_text(encoding="utf-8"), title):
                continue
        articles.append(article)

    articles.sort(key=lambda item: (item["category"], item["path"]))
    if source_dir:
        for article in articles:
            render_article(article, (source_dir / article["path"]).read_text(encoding="utf-8"))
    payload = json.dumps(articles, ensure_ascii=False, separators=(",", ":"))
    OUTPUT.write_text(
        "// Generated from the Awesome-AI-Pedia repository tree.\n"
        f"window.aiKnowledgeArticles = {payload};\n",
        encoding="utf-8",
    )
    print(f"wrote {len(articles)} AI knowledge articles to {OUTPUT}")


if __name__ == "__main__":
    main()
