import datetime as dt
import html
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "templates")
CONTENT_DIR = os.path.join(ROOT, "content")
PROJECTS_CONTENT_DIR = os.path.join(CONTENT_DIR, "projects")
SECTION_TEMPLATE_DIR = os.path.join(CONTENT_DIR, "_templates")

BASE_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "base.html")

METADATA_RE = re.compile(r"<!--\s*([a-zA-Z0-9_-]+)\s*:\s*(.*?)\s*-->")
METADATA_COMMENT_RE = re.compile(r"^\s*<!--\s*[a-zA-Z0-9_-]+\s*:\s*.*?-->\s*$")
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
BODY_RE = re.compile(r"<body[^>]*>(.*?)</body>", re.IGNORECASE | re.DOTALL)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TWO_DIGIT_RE = re.compile(r"^\d{2}$")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".avif"}
MATH_TOKEN_RE = re.compile(r"(\$\$.*?\$\$|\$(?:\\.|[^$\\])+\$|\\\\\(.*?\\\\\)|\\\\\[.*?\\\\\])", re.DOTALL)
MATH_DETECT_RE = re.compile(r"\$\$.*?\$\$|\$(?:\\.|[^$\\])+\$|\\\\\(.*?\\\\\)|\\\\\[.*?\\\\\]", re.DOTALL)
MATHJAX_SCRIPT = (
    '<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]],displayMath:[["$$","$$"],["\\\\[","\\\\]"]]}};</script>'
    '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
)


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def rel_prefix(output_rel_path):
    depth = len(output_rel_path.split(os.sep)) - 1
    return "../" * depth


def parse_metadata(content):
    metadata = {}
    for key, value in METADATA_RE.findall(content):
        metadata[key.strip().lower()] = value.strip()
    return metadata


def strip_metadata_comments(content):
    lines = content.splitlines()
    filtered = [line for line in lines if not METADATA_COMMENT_RE.match(line)]
    return "\n".join(filtered).strip()


def markdown_inline(text):
    protected_segments = []

    def protect_math(match):
        protected_segments.append(match.group(0))
        return f"__MATH_TOKEN_{len(protected_segments)-1}__"

    text = MATH_TOKEN_RE.sub(protect_math, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)

    for idx, segment in enumerate(protected_segments):
        text = text.replace(f"__MATH_TOKEN_{idx}__", segment)

    return text


def contains_math_markup(text):
    return bool(MATH_DETECT_RE.search(text or ""))


def markdown_to_html(markdown_text):
    lines = markdown_text.splitlines()
    html_lines = []
    paragraph_buffer = []
    in_list = False

    def flush_paragraph():
        nonlocal paragraph_buffer
        if paragraph_buffer:
            html_lines.append(f"<p>{markdown_inline(' '.join(paragraph_buffer).strip())}</p>")
            paragraph_buffer = []

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped:
            flush_paragraph()
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{markdown_inline(stripped[2:].strip())}</h1>")
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{markdown_inline(stripped[3:].strip())}</h2>")
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{markdown_inline(stripped[4:].strip())}</h3>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{markdown_inline(stripped[2:].strip())}</li>")
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph()
    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def extract_title(content_html, fallback):
    match = H1_RE.search(content_html)
    if match:
        title = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        if title:
            return title
    return fallback


def render_source_body(path):
    raw = read_text(path)
    metadata = parse_metadata(raw)
    stripped = strip_metadata_comments(raw)
    if path.endswith(".md"):
        body_html = markdown_to_html(stripped)
    else:
        body_html = stripped
        match = BODY_RE.search(body_html)
        if match:
            body_html = match.group(1).strip()
    return metadata, body_html


def discover_preferred_entries(directory):
    preferred = {}
    for name in os.listdir(directory):
        full = os.path.join(directory, name)
        if not os.path.isfile(full):
            continue
        stem, ext = os.path.splitext(name)
        if ext not in {".md", ".html"}:
            continue
        existing = preferred.get(stem)
        if existing is None or ext == ".md":
            preferred[stem] = ext
    return [f"{stem}{preferred[stem]}" for stem in sorted(preferred.keys())]


def list_project_image_relpaths(project_dir):
    images_dir = os.path.join(project_dir, "images")
    if not os.path.isdir(images_dir):
        return []

    relpaths = []
    for root, _, files in os.walk(images_dir):
        for fname in sorted(files):
            _, ext = os.path.splitext(fname)
            if ext.lower() not in IMAGE_EXTENSIONS:
                continue
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, images_dir).replace(os.sep, "/")
            relpaths.append(rel)
    return sorted(relpaths)


