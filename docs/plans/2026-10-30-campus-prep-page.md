# 校招备考攻略子页面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完成大厂校招备考攻略的总览布局和交互，并先发布腾讯 `final` 专稿，其余公司保留布局占位。

**Architecture:** `campus-prep.html` 提供总览、搜索、分类筛选和公司卡片；腾讯卡片链接到 `campus-prep/tencent.html`，其余卡片保持不可点击占位。`campus-prep.css` 负责总览与文章页共用视觉，`tools/build_campus_prep.py` 只生成腾讯文章页并在转换前移除具体日期时间。首页接入新子项和主题卡入口。

**Tech Stack:** 原生 HTML/CSS/JavaScript；Python `markdown` 用于一次性将现有 final Markdown 转为静态 HTML；Node 内置断言做页面结构回归检查。

---

### Task 1: 写页面结构回归测试

**Files:**
- Create: `tests/campus-prep.test.js`

断言总览页存在新标题、9 篇 final 专稿卡片、搜索控件和文章链接；断言首页新菜单项指向总览页；断言每篇文章页存在正文标题和返回入口。

### Task 2: 创建总览页和共用样式

**Files:**
- Create: `campus-prep.html`
- Create: `campus-prep.css`
- Modify: `index.html`

实现桌面侧栏、移动端横向筛选、搜索、公司卡片、两周冲刺清单、主题切换和首页导航接入。

### Task 3: 发布腾讯 final 专稿

**Files:**
- Create: `tools/build_campus_prep.py`

读取 `01-腾讯-final.md`，移除具体日期、月份、小时、分钟和 Day 时间表达，转换为文章页并引用自制 SVG 封面；不生成其他公司的文章页。

### Task 4: 验证

运行 `node tests/campus-prep.test.js`、`git diff --check`，并用静态 HTTP 服务检查首页、总览页、腾讯文章页和封面资源可访问，同时确认其他公司正文未发布。
