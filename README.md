# Portfolio Website – Shamit Sai Imandi

Minimal monospace portfolio with a content-first static generation workflow.

## Core Rule

The visual style is fixed and shared across all pages.

- Do not change `style.css` unless you intentionally want a site-wide redesign.
- Edit content in `content/` only.
- Generated HTML in root folders (`index.html`, `projects/*.html`, etc.) is rebuilt automatically and should not be edited manually.

## Repository Structure

```
├── index.html / projects.html                             # generated
├── projects/                                              # generated detail pages
├── style.css                                              # fixed theme
├── content/
│   ├── about.md
│   ├── projects/
│   │   └── <project-slug>/
│   │       ├── index.md                                   # project home page
│   │       ├── post-1.md                                  # project post/page
│   │       └── post-2.md
│   └── _templates/                                        # scaffolding templates
├── scripts/
│   └── build_index.py
└── templates/
   └── base.html
```

## Commands

### Build site

```bash
python3 scripts/build_index.py
```

### Validate metadata

```bash
python3 scripts/build_index.py check
```

Checks required metadata and duplicate IDs.

### Create new content entry (recommended)

```bash
python3 scripts/build_index.py new --section projects --slug my-project --title "My Project"
python3 scripts/build_index.py new-post --project my-project --slug week-1-log --title "Week 1 Log"
```

This generates starter Markdown files from templates in `content/_templates/`.

## Metadata Reference

### Project index (`content/projects/<project>/index.md`)

```html
<!-- project-id: slug -->
<!-- title: Project Title -->
<!-- status: systems / ml -->
<!-- summary: One-line description -->
```

### Project post (`content/projects/<project>/<post>.md`)

```html
<!-- title: Post Title -->
<!-- date: 2026-03-03 -->
<!-- summary: One-line update summary -->
```

## Notes

- Markdown (`.md`) is preferred for all new content.
- For project folders, `index.md` (or `index.html`) is the project home page.
- Any additional `.md`/`.html` files in that folder become posts/pages under that project.
- `projects.html` is the top-level index of all projects.