def unique_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    index = 2
    while True:
        candidate = f"{base}-{index}{ext}"
        if not os.path.exists(candidate):
            return candidate
        index += 1


def normalize_project_structure(project_dir):
    pages_dir = os.path.join(project_dir, "pages")
    images_dir = os.path.join(project_dir, "images")
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for name in os.listdir(project_dir):
        if name in {"pages", "images"}:
            continue

        src = os.path.join(project_dir, name)
        if os.path.isdir(src):
            dst = os.path.join(images_dir, name)
            if os.path.exists(dst):
                shutil.copytree(src, dst, dirs_exist_ok=True)
                shutil.rmtree(src)
            else:
                shutil.move(src, dst)
            continue

        _, ext = os.path.splitext(name)
        if ext.lower() == ".html":
            dst = os.path.join(pages_dir, name)
        else:
            dst = os.path.join(images_dir, name)

        if os.path.exists(dst):
            os.remove(src)
        else:
            shutil.move(src, dst)


def normalize_all_project_structures():
    os.makedirs(PROJECTS_CONTENT_DIR, exist_ok=True)
    for name in os.listdir(PROJECTS_CONTENT_DIR):
        project_dir = os.path.join(PROJECTS_CONTENT_DIR, name)
        if os.path.isdir(project_dir):
            normalize_project_structure(project_dir)


def make_two_digit_id(num):
    return f"{num:02d}"


def assign_missing_two_digit_ids(items, key):
    used = set()
    for item in items:
        value = item.get(key, "").strip()
        if TWO_DIGIT_RE.match(value) and value not in used:
            used.add(value)
            item[key] = value
        else:
            item[key] = ""

    next_num = 1
    for item in items:
        value = item.get(key, "").strip()
        if TWO_DIGIT_RE.match(value):
            item[key] = value
            continue

        while make_two_digit_id(next_num) in used:
            next_num += 1
        new_id = make_two_digit_id(next_num)
        item[key] = new_id
        used.add(new_id)
        next_num += 1


def parse_artifact_notes(project_dir):
    images_dir = os.path.join(project_dir, "images")
    candidate_names = ["artifacts.txt", "captions.txt", "notes.txt", "descriptions.txt"]
    candidates = [os.path.join(images_dir, name) for name in candidate_names]
    candidates.extend(
        sorted(
            os.path.join(images_dir, name)
            for name in os.listdir(images_dir)
            if name.lower().endswith(".txt") and name.lower() not in candidate_names
        )
        if os.path.isdir(images_dir)
        else []
    )

    notes_file = None
    for path in candidates:
        if os.path.isfile(path):
            notes_file = path
            break

    if notes_file is None:
        return {}

    notes = {}
    for raw in read_text(notes_file).splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key_norm = key.strip().replace("\\", "/").lower()
        val_norm = value.strip()
        if not key_norm:
            continue
        notes[key_norm] = val_norm
        notes[os.path.basename(key_norm)] = val_norm

    return notes


