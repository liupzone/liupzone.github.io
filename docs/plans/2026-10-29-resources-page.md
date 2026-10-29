# 精品资源页面 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a friendly, searchable resource-library subpage from `宝藏资源.xlsx` and connect the homepage's 精品资源 entry to it.

**Architecture:** Generate a static `resources-data.js` snapshot from the workbook's 29 populated sheets and 900 name/link records. Add a standalone `resources.html` with a shared bright visual language, category sidebar, search/filter controls, resource cards, and direct external links. Keep the homepage intact except for the 精品资源 links.

**Tech Stack:** HTML, CSS, vanilla JavaScript, generated JSON-like JavaScript data; no external dependencies.

---

### Task 1: Export workbook data

**Files:**
- Create: `resources-data.js`

Read the workbook with `openpyxl`, preserve worksheet/category names and valid links, assign a broad group for education, media, books, exams, or other, and emit 900 records.

### Task 2: Build resources subpage

**Files:**
- Create: `resources.html`

Build a bright resource-library UI with brand header, intro metrics, search box, group chips, category list, responsive cards, empty state, and external open actions. Use data from `resources-data.js` and render the first category/all resources by default.

### Task 3: Connect and verify

**Files:**
- Modify: `index.html`

Point homepage 精品资源 links to `resources.html`, then run `git diff --check`, data-count validation, and desktop/mobile browser screenshots. Confirm search, group filters, category filters, and links work.
