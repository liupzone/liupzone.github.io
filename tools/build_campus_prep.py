#!/usr/bin/env python3
"""Build static article pages from the final campus-prep Markdown chapters."""

from html import escape
import json
from pathlib import Path
import re

import markdown


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path('/home/lpzone/content_creator/campus_content/docs/大厂校招备考攻略PDF')
OUTPUT_DIR = ROOT / 'campus-prep'
SITE_URL = 'https://liupzone.github.io'
SLUGS = {
    '01-腾讯-final.md': 'tencent',
    '02-阿里巴巴-final.md': 'alibaba',
}


def flatten_tokens(tokens):
    for token in tokens:
        yield token
        yield from flatten_tokens(token.get('children', []))


def sanitize_tencent_source(source: str) -> str:
    """Remove calendar-specific dates while keeping the evergreen interview advice."""
    source = source.replace('2026腾讯校招备考全攻略：高频题、面试风格、30天计划', '腾讯校招备考全攻略：高频题、面试风格、备考计划')
    source = source.replace('数据来源：真实面经整理 | 更新时间：2026年3月', '数据来源：真实面经整理 | 版本：final')
    source = source.replace('这篇文章把腾讯校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、30天备考计划。', '这篇文章把腾讯校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、备考计划。')
    source = re.sub(r'\*\*2026届校招时间线（参考）\*\*：\n\n```[\s\S]*?```', '**校招节奏（参考）**：\n\n- 预热与网申：关注官方招聘入口和内推信息\n- 笔试阶段：熟悉平台规则，保持稳定的解题状态\n- 面试阶段：准备技术面、项目面与 HR 面\n- Offer 阶段：结合岗位方向、团队和发展路径做选择', source)
    source = source.replace('腾讯技术面通常 2-3 轮，每轮 60-90 分钟。', '腾讯技术面通常有多轮，每轮会在手写代码后继续深挖基础知识。')
    source = source.replace('**考试时长**：约 2 小时', '**考试安排**：以官方通知和具体岗位要求为准')
    source = source.replace('先花 10 分钟看清楚题意，想好思路再动手', '先看清楚题意，想好思路再动手')
    source = source.replace('## 30 天备考计划', '## 备考计划')
    source = source.replace('适合已有 LeetCode 200+ 刷题量的同学，冲刺备考腾讯。', '适合已经有一定 LeetCode 刷题基础、准备冲刺腾讯的同学。')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace(
        '| 阶段 | 准备重点 |\n|------|------|---------|',
        '| 阶段 | 准备重点 |\n|------|---------|',
    )
    plan_rows = {
        '| **链表专项** | Day 1-5 |': '| **链表专项** |',
        '| **排序专项** | Day 6-9 |': '| **排序专项** |',
        '| **树专项** | Day 10-13 |': '| **树专项** |',
        '| **动态规划** | Day 14-19 |': '| **动态规划** |',
        '| **字符串+双指针** | Day 20-22 |': '| **字符串+双指针** |',
        '| **系统知识** | Day 23-27 |': '| **系统知识** |',
        '| **冲刺收尾** | Day 28-30 |': '| **冲刺收尾** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('**每天时间分配建议**：', '**每天准备建议**：')
    source = source.replace('- 上午 2h：刷题（2-3 道 Medium，1 道 Hard）', '- 刷题时段：保持 Medium 题为主，穿插 Hard 题')
    source = source.replace('- 下午 1h：复习系统知识（OS 和网络轮流）', '- 基础复习时段：OS 和网络交替复习')
    source = source.replace('- 晚上 1h：看面经 + 写总结笔记', '- 复盘时段：看面经并写总结笔记')
    source = source.replace('百度2026校招避坑指南', '百度校招避坑指南')
    source = re.sub(r'覆盖2024-2026年腾讯校招面经，更新时间：2026年3月', '覆盖历年腾讯校招面经', source)
    return source


def sanitize_alibaba_source(source: str) -> str:
    """Remove calendar-specific dates while keeping evergreen Alibaba advice."""
    source = source.replace('2026阿里校招全攻略：高频题、考点，一篇搞定', '阿里巴巴校招全攻略：高频题、考点，一篇搞定')
    source = source.replace('数据来源：真实面经整理 | 更新时间：2026年3月', '数据来源：真实面经整理 | 版本：final')
    source = source.replace('这篇文章把阿里校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、30天备考计划。', '这篇文章把阿里校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、备考计划。')
    source = re.sub(r'\*\*2026届校招时间线（参考）\*\*：\n\n```[\s\S]*?```', '**校招节奏（参考）**：\n\n- 预热与网申：关注官方招聘入口和内推信息\n- 笔试阶段：熟悉平台规则，准备编程题与能力测评\n- 面试阶段：准备技术面、项目面与 HR 面\n- Offer 阶段：结合岗位方向、团队和发展路径做选择', source)
    source = source.replace('阿里成立于1999年，总部杭州，2024财年营收超9400亿元，全球员工超20万人。', '阿里总部位于杭州，业务覆盖电商、云计算、物流、企业协作与本地生活等多个方向。')
    source = source.replace('## 30天备考计划', '## 备考计划')
    source = source.replace('适合Java方向后端或算法岗同学冲刺备考阿里。', '适合 Java 方向后端或算法岗同学准备阿里校招。')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace(
        '| 阶段 | 准备重点 |\n|------|------|---------|',
        '| 阶段 | 准备重点 |\n|------|---------|',
    )
    plan_rows = {
        '| **链表+DP专项** | Day 1-6 |': '| **链表+DP专项** |',
        '| **Java八股** | Day 7-12 |': '| **Java八股** |',
        '| **分布式专项** | Day 13-18 |': '| **分布式专项** |',
        '| **系统设计** | Day 19-22 |': '| **系统设计** |',
        '| **数据库+算法** | Day 23-26 |': '| **数据库+算法** |',
        '| **冲刺收尾** | Day 27-30 |': '| **冲刺收尾** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('能讲20分钟不重样', '能完整讲清楚且经得起追问')
    source = source.replace('能讲20分钟', '能完整讲清楚')
    source = source.replace('百度2026校招避坑指南', '百度校招避坑指南')
    source = re.sub(r'覆盖2024-2026年阿里校招面经，更新时间：2026年3月', '覆盖历年阿里校招面经', source)
    return source


def convert_markdown(source: str):
    # The source uses bold numbered lines as visual labels and immediately
    # follows them with a dash line. Normalize those blocks before Markdown
    # parsing so the article keeps a readable heading/list hierarchy in HTML.
    source = re.sub(
        r'^\*\*(\d+\.\s+.+?)\*\*(.*)$',
        lambda match: f'#### {match.group(1)}{match.group(2)}',
        source,
        flags=re.MULTILINE,
    )
    engine = markdown.Markdown(
        extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'sane_lists'],
        extension_configs={'codehilite': {'guess_lang': False, 'noclasses': True}},
    )
    body = engine.convert(source)
    title_match = re.search(r'^#\s+(.+?)\s*$', source, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else '大厂校招备考攻略'
    body = re.sub(r'^<h1[^>]*>.*?</h1>\s*', '', body, count=1, flags=re.DOTALL)
    meta_match = re.search(r'版本：([^|\n]+)', source)
    updated = meta_match.group(1).strip() if meta_match else 'final'
    toc_items = [token for token in flatten_tokens(engine.toc_tokens) if token.get('level') == 2]
    return title, updated, body, toc_items


def render_page(title, updated, body, toc_items, cover_asset, cover_alt, slug):
    nav = ''.join(f'<a href="#{escape(item["id"])}">{escape(item["name"])}</a>' for item in toc_items)
    canonical = f'{SITE_URL}/campus-prep/{slug}.html'
    description = f'{title}：岗位方向、高频题、技术考点、面试风格与备考路线。'
    article_schema = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': title,
        'description': description,
        'image': [f'{SITE_URL}/assets/{cover_asset}'],
        'author': {'@type': 'Organization', 'name': 'liupzone', 'url': SITE_URL},
        'publisher': {'@type': 'Organization', 'name': 'liupzone', 'url': SITE_URL},
        'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical},
        'articleSection': '校招稳稳拿OFFER',
        'inLanguage': 'zh-CN',
    }
    breadcrumb_schema = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '首页', 'item': f'{SITE_URL}/'},
            {'@type': 'ListItem', 'position': 2, 'name': '大厂校招备考攻略', 'item': f'{SITE_URL}/campus-prep.html'},
            {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canonical},
        ],
    }
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#f5f6fb" />
  <meta name="description" content="{escape(description)}" />
  <meta name="keywords" content="{escape(title)},校招,校招备考,大厂面试,高频题,技术面试,应届生求职" />
  <meta name="author" content="liupzone" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
  <meta name="applicable-device" content="pc,mobile" />
  <meta name="mobile-agent" content="format=html5;url={escape(canonical)}" />
  <title>{escape(title)} · 校招稳稳拿OFFER</title>
  <link rel="canonical" href="{escape(canonical)}" />
  <link rel="alternate" hreflang="zh-CN" href="{escape(canonical)}" />
  <link rel="sitemap" type="application/xml" href="{SITE_URL}/sitemap.xml" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="zh_CN" />
  <meta property="og:site_name" content="liupzone 人生路标小站" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <meta property="og:url" content="{escape(canonical)}" />
  <meta property="og:image" content="{SITE_URL}/assets/{escape(cover_asset)}" />
  <meta property="og:image:alt" content="{escape(cover_alt)}" />
  <meta property="article:section" content="校招稳稳拿OFFER" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{escape(title)}" />
  <meta name="twitter:description" content="{escape(description)}" />
  <meta name="twitter:image" content="{SITE_URL}/assets/{escape(cover_asset)}" />
  <script type="application/ld+json">{json.dumps(article_schema, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>
  <link rel="stylesheet" href="../campus-prep.css" />
</head>
<body class="light">
  <header class="topbar shell">
    <a class="brand" href="../index.html" aria-label="liupzone 首页"><span class="mark" aria-hidden="true"></span><span><span class="brand-cn">liupzone</span><span class="brand-en">人生路标小站</span></span></a>
    <nav class="nav" aria-label="主导航"><a href="../index.html">首页</a><a class="active" href="../campus-prep.html">校招稳稳拿OFFER</a><a href="../resources.html">精品资源</a><button class="icon-btn" id="themeToggle" aria-label="切换主题" title="切换主题">☾</button></nav>
  </header>
  <main class="article-page shell">
    <a class="article-back" href="../campus-prep.html">← 返回攻略目录</a>
    <header class="article-head"><div class="eyebrow">CAMPUS PREP / FINAL ARTICLE</div><h1>{escape(title)}</h1><img class="article-cover" src="../assets/{escape(cover_asset)}" alt="{escape(cover_alt)}" /><div class="article-meta"><span>版本：{escape(updated)}</span><span>内容类型：公司专项攻略</span><span>仅供学习参考</span></div></header>
    <div class="article-layout"><aside class="article-nav"><h2>本篇导航</h2>{nav}</aside><article class="article-body">{body}</article></div>
  </main>
  <script>
    document.getElementById('themeToggle').addEventListener('click', () => {{ const dark = document.body.classList.toggle('dark'); document.body.classList.toggle('light', !dark); document.getElementById('themeToggle').textContent = dark ? '☼' : '☾'; document.querySelector('meta[name="theme-color"]').setAttribute('content', dark ? '#0b1026' : '#f5f6fb'); }});
  </script>
</body>
</html>
'''


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, slug in SLUGS.items():
        source_path = SOURCE_DIR / filename
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        source = source_path.read_text(encoding='utf-8')
        if slug == 'tencent':
            source = sanitize_tencent_source(source)
            cover_asset = 'tencent-campus-prep-cover.svg'
            cover_alt = '腾讯校招备考攻略封面'
        elif slug == 'alibaba':
            source = sanitize_alibaba_source(source)
            cover_asset = 'alibaba-campus-prep-cover.svg'
            cover_alt = '阿里巴巴校招备考攻略封面'
        else:
            raise ValueError(f'Unknown campus prep slug: {slug}')
        title, updated, body, toc_items = convert_markdown(source)
        (OUTPUT_DIR / f'{slug}.html').write_text(render_page(title, updated, body, toc_items, cover_asset, cover_alt, slug), encoding='utf-8')
        print(f'generated {slug}.html')


if __name__ == '__main__':
    main()