def build_project_artifacts_page(project):
    if not project["image_relpaths"]:
        return (
            f"<h1>{html.escape(project['title'])} ARTIFACTS</h1>\n"
            "<p>No artifacts found in this project.</p>"
        )

    cards = []
    modal_images = []
    modal_notes = []
    notes = project["artifact_notes"]

    for idx, rel in enumerate(project["image_relpaths"]):
        rel_norm = rel.replace("\\", "/")
        img_url = f"images/{rel_norm}"
        file_name = os.path.basename(rel_norm)
        note = notes.get(rel_norm.lower(), notes.get(file_name.lower(), ""))
        safe_name = html.escape(file_name)
        safe_note = html.escape(note)

        cards.append(
            "\n".join(
                [
                    f'<button type="button" class="artifact-thumb" data-artifact-open="{idx}" aria-label="Open {safe_name}">',
                    f'<img src="{img_url}" alt="{safe_name}" loading="lazy">',
                    f'<span class="artifact-thumb-label">{safe_name}</span>',
                    "</button>",
                ]
            )
        )
        modal_images.append(
            f'<img src="{img_url}" alt="{safe_name}" class="artifact-modal-image" data-artifact-image-index="{idx}" loading="lazy">'
        )
        modal_notes.append(
            f'<div class="artifact-note" data-artifact-note-index="{idx}">{safe_note or "No description provided."}</div>'
        )

    return "\n".join(
        [
            f"<h1>{html.escape(project['title'])} ARTIFACTS</h1>",
            '<p>All project artifacts from the images folder.</p>',
            '<style>',
            '.artifact-toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:8px 0 14px 0}',
            '.artifact-search{font:inherit;color:inherit;background:transparent;border:1px solid currentColor;padding:8px 10px;min-width:260px}',
            '.artifact-count{font-size:13px;opacity:.8}',
            '.artifact-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;max-width:100%}',
            '.artifact-thumb{display:flex;flex-direction:column;gap:6px;border:1px solid currentColor;background:transparent;padding:8px;cursor:pointer;overflow:hidden;min-height:170px;text-align:left}',
            '.artifact-thumb img{width:100%;height:120px;max-height:120px;object-fit:contain;display:block}',
            '.artifact-thumb-label{font-size:12px;line-height:1.3;overflow-wrap:anywhere}',
            '.artifact-modal[hidden]{display:none !important}',
            '.artifact-modal{position:fixed;inset:0;z-index:1000}',
            '.artifact-modal-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.75)}',
            '.artifact-modal-content{position:relative;display:flex;align-items:center;justify-content:center;height:100%;padding:18px;gap:10px}',
            '.artifact-modal-stage{position:relative;max-width:min(1400px,95vw);max-height:92vh;display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px;align-items:start}',
            '.artifact-modal-image{display:none;max-width:100%;max-height:88vh;object-fit:contain;border:1px solid currentColor}',
            '.artifact-meta{border:1px solid currentColor;padding:10px;max-height:88vh;overflow:auto}',
            '.artifact-meta-top{font-size:13px;opacity:.8;margin-bottom:8px}',
            '.artifact-note{display:none;font-size:13px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere}',
            '.artifact-nav,.artifact-close{font:inherit;color:inherit;background:transparent;border:1px solid currentColor;cursor:pointer}',
            '.artifact-nav{width:36px;height:36px;display:flex;align-items:center;justify-content:center}',
            '.artifact-close{position:absolute;top:24px;right:24px;width:36px;height:36px}',
            '@media (max-width:960px){.artifact-modal-stage{grid-template-columns:minmax(0,1fr)}.artifact-meta{max-height:none}.artifact-nav{position:absolute;top:50%;transform:translateY(-50%)}.artifact-prev{left:8px}.artifact-next{right:8px}}',
            '</style>',
            '<div class="artifact-toolbar">',
            '<input id="artifact-search" class="artifact-search" type="text" placeholder="Filter by filename or description..." aria-label="Filter artifacts">',
            '<span id="artifact-count" class="artifact-count"></span>',
            "</div>",
            '<div class="artifact-grid" id="artifact-grid">',
            *cards,
            "</div>",
            '<div class="artifact-modal" id="artifact-modal" hidden>',
            '<div class="artifact-modal-backdrop" data-artifact-close="1"></div>',
            '<div class="artifact-modal-content" role="dialog" aria-modal="true" aria-label="Artifact viewer">',
            '<button type="button" class="artifact-nav artifact-prev" data-artifact-prev="1" aria-label="Previous image">&#8592;</button>',
            '<div class="artifact-modal-stage">',
            *modal_images,
            '<div class="artifact-meta">',
            '<div class="artifact-meta-top">',
            '<span id="artifact-position"></span>',
            "</div>",
            *modal_notes,
            "</div>",
            "</div>",
            '<button type="button" class="artifact-nav artifact-next" data-artifact-next="1" aria-label="Next image">&#8594;</button>',
            '<button type="button" class="artifact-close" data-artifact-close="1" aria-label="Close viewer">&#10005;</button>',
            "</div>",
            "</div>",
            "<script>",
            "(function(){",
            "var modal = document.getElementById('artifact-modal');",
            "var grid = document.getElementById('artifact-grid');",
            "var search = document.getElementById('artifact-search');",
            "var count = document.getElementById('artifact-count');",
            "if (!modal || !grid) return;",
            "var cards = Array.prototype.slice.call(grid.querySelectorAll('[data-artifact-open]'));",
            "var images = Array.prototype.slice.call(modal.querySelectorAll('[data-artifact-image-index]'));",
            "var notes = Array.prototype.slice.call(modal.querySelectorAll('[data-artifact-note-index]'));",
            "var position = document.getElementById('artifact-position');",
            "var visible = cards.map(function(_, i){ return i; });",
            "var active = 0;",
            "function updateCount(){ if (count) count.textContent = visible.length + ' / ' + cards.length + ' visible'; }",
            "function syncModal(){",
            "images.forEach(function(el, i){ el.style.display = i === active ? 'block' : 'none'; });",
            "notes.forEach(function(el, i){ el.style.display = i === active ? 'block' : 'none'; });",
            "if (position) position.textContent = (active + 1) + ' / ' + images.length;",
            "}",
            "function openAt(i){ if (!images.length) return; active = (i + images.length) % images.length; modal.hidden = false; document.body.style.overflow = 'hidden'; syncModal(); }",
            "function closeModal(){ modal.hidden = true; document.body.style.overflow = ''; }",
            "cards.forEach(function(card){ card.addEventListener('click', function(){ openAt(Number(card.getAttribute('data-artifact-open')) || 0); }); });",
            "modal.addEventListener('click', function(e){",
            "if (e.target.closest('[data-artifact-close]')) closeModal();",
            "if (e.target.closest('[data-artifact-prev]')) openAt(active - 1);",
            "if (e.target.closest('[data-artifact-next]')) openAt(active + 1);",
            "});",
            "document.addEventListener('keydown', function(e){",
            "if (modal.hidden) return;",
            "if (e.key === 'Escape') closeModal();",
            "if (e.key === 'ArrowLeft') openAt(active - 1);",
            "if (e.key === 'ArrowRight') openAt(active + 1);",
            "});",
            "if (search){",
            "search.addEventListener('input', function(){",
            "var q = search.value.trim().toLowerCase();",
            "visible = [];",
            "cards.forEach(function(card, idx){",
            "var txt = card.textContent.toLowerCase();",
            "var note = (notes[idx] && notes[idx].textContent || '').toLowerCase();",
            "var show = !q || txt.indexOf(q) >= 0 || note.indexOf(q) >= 0;",
            "card.style.display = show ? 'block' : 'none';",
            "if (show) visible.push(idx);",
            "});",
            "updateCount();",
            "});",
            "}",
            "updateCount();",
            "syncModal();",
            "})();",
            "</script>",
        ]
    )


