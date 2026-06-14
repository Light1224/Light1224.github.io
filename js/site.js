const DATA_DIR = new URL("../data/", import.meta.url);

const DATA_FILES = {
  meta: "meta.json",
  about: "about.json",
  education: "education.json",
  experience: "experience.json",
  projects: "projects.json",
  blog: "blog.json",
  reading: "reading.json",
  contact: "contact.json",
};

async function fetchJson(file) {
  const response = await fetch(new URL(file, DATA_DIR));
  if (!response.ok) {
    throw new Error(`Failed to load data/${file} (${response.status})`);
  }
  return response.json();
}

async function loadBlogPostBody(slug) {
  const response = await fetch(new URL(`blog/posts/${slug}.json`, DATA_DIR));
  if (!response.ok) {
    throw new Error(`Failed to load blog post "${slug}" (${response.status})`);
  }
  return response.json();
}

function findBlogPost(data, slug) {
  return data.blog.posts.find((post) => post.slug === slug);
}

function postPageUrl(slug) {
  return `post.html?slug=${encodeURIComponent(slug)}`;
}

async function loadSiteData() {
  const [meta, about, education, experience, projects, blog, reading, contact] = await Promise.all([
    fetchJson(DATA_FILES.meta),
    fetchJson(DATA_FILES.about),
    fetchJson(DATA_FILES.education),
    fetchJson(DATA_FILES.experience),
    fetchJson(DATA_FILES.projects),
    fetchJson(DATA_FILES.blog),
    fetchJson(DATA_FILES.reading),
    fetchJson(DATA_FILES.contact),
  ]);

  return {
    meta: {
      name: meta.name,
      lastUpdated: meta.lastUpdated,
    },
    nav: meta.nav,
    external: meta.external,
    about,
    education,
    experience,
    projects,
    blog,
    reading,
    contact,
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function externalAttrs(href) {
  if (href.startsWith("http") || href.toLowerCase().endsWith(".pdf")) {
    return ' target="_blank" rel="noopener noreferrer"';
  }
  return "";
}

function renderLine(line) {
  if (typeof line === "string") {
    return escapeHtml(line);
  }

  return `<a href="${escapeHtml(line.href)}"${externalAttrs(line.href)}>${escapeHtml(line.text)}</a>`;
}

function sectionBar(title) {
  return `<div class="section-bar"><h2>${escapeHtml(title)}</h2></div>`;
}

function renderBullets(items) {
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderEntryTitle(title, href) {
  if (href) {
    return `<h3><a href="${escapeHtml(href)}"${externalAttrs(href)}>${escapeHtml(title)}</a></h3>`;
  }

  return `<h3>${escapeHtml(title)}</h3>`;
}

function renderEntry({ title, href, meta, summary, bullets, links }) {
  const summaryHtml = summary ? `<p class="entry-summary">${escapeHtml(summary)}</p>` : "";
  const linksHtml = links?.length
    ? `<p class="entry-links">${links
        .map(
          (link) =>
            `<a href="${escapeHtml(link.href)}"${externalAttrs(link.href)}>${escapeHtml(link.label)}</a>`
        )
        .join(" · ")}</p>`
    : "";

  return `
    <article class="entry">
      <header class="entry-header">
        ${renderEntryTitle(title, href)}
        ${meta ? `<p class="meta">${escapeHtml(meta)}</p>` : ""}
      </header>
      ${summaryHtml}
      ${bullets ? renderBullets(bullets) : ""}
      ${linksHtml}
    </article>
  `;
}

function renderSidebar(data, activePage) {
  const navLinks = data.nav
    .map((item) => {
      const isActive = item.id === activePage;
      const activeClass = isActive ? " active" : "";
      const ariaCurrent = isActive ? ' aria-current="page"' : "";
      return `<a href="${escapeHtml(item.href)}" class="nav-link${activeClass}"${ariaCurrent}>${escapeHtml(item.label)}</a>`;
    })
    .join("");

  const externalLinks = data.external
    .map(
      (item) =>
        `<a class="external-link" href="${escapeHtml(item.href)}"${externalAttrs(item.href)}>${escapeHtml(item.label)}</a>`
    )
    .join("");

  return `
    <div class="sidebar-inner">
      <div class="sidebar-header">
        <a class="site-name" href="index.html">${escapeHtml(data.meta.name)}</a>
      </div>

      <div class="sidebar-section">
        <span class="nav-label">pages</span>
        <div class="sidebar-links">${navLinks}</div>
      </div>

      <div class="sidebar-section">
        <span class="nav-label">external</span>
        <div class="sidebar-links">${externalLinks}</div>
      </div>
    </div>
  `;
}

function renderAbout(data) {
  const { about } = data;
  const introLines = about.intro.lines.map((line) => renderLine(line)).join("<br>");

  return `
    <h1>${escapeHtml(about.title)}</h1>
    <p>
      <b>${escapeHtml(about.intro.name)}</b><br>
      ${introLines}
    </p>
    <p>${escapeHtml(about.intro.bio)}</p>
  `;
}

function renderEducation(data) {
  const { education } = data;
  const schoolLines = education.school.lines.map((line) => escapeHtml(line)).join("<br>");

  const courseworkHtml = education.school.coursework
    .map(
      (group) => `
        <div class="coursework-group">
          <p><b>${escapeHtml(group.title)}</b><br>${group.courses.map((course) => escapeHtml(course)).join(", ")}</p>
        </div>
      `
    )
    .join("");

  const skillsHtml = education.skills
    .map(
      (group) => `
        <div class="info-block">
          <p><b>${escapeHtml(group.title)}</b><br>${group.lines.map((line) => escapeHtml(line)).join("<br>")}</p>
        </div>
      `
    )
    .join("");

  return `
    <h1>${escapeHtml(education.title)}</h1>
    ${sectionBar("Education")}
    <p>
      <b>${escapeHtml(education.school.title)}</b><br>
      ${schoolLines}
    </p>
    ${sectionBar("Coursework")}
    ${courseworkHtml}
    ${sectionBar("Skills")}
    ${skillsHtml}
  `;
}

function renderExperience(data) {
  const entries = data.experience.map((entry) => renderEntry(entry)).join("");

  return `
    <h1>Experience</h1>
    ${entries || "<p>No entries yet.</p>"}
  `;
}

function renderProjects(data) {
  const entries = data.projects.map((entry) => renderEntry(entry)).join("");

  return `
    <h1>Projects</h1>
    ${entries || "<p>No entries yet.</p>"}
  `;
}

function postDateValue(date) {
  if (!date) {
    return 0;
  }

  const value = Date.parse(date);
  return Number.isNaN(value) ? 0 : value;
}

function sortBlogPosts(posts) {
  return [...posts].sort((a, b) => postDateValue(b.date) - postDateValue(a.date));
}

function renderBlogIndexItem(post) {
  const postUrl = post.slug ? postPageUrl(post.slug) : post.href;
  const isInternal = Boolean(post.slug);

  const titleHtml = postUrl
    ? `<a href="${escapeHtml(postUrl)}" class="blog-index-title"${isInternal ? "" : externalAttrs(postUrl)}>${escapeHtml(post.title)}</a>`
    : `<span class="blog-index-title">${escapeHtml(post.title)}</span>`;

  return `
    <li class="blog-index-item">
      <span class="blog-index-date">${escapeHtml(post.date || "")}</span>
      ${titleHtml}
    </li>
  `;
}

function renderBlogBodyBlock(block) {
  if (block.type === "heading") {
    return `<h2 class="article-heading">${escapeHtml(block.text)}</h2>`;
  }

  if (block.type === "list") {
    return `<ul class="article-list">${block.items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  }

  return `<p>${escapeHtml(block.text)}</p>`;
}

async function renderBlogArticle(data, slug) {
  const post = findBlogPost(data, slug);
  if (!post) {
    return `<h1>Post not found</h1><p><a href="blog.html">Back to blog</a></p>`;
  }

  const { body } = await loadBlogPostBody(slug);
  const bodyHtml = body.map((block) => renderBlogBodyBlock(block)).join("");

  document.title = `Shamit Sai — ${post.title}`;

  return `
    <div class="article-wrap">
      <p class="blog-back"><a href="blog.html">← Back to blog</a></p>
      <article class="article">
        <header class="article-header">
          <h1>${escapeHtml(post.title)}</h1>
          ${post.date ? `<p class="meta article-date">${escapeHtml(post.date)}</p>` : ""}
          ${post.summary ? `<p class="article-lede">${escapeHtml(post.summary)}</p>` : ""}
        </header>
        <div class="article-body">
          ${bodyHtml}
        </div>
      </article>
    </div>
  `;
}

function renderBlog(data) {
  const { blog } = data;
  const posts = sortBlogPosts(blog.posts);
  const indexHtml = posts.length
    ? `
      ${sectionBar("Index")}
      <ol class="blog-index">
        ${posts.map((post) => renderBlogIndexItem(post)).join("")}
      </ol>
    `
    : `<p class="blog-empty">No posts yet.</p>`;

  return `
    <h1>${escapeHtml(blog.title)}</h1>
    <p class="blog-intro">${escapeHtml(blog.intro)}</p>
    ${indexHtml}
  `;
}

function renderReadingItem(book) {
  const titleHtml = book.href
    ? `<a href="${escapeHtml(book.href)}" class="reading-index-title"${externalAttrs(book.href)}>${escapeHtml(book.title)}</a>`
    : `<span class="reading-index-title">${escapeHtml(book.title)}</span>`;

  const noteHtml = book.note ? `<span class="reading-index-note">${escapeHtml(book.note)}</span>` : "";

  return `
    <li class="reading-index-item">
      <div class="reading-index-main">
        ${titleHtml}
        ${noteHtml}
      </div>
      <span class="reading-index-author">${escapeHtml(book.author || "")}</span>
    </li>
  `;
}

function renderReading(data) {
  const { reading } = data;
  const indexHtml = reading.books?.length
    ? `
      ${sectionBar("Index")}
      <ol class="reading-index">
        ${reading.books.map((book) => renderReadingItem(book)).join("")}
      </ol>
    `
    : `<p class="reading-empty">No books listed yet.</p>`;

  return `
    <h1>${escapeHtml(reading.title)}</h1>
    <p class="reading-intro">${escapeHtml(reading.intro)}</p>
    ${indexHtml}
  `;
}

function renderContactItem(item) {
  return `
    <div class="contact-row">
      <dt>${escapeHtml(item.label)}</dt>
      <dd><a href="${escapeHtml(item.href)}"${externalAttrs(item.href)}>${escapeHtml(item.text)}</a></dd>
    </div>
  `;
}

function renderContactSection(section) {
  const rows = section.items.map((item) => renderContactItem(item)).join("");

  return `
    ${sectionBar(section.title)}
    <dl class="contact-list">${rows}</dl>
  `;
}

function renderContact(data) {
  const { contact } = data;
  const primary = contact.sections
    .flatMap((section) => section.items)
    .find((item) => item.primary);

  const primaryHtml = primary
    ? `
      <div class="contact-primary">
        <span class="contact-primary-label">${escapeHtml(primary.label)}</span>
        <a class="contact-primary-link" href="${escapeHtml(primary.href)}"${externalAttrs(primary.href)}>${escapeHtml(primary.text)}</a>
      </div>
    `
    : "";

  const sectionsHtml = contact.sections.map((section) => renderContactSection(section)).join("");
  const noteHtml = contact.note
    ? `<p class="contact-note">${escapeHtml(contact.note)}</p>`
    : "";

  return `
    <h1>${escapeHtml(contact.title)}</h1>
    <p class="contact-intro">${escapeHtml(contact.intro)}</p>
    ${primaryHtml}
    ${sectionsHtml}
    ${noteHtml}
  `;
}

const pageRenderers = {
  about: renderAbout,
  education: renderEducation,
  experience: renderExperience,
  projects: renderProjects,
  blog: renderBlog,
  reading: renderReading,
  contact: renderContact,
};

async function init() {
  const activePage = document.body.dataset.page;
  const sidebar = document.getElementById("sidebar");
  const main = document.getElementById("main");
  const footer = document.getElementById("footer");

  if (!activePage || !sidebar || !main || !footer) {
    return;
  }

  const navActive = activePage === "blog-post" ? "blog" : activePage;

  try {
    const data = await loadSiteData();
    sidebar.innerHTML = renderSidebar(data, navActive);

    if (activePage === "blog-post") {
      const slug = new URLSearchParams(window.location.search).get("slug");
      if (!slug) {
        main.innerHTML = `<h1>Post not found</h1><p><a href="blog.html">Back to blog</a></p>`;
      } else {
        main.innerHTML = await renderBlogArticle(data, slug);
      }
    } else {
      const renderPage = pageRenderers[activePage];
      if (!renderPage) {
        main.innerHTML = "<p>Page not found.</p>";
        return;
      }
      main.innerHTML = renderPage(data);
    }

    footer.textContent = `last updated: ${data.meta.lastUpdated}`;
  } catch (error) {
    main.innerHTML = "<p>Could not load page content. Serve the site over HTTP (not file://).</p>";
    footer.textContent = "";
    console.error(error);
  }
}

init();
