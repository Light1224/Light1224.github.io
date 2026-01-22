import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECTIONS = {
    "putnam": {"dir": "putnam", "index": "putnam.html", "title": "PUTNAM"},
    "imc": {"dir": "imc", "index": "imc.html", "title": "IMC"},
}

ID_RE = re.compile(r"problem-id:\s*([^\s<]+)", re.IGNORECASE)
STATUS_RE = re.compile(r"status:\s*([^\s<]+)", re.IGNORECASE)


def extract_metadata(path):
    pid = None
    status = "unknown"

    with open(path, encoding="utf-8") as f:
        for _ in range(30):
            line = f.readline()
            if not line:
                break

            if pid is None:
                m = ID_RE.search(line)
                if m:
                    pid = m.group(1).strip()

            m = STATUS_RE.search(line)
            if m:
                status = m.group(1).strip().lower()

            if pid and status != "unknown":
                break

    if pid is None:
        pid = os.path.splitext(os.path.basename(path))[0]

    return pid, status


def build_section(section):
    base_dir = os.path.join(ROOT, section["dir"])
    index_path = os.path.join(ROOT, section["index"])

    entries = []

    for fname in sorted(os.listdir(base_dir)):
        if not fname.endswith(".html"):
            continue

        full_path = os.path.join(base_dir, fname)
        pid, status = extract_metadata(full_path)
        entries.append((pid, status, fname))

    with open(index_path, "w", encoding="utf-8") as out:
        out.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{section["title"]}</title>
<link rel="stylesheet" href="style.css">
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
<div class="layout">
<nav class="sidebar">
<div class="name">SHAMIT</div>
<div class="line"></div>
<a href="index.html">About</a>
<a href="projects.html">Projects</a>
<a href="putnam.html"{' class="active"' if section["title"] == "PUTNAM" else ""}>Putnam</a>
<a href="imc.html"{' class="active"' if section["title"] == "IMC" else ""}>IMC</a>
<a href="cv.pdf" target="_blank">CV</a>
</nav>
<main class="content">
<h1>{section["title"]}</h1>
<pre class="index">
""")

        for pid, status, fname in entries:
            out.write(f'<a href="{section["dir"]}/{fname}">{pid}</a>  [{status}]\n')

        out.write("""</pre>
</main>
</div>
</body>
</html>
""")


def main():
    for section in SECTIONS.values():
        build_section(section)
    print("Indexes rebuilt successfully.")


if __name__ == "__main__":
    main()