def build_artifact_viewer_html(image_urls):
    if not image_urls:
        return ""

    thumb_lines = []
    for idx, url in enumerate(image_urls):
        alt = f"Artifact {idx + 1}"
        thumb_lines.append(
            f'<button type="button" class="artifact-thumb" data-artifact-index="{idx}" aria-label="Open {alt}">'
            f'<img src="{url}" alt="{alt}" loading="lazy">'
            "</button>"
        )

    modal_items = []
    for idx, url in enumerate(image_urls):
        alt = f"Artifact {idx + 1}"
        modal_items.append(
            f'<img src="{url}" alt="{alt}" class="artifact-modal-image" data-artifact-image-index="{idx}" loading="lazy">'
        )

    return "\n".join(
        [
            '<section class="artifact-viewer">',
            '<h2>ARTIFACTS</h2>',
            '<div class="artifact-grid">',
            *thumb_lines,
            "</div>",
            "</section>",
            '<div class="artifact-modal" hidden>',
            '<div class="artifact-modal-backdrop" data-artifact-close="1"></div>',
            '<div class="artifact-modal-content" role="dialog" aria-modal="true" aria-label="Artifact viewer">',
            '<button type="button" class="artifact-nav artifact-prev" data-artifact-prev="1" aria-label="Previous image">&#8592;</button>',
            '<div class="artifact-modal-stage">',
            *modal_items,
            "</div>",
            '<button type="button" class="artifact-nav artifact-next" data-artifact-next="1" aria-label="Next image">&#8594;</button>',
            '<button type="button" class="artifact-close" data-artifact-close="1" aria-label="Close viewer">&#10005;</button>',
            "</div>",
            "</div>",
            "<script>",
            "(function(){",
            "var root = document.currentScript && document.currentScript.previousElementSibling;",
            "while (root && !root.classList.contains('artifact-modal')) root = root.previousElementSibling;",
            "if (!root) return;",
            "var section = root.previousElementSibling;",
            "if (!section || !section.classList.contains('artifact-viewer')) return;",
            "var thumbs = Array.prototype.slice.call(section.querySelectorAll('[data-artifact-index]'));",
            "var images = Array.prototype.slice.call(root.querySelectorAll('[data-artifact-image-index]'));",
            "if (!thumbs.length || !images.length) return;",
            "var active = 0;",
            "function sync(){",
            "images.forEach(function(img, i){ img.style.display = i === active ? 'block' : 'none'; });",
            "}",
            "function openAt(i){",
            "active = (i + images.length) % images.length;",
            "root.hidden = false;",
            "document.body.style.overflow = 'hidden';",
            "sync();",
            "}",
            "function close(){",
            "root.hidden = true;",
            "document.body.style.overflow = '';",
            "}",
            "thumbs.forEach(function(btn){",
            "btn.addEventListener('click', function(){ openAt(Number(btn.getAttribute('data-artifact-index')) || 0); });",
            "});",
            "root.addEventListener('click', function(e){",
            "if (e.target.closest('[data-artifact-close]')) close();",
            "if (e.target.closest('[data-artifact-prev]')) { openAt(active - 1); }",
            "if (e.target.closest('[data-artifact-next]')) { openAt(active + 1); }",
            "});",
            "document.addEventListener('keydown', function(e){",
            "if (root.hidden) return;",
            "if (e.key === 'Escape') close();",
            "if (e.key === 'ArrowLeft') openAt(active - 1);",
            "if (e.key === 'ArrowRight') openAt(active + 1);",
            "});",
            "sync();",
            "})();",
            "</script>",
        ]
    )


