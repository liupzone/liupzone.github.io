# Liupzone Homepage Layout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the static homepage into a bright personal content hub organized around the site's recruitment, resources, graduate-exam, and lifestyle themes.

**Architecture:** Keep the single-file static site in `index.html`. Replace the vocabulary-study workspace with a content-first layout: brand header, category navigation, latest-content feed, category cards, and a recommendation sidebar. Keep the existing light/dark theme toggle and recruitment dropdown behavior.

**Tech Stack:** Semantic HTML, CSS, and vanilla JavaScript; no build step or external dependencies.

---

### Task 1: Replace homepage content structure

**Files:**
- Modify: `index.html`

Add a site introduction, latest content cards, five topic entry points, and a compact recommendation panel. Keep links and labels aligned with the existing header categories.

### Task 2: Restyle for a bright editorial resource hub

**Files:**
- Modify: `index.html`

Use the existing light theme as the default, with restrained borders, paper-like panels, strong type hierarchy, and responsive one-column behavior below 760px.

### Task 3: Preserve interactions and verify rendering

**Files:**
- Modify: `index.html`

Keep theme switching, recruitment submenu selection, search focus shortcut, and toast feedback. Run `git diff --check`, render desktop/mobile screenshots, and inspect for overflow or missing labels.
