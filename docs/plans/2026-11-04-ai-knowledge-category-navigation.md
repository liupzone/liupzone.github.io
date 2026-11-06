# AI Knowledge Category Navigation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the AI knowledge page open on a category overview and reveal articles only after a category is selected.

**Architecture:** Keep the existing `ai-knowledge-data.js` article index and local article pages. Add a category overview view and a category article view in `ai-knowledge.html`; category metadata is defined in the page and article counts remain derived from the imported index.

**Tech Stack:** Static HTML, CSS, browser JavaScript, Node regression test.

---

### Task 1: Lock the navigation contract with regression assertions

**Files:**
- Modify: `tests/campus-prep.test.js`

Add assertions for the category overview, category cards, hidden article view on initial load, and a category-selection handler marker.

### Task 2: Implement the category-first AI knowledge page

**Files:**
- Modify: `ai-knowledge.html`

Add category descriptions based on the source repository's top-level directories, render the overview first, and switch to the filtered article feed after a category button is clicked. Preserve search within the selected category and provide a return-to-categories control.

### Task 3: Verify the static site

Run `node tests/campus-prep.test.js` and `git diff --check`. Inspect the diff to ensure only the AI page, tests, and this plan changed.