def parse_date_yyyy_mm_dd(value):
    if not value or not DATE_RE.match(value):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def build_sidebar_links(active, prefix):
    links = [
        ("about", "ABOUT", f"{prefix}index.html"),
        ("projects", "PROJECTS", f"{prefix}projects.html"),
    ]

    rendered = []
    for key, label, href in links:
        class_attr = ' class="active"' if key == active else ""
        rendered.append(f'<a href="{href}"{class_attr}>{label}</a>')

    rendered.append(f'<a href="{prefix}cv.pdf" target="_blank">CV</a>')
    return "\n\t\t\t\t".join(rendered)


def render_page(*, output_rel_path, title, active, content_html, mathjax=False):
    template = read_text(BASE_TEMPLATE_PATH)
    prefix = rel_prefix(output_rel_path)

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{STYLESHEET_PATH}}", f"{prefix}style.css")
    use_mathjax = mathjax or contains_math_markup(content_html)
    html = html.replace("{{MATHJAX}}", MATHJAX_SCRIPT if use_mathjax else "")
    html = html.replace("{{EXTRA_HEAD}}", "")
    html = html.replace("{{SIDEBAR_LINKS}}", build_sidebar_links(active, prefix))
    html = html.replace("{{CONTENT}}", content_html.strip())

    write_text(os.path.join(ROOT, output_rel_path), html + "\n")


def build_about():
    source_candidates = [
        os.path.join(CONTENT_DIR, "about.md"),
        os.path.join(CONTENT_DIR, "about.html"),
    ]
    source_path = None
    for candidate in source_candidates:
        if os.path.exists(candidate):
            source_path = candidate
            break

    if source_path is None:
        raise FileNotFoundError("Expected content/about.md or content/about.html")

    _, body_html = render_source_body(source_path)
    render_page(
        output_rel_path="index.html",
        title="SHAMIT",
        active="about",
        content_html=body_html,
    )


