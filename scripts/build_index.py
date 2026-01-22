from pathlib import Path
from datetime import date

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
<div class="layout">
<nav class="sidebar">
<div class="name">Your Name</div>
<a href="index.html">About</a>
<a href="projects.html"{projects_active}>Projects</a>
<a href="putnam.html"{putnam_active}>Putnam</a>
<a href="imc.html"{imc_active}>IMC</a>
<a href="cv.pdf" target="_blank">CV</a>
</nav>
<main class="content">
<h1>{title}</h1>
<pre class="index">
{rows}
</pre>
</main>
</div>
</body>
</html>
"""


def build_index(name):
    folder = Path(name)
    files = sorted(folder.glob("*.html"))

    today = date.today().isoformat()
    rows = [(f.stem, today) for f in files]

    if rows:
        pid_width = max(len(pid) for pid, _ in rows)
        lines = [
            f'<a href="{name}/{pid}.html">{pid.ljust(pid_width)}</a>  {d}'
            for pid, d in rows
        ]
        body = "\n".join(lines)
    else:
        body = "(no entries yet)"

    html = TEMPLATE.format(
        title=name.upper(),
        rows=body,
        projects_active=' class="active"' if name == "projects" else "",
        putnam_active=' class="active"' if name == "putnam" else "",
        imc_active=' class="active"' if name == "imc" else "",
    )

    Path(f"{name}.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_index("projects")
    build_index("putnam")
    build_index("imc")
