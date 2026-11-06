# Repository Guidelines

## Project Structure & Module Organization

This is a static GitHub Pages site.

- `index.html`: homepage, theme entry points, latest content, and visibility stats.
- `campus-prep.html` and `campus-prep/`: campus-recruitment index and generated company articles.
- `resources.html`, `resources-data.js`: searchable resource library.
- `search.html`: fuzzy search across all published site content.
- `assets/`: SVG covers and image assets.
- `tools/build_campus_prep.py`: generator for campus article HTML.
- `tests/`: Node-based site verification scripts.
- `docs/`: analytics and operational notes.
- `CNAME`, `robots.txt`, `sitemap.xml`: custom-domain and SEO configuration.

## Build, Test, and Development Commands

```bash
python3 tools/build_campus_prep.py  # regenerate all campus pages
node tests/campus-prep.test.js      # run regression checks
python3 -m http.server 8000         # local preview
git diff --check                    # check whitespace
```

The generator requires Python `markdown` and reads external `content_creator` sources. Change the generator, not generated articles.

## Coding Style & Naming Conventions

- Use UTF-8, semantic HTML5, and 2-space web indentation; use 4 spaces in Python.
- Use lowercase hyphenated filenames, such as `huawei.html`.
- Name company covers `<slug>-campus-prep-cover.svg`.
- Use `const`/`let`; canonical URLs stay on `https://www.liupzone.cn`.

## Testing Guidelines

No framework or coverage threshold is configured. The plain-Node test file checks navigation, generated HTML, search, SEO, and content counts. Add assertions for those changes; verify UI in a browser.

```bash
node tests/campus-prep.test.js
git diff --check
```

## Commit & Pull Request Guidelines

History follows Conventional Commits, for example:

```text
feat(search): add four-category fuzzy content search
fix(analytics): label daily visits correctly
style(home): use horizontal cover cards
```

Pull requests should summarize changes, list test results, and include before/after screenshots for UI work. Link related issues when available.

## Content & SEO Rules

Do not add simulated dates, statistics, links, or unpublished content. Keep “生活福利” marked as pending until real content exists. When publishing an article, update its cover, index entry, search index, sitemap, and tests.

Analytics use anonymous local fallback data unless a summary endpoint is configured; never invent site-wide counts. Keep SEO files and canonicals on `www.liupzone.cn`.