def load_project_posts(project_dir, project_slug):
    posts = []
    pages_dir = os.path.join(project_dir, "pages")
    source_dir = pages_dir if os.path.isdir(pages_dir) else project_dir
    uses_pages_dir = source_dir == pages_dir

    for fname in discover_preferred_entries(source_dir):
        stem, _ = os.path.splitext(fname)
        if stem == "index":
            continue

        src_path = os.path.join(source_dir, fname)
        metadata, body_html = render_source_body(src_path)

        post_title = metadata.get("title", extract_title(body_html, stem.replace("-", " ").title()))
        page_id = metadata.get("page-id", "")
        topics = metadata.get("topics", "")
        post_summary = metadata.get("summary", "")
        post_date_raw = metadata.get("date", "")
        post_date_obj = parse_date_yyyy_mm_dd(post_date_raw) if post_date_raw else None

        if uses_pages_dir:
            output_rel = os.path.join("projects", project_slug, "pages", f"{stem}.html")
        else:
            output_rel = os.path.join("projects", project_slug, f"{stem}.html")
        posts.append(
            {
                "slug": stem,
                "page_id": page_id,
                "title": post_title,
                "topics": topics,
                "summary": post_summary,
                "date": post_date_raw,
                "date_obj": post_date_obj,
                "body_html": body_html,
                "source": src_path,
                "output_rel": output_rel,
                "uses_pages_dir": uses_pages_dir,
                "href": output_rel.replace(os.sep, "/"),
            }
        )

    deduped_posts = []
    seen_signatures = set()
    for post in posts:
        signature = (
            post["title"].strip().lower(),
            post["topics"].strip().lower(),
            post["body_html"].strip(),
        )
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        deduped_posts.append(post)

    posts = deduped_posts

    posts.sort(key=lambda x: x["title"].lower())
    assign_missing_two_digit_ids(posts, "page_id")
    posts.sort(key=lambda x: (x["page_id"], x["title"].lower()))

    return posts


def load_projects():
    normalize_all_project_structures()
    os.makedirs(PROJECTS_CONTENT_DIR, exist_ok=True)
    projects = []

    for name in sorted(os.listdir(PROJECTS_CONTENT_DIR)):
        full = os.path.join(PROJECTS_CONTENT_DIR, name)

        if os.path.isdir(full):
            source_path = None
            for candidate in ("index.md", "index.html"):
                maybe = os.path.join(full, candidate)
                if os.path.exists(maybe):
                    source_path = maybe
                    break

            if source_path is None:
                metadata = {}
                body_html = ""
                title = name.replace("-", " ").upper()
            else:
                metadata, body_html = render_source_body(source_path)
                title = metadata.get("title", extract_title(body_html, name))

            project_id = metadata.get("project-id", "")
            status = metadata.get("status", "active")
            summary = metadata.get("summary", "Project write-up")
            topics = metadata.get("topics", "")

            posts = load_project_posts(full, name)
            if not posts:
                continue
            image_relpaths = list_project_image_relpaths(full)
            artifact_notes = parse_artifact_notes(full)
            projects.append(
                {
                    "slug": name,
                    "title": title,
                    "project_id": project_id,
                    "status": status,
                    "summary": summary,
                    "topics": topics,
                    "body_html": body_html,
                    "source": source_path or full,
                    "posts": posts,
                    "image_relpaths": image_relpaths,
                    "images_source_dir": os.path.join(full, "images"),
                    "artifact_notes": artifact_notes,
                }
            )
            continue

    projects.sort(key=lambda x: x["title"].lower())
    assign_missing_two_digit_ids(projects, "project_id")
    projects.sort(key=lambda x: (x["project_id"], x["title"].lower()))
    return projects


def render_project_page(project):
    project_output_dir = os.path.join(ROOT, "projects", project["slug"])
    if os.path.isdir(project_output_dir):
        shutil.rmtree(project_output_dir)
    os.makedirs(project_output_dir, exist_ok=True)

    if os.path.isdir(project["images_source_dir"]):
        shutil.copytree(project["images_source_dir"], os.path.join(project_output_dir, "images"), dirs_exist_ok=True)

    for post in project["posts"]:
        render_page(
            output_rel_path=post["output_rel"],
            title=post["title"],
            active="projects",
            content_html=post["body_html"],
        )

    render_page(
        output_rel_path=os.path.join("projects", project["slug"], "artifacts.html"),
        title=f"{project['title']} ARTIFACTS",
        active="projects",
        content_html=build_project_artifacts_page(project),
    )


def render_projects():
    projects = load_projects()

    for project in projects:
        render_project_page(project)

    index_lines = [
        "<h1>PROJECTS</h1>",
        "<p>Archive index of project pages.</p>",
        '<pre class="index">',
    ]

    for project in projects:
        project_topics = f'  [{project["topics"]}]' if project["topics"] else ""
        index_lines.append(f'[{project["project_id"]}] {project["title"]}{project_topics}')

        for post in project["posts"]:
            archive_id = f'{project["project_id"]}{post["page_id"]}'
            post_topics = f'  [{post["topics"]}]' if post["topics"] else ""
            index_lines.append(
                f'    <a href="{post["href"]}">{archive_id} {post["title"]}</a>'
                f"{post_topics}"
            )
        index_lines.append(
            f'    <a href="projects/{project["slug"]}/artifacts.html">VIEW ARTIFACTS</a>'
        )

    index_lines.append("</pre>")

    render_page(
        output_rel_path="projects.html",
        title="PROJECTS",
        active="projects",
        content_html="\n".join(index_lines),
    )


