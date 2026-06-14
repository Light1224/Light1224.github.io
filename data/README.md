# Site data

Each file maps to one part of the site. Edit the file for the section you want to change.

| File | What to edit |
|------|----------------|
| `meta.json` | Site name, last updated date, sidebar nav, external links |
| `about.json` | About Me page |
| `education.json` | Education & Skills page |
| `experience.json` | Experience entries (array — add `{ ... }` objects) |
| `projects.json` | Project entries (array — add `{ ... }` objects) |
| `blog.json` | Blog intro and posts |
| `reading.json` | Reading list |
| `contact.json` | Contact page |

## Quick examples

**New experience entry** — append to `experience.json`:

```json
{
  "title": "Company — Role",
  "href": "https://company-website.com",
  "meta": "Intern · Jun 2026 – Aug 2026 · City",
  "bullets": ["First accomplishment.", "Second accomplishment."]
}
```

`href` is optional — omit it if the organization has no link.

**Coursework** — edit `education.json` → `school.coursework`:

```json
{
  "title": "Minor in Data Science",
  "courses": [
    "Machine Learning",
    "Course Title — add here"
  ]
}
```

Add objects for each track (e.g. `Minor in Data Science`, `ECE`). Append course names to the `courses` array.

**New project** — append to `projects.json`:

```json
{
  "title": "Project Name",
  "meta": "Mar 2026 · Independent",
  "summary": "One-line description.",
  "bullets": ["Result one.", "Result two."],
  "links": [{ "label": "GitHub", "href": "https://github.com/..." }]
}
```

**New book** — append to `reading.json` → `books`:

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "href": "https://example.com",
  "note": "Optional: why you recommend it."
}
```

`href` and `note` are optional.

**New blog post** — add metadata to `blog.json` → `posts`, then create `blog/posts/your-slug.json` with the full article body:

`blog.json`:
```json
{
  "slug": "your-slug",
  "title": "Post title",
  "date": "2026-03-01",
  "summary": "Short summary for the list page."
}
```

`blog/posts/your-slug.json`:
```json
{
  "body": [
    { "type": "paragraph", "text": "Opening paragraph." },
    { "type": "heading", "text": "Section title" },
    { "type": "list", "items": ["Point one.", "Point two."] }
  ]
}
```

Body block types: `paragraph`, `heading`, `list`. The post is served at `post.html?slug=your-slug`.

Posts are sorted **latest to oldest** by `date` on the blog page. Order in the JSON file does not matter.

For external posts only, omit `slug` and use `"href": "https://..."` in `blog.json` instead.

**Footer date** — update `lastUpdated` in `meta.json`.

**New sidebar page** — add to `nav` in `meta.json` and create a matching HTML shell in the project root.
