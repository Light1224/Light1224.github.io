# Portfolio — Shamit Sai

A minimal static portfolio for [GitHub Pages](https://pages.github.com/). No build step, no animations.

## Structure

```
data/            ← site content (one JSON file per section)
  meta.json      ← name, footer date, nav, external links
  about.json
  education.json
  experience.json
  projects.json
  blog.json
  contact.json
js/site.js       ← loads data and renders pages
css/style.css
index.html       ← About Me
education.html
experience.html
projects.html
blog.html
reading.html
contact.html
resume.pdf
```

See **`data/README.md`** for what to edit in each file.

## Local preview

Content is fetched with JavaScript, so use a local server (not `file://`):

```bash
python3 -m http.server 8000
```

Visit [http://localhost:8000](http://localhost:8000).

## Deploy to GitHub Pages

1. Create a repository named **`Light1224.github.io`** (or your username equivalent).
2. Push this folder to `main`.
3. In **Settings → Pages**, deploy from branch **`main`**, folder **`/ (root)`**.

Site URL: **https://light1224.github.io**

## Customize styles

Edit `css/style.css`. CSS variables at the top control colors, sidebar width, and typography.