def validate_content():
    errors = []
    projects = load_projects()
    seen_project_ids = set()

    for project in projects:
        if project["project_id"].strip() and not TWO_DIGIT_RE.match(project["project_id"]):
            errors.append(f"[projects] Invalid project-id='{project['project_id']}' in {project['source']} (expected 2 digits)")
        elif project["project_id"] in seen_project_ids:
            errors.append(f"[projects] Duplicate project-id='{project['project_id']}'")
        else:
            seen_project_ids.add(project["project_id"])

        if not project["title"].strip():
            errors.append(f"[projects] Missing 'title' in {project['source']}")

        seen_page_ids = set()
        for post in project["posts"]:
            if not post["title"].strip():
                errors.append(f"[projects] Missing 'title' in {post['source']}")
            if post["page_id"].strip() and not TWO_DIGIT_RE.match(post["page_id"]):
                errors.append(f"[projects] Invalid page-id='{post['page_id']}' in {post['source']} (expected 2 digits)")
            elif post["page_id"] in seen_page_ids:
                errors.append(f"[projects] Duplicate page-id='{post['page_id']}' in project-id='{project['project_id']}'")
            else:
                seen_page_ids.add(post["page_id"])
            if post["date"] and post["date_obj"] is None:
                errors.append(f"[projects] Invalid date='{post['date']}' in {post['source']} (expected YYYY-MM-DD)")

    if errors:
        print("Validation failed:\n")
        for err in errors:
            print(f"- {err}")
        return False

    print("Validation passed.")
    return True


def slugify(raw):
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ValueError("Slug cannot be empty")
    return value


def render_template(template_name, replacements):
    template_path = os.path.join(SECTION_TEMPLATE_DIR, template_name)
    if os.path.exists(template_path):
        template = read_text(template_path)
    else:
        raise FileNotFoundError(f"Missing template: {template_path}")

    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def scaffold_project(slug, title):
    project_slug = slugify(slug)
    target_dir = os.path.join(PROJECTS_CONTENT_DIR, project_slug)
    target_path = os.path.join(target_dir, "index.md")

    if os.path.exists(target_path):
        raise FileExistsError(f"Project already exists: {target_path}")

    os.makedirs(target_dir, exist_ok=True)
    existing_project_dirs = [
        name for name in os.listdir(PROJECTS_CONTENT_DIR)
        if os.path.isdir(os.path.join(PROJECTS_CONTENT_DIR, name))
    ]
    next_project_id = f"{len(existing_project_dirs) + 1:02d}"

    content = render_template(
        "projects.md",
        {
            "{{ID}}": next_project_id,
            "{{TITLE}}": title.strip(),
            "{{DATE}}": dt.date.today().isoformat(),
        },
    )
    write_text(target_path, content)
    return target_path


def scaffold_project_post(project, slug, title):
    project_slug = slugify(project)
    post_slug = slugify(slug)

    project_dir = os.path.join(PROJECTS_CONTENT_DIR, project_slug)
    index_md = os.path.join(project_dir, "index.md")
    index_html = os.path.join(project_dir, "index.html")
    pages_dir = os.path.join(project_dir, "pages")
    if not os.path.exists(index_md) and not os.path.exists(index_html):
        raise FileNotFoundError(f"Project '{project_slug}' does not exist in content/projects")

    target_parent = pages_dir if os.path.isdir(pages_dir) else project_dir

    target_path = os.path.join(target_parent, f"{post_slug}.md")
    if os.path.exists(target_path):
        raise FileExistsError(f"Post already exists: {target_path}")

    existing_posts = [
        fname for fname in os.listdir(target_parent)
        if os.path.splitext(fname)[0] != "index" and os.path.splitext(fname)[1] in {".md", ".html"}
    ]
    next_page_id = f"{len(existing_posts) + 1:02d}"

    content = render_template(
        "project-post.md",
        {
            "{{PROJECT}}": project_slug,
            "{{ID}}": post_slug,
            "{{TITLE}}": title.strip(),
            "{{PAGE_ID}}": next_page_id,
        },
    )
    write_text(target_path, content)
    return target_path


def build_all():
    build_about()
    render_projects()
