from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Iterable

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
ARTICLE_TEMPLATE = "article-template.html"
SITE_NAME = "James Cullimore"
SITE_ROLE = "Software Engineering"
SITE_TITLE = f"{SITE_NAME} {SITE_ROLE}"
SITE_URL = "https://jamescullimore.dev"
COPYRIGHT_YEAR = "2026"
VERIFIED_MEDIUM_DATES = {
    "accessibility-amplified-a-journey-to-inclusive-android-apps.html": "2024-02-01",
    "android-symphony-a-ux-melody-with-tooltips-popups-and-dialogs.html": "2024-02-01",
    "artifactory-secrets-unveiled-maximizing-android-projects-with-private-module-publishing.html": "2024-04-10",
    "breaking-and-defending-https-on-android-a-hands-on-certificate-pinning-lab.html": "2026-02-16",
    "building-a-reliable-control-handoff-with-the-wear-os-data-layer.html": "2026-02-11",
    "challenge-accepted-hacks-for-effortless-oauth2-login-testing-on-android.html": "2023-10-19",
    "compose-and-conquer-a-tale-of-effortless-android-navigation.html": "2023-12-15",
    "contribute-struggle-adjust-repeat-finding-work-life-balance-as-a-dev.html": "2025-07-25",
    "defending-against-mitm-attacks-the-android-certificate-pinning-approach.html": "2023-09-22",
    "defending-the-android-realm-proguards-role-in-app-security-and-efficiency.html": "2024-01-11",
    "diving-into-the-developers-dive-crafting-android-development-articles-for-android-developers.html": "2024-04-03",
    "diving-into-the-license-abyss-an-android-odyssey-through-font-image-and-library-licenses.html": "2023-08-11",
    "editable-config-files-a-ui-less-way-to-configure-android-apps-and-services.html": "2025-02-04",
    "fast-feedback-winning-back-60-of-our-ci-time.html": "2025-05-09",
    "git-it-together.html": "2024-12-15",
    "goodbye-androidview-a-real-camerax-qr-scanner-in-compose.html": "2026-01-14",
    "how-i-built-seamless-watch-phone-handover-in-wear-os.html": "2025-07-02",
    "how-i-cut-my-gradle-build-time-by-50.html": "2025-04-07",
    "how-i-tackled-parsing-xml-on-android-when-jaxb-just-wouldnt-play-nice.html": "2025-04-14",
    "leveling-up-the-dev-dungeon-with-ml-kits-text-recognition.html": "2024-03-13",
    "locking-in-data-confidence-decoding-androids-encrypted-preferences-arsenal.html": "2023-12-23",
    "monetizing-marvels-a-developers-guide-to-in-app-purchases-on-android.html": "2024-02-21",
    "one-piece-of-code-picking-and-reading-files-like-a-true-pirate-king.html": "2024-11-16",
    "one-punch-one-scan-effortless-barcode-scanning-on-android-with-googles-ml-kit-jetpack-compose.html": "2024-04-16",
    "one-repo-to-rule-them-all-android-modules-with-git-submodules.html": "2025-07-25",
    "pixel-perfect-designing-for-every-screen-every-fold.html": "2024-02-06",
    "pixels-to-profits-monetizing-jetpack-compose-apps-with-admob.html": "2024-02-26",
    "permission-slips-and-flag-waving-navigating-the-android-development-skyline.html": "2024-02-14",
    "pip-boy-perfect-your-wasteland-survival-guide-to-maestro-ui-testing-on-android.html": "2024-04-24",
    "reshaping-the-network-layer-transitioning-from-retrofit-to-ktor.html": "2023-12-07",
    "room-to-grow-walking-through-the-gardens-of-android-databases.html": "2024-02-07",
    "say-goodbye-to-dependency-hell-simplify-your-android-development-with-version-catalogs.html": "2024-03-27",
    "spring-loaded-perfection-coil-and-jetpack-compose-for-effortless-image-loading.html": "2023-12-01",
    "stepping-into-the-alternative-universe-of-automated-testing-for-android-mobile-espresso.html": "2023-12-04",
    "stop-using-playerview-in-compose-media3-playersurface-done-right.html": "2026-01-19",
    "tailoring-apps-with-finesse-using-build-variants.html": "2023-08-16",
    "two-sides-of-200-android-interviews.html": "2025-06-25",
    "wear-os-seamless-handover.html": "2025-07-02",
    "wifi-wizardry-a-developers-guide-to-android-network-magic.html": "2023-09-30",
    "yo-ho-ho-and-a-heap-of-memory-leak-woes-leakcanary-to-the-rescue.html": "2023-12-24",
}


@dataclass(frozen=True)
class ArticleMeta:
    filename: str
    title: str
    description: str
    image: str
    canonical: str
    published_iso: str
    published_display: str
    read_time: str
    author: str

    @property
    def root_href(self) -> str:
        return f"articles/{self.filename}"

    @property
    def pages_href(self) -> str:
        return f"../articles/{self.filename}"

    @property
    def parsed_date(self) -> tuple[int, int, int]:
        try:
            dt = datetime.strptime(self.published_iso, "%Y-%m-%d")
            return (dt.year, dt.month, dt.day)
        except ValueError:
            return (0, 0, 0)


def read_article_meta(path: Path) -> ArticleMeta:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    title = soup.title.get_text(strip=True)
    description_tag = soup.find("meta", attrs={"name": "description"})
    image_tag = soup.find("meta", attrs={"property": "og:image"})
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    author_tag = soup.find("meta", attrs={"name": "author"})
    time_tag = soup.find("time", attrs={"datetime": True})
    meta_candidates = soup.select(".article-meta span, .article-meta time")
    read_time = next(
        (
            candidate.get_text(" ", strip=True)
            for candidate in meta_candidates
            if re.search(r"\b\d+\s+min read\b", candidate.get_text(" ", strip=True))
        ),
        "",
    )

    if not all([description_tag, image_tag, canonical_tag, author_tag, time_tag, read_time]):
        raise ValueError(f"Missing article metadata in {path.name}")

    return ArticleMeta(
        filename=path.name,
        title=title,
        description=description_tag["content"].strip(),
        image=image_tag["content"].strip(),
        canonical=canonical_tag["href"].strip(),
        published_iso=time_tag["datetime"].strip(),
        published_display=time_tag.get_text(" ", strip=True),
        read_time=read_time,
        author=author_tag["content"].strip(),
    )


def display_date(iso_date: str) -> str:
    return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%b %d, %Y").replace(" 0", " ")


def article_files() -> list[Path]:
    return sorted(
        path
        for path in ARTICLES_DIR.glob("*.html")
        if path.name not in {ARTICLE_TEMPLATE}
    )


def sort_articles(articles: Iterable[ArticleMeta]) -> list[ArticleMeta]:
    return sorted(
        articles,
        key=lambda item: (-item.parsed_date[0], -item.parsed_date[1], -item.parsed_date[2], item.title.lower()),
    )


def ensure_body_class(text: str, body_class: str) -> str:
    body_match = re.search(r"<body([^>]*)>", text)
    if not body_match:
        return text

    attrs = body_match.group(1)
    if "class=" in attrs:
        updated_attrs = re.sub(
            r'class="([^"]*)"',
            lambda m: f'class="{append_class(m.group(1), body_class)}"',
            attrs,
            count=1,
        )
    else:
        updated_attrs = f'{attrs} class="{body_class}"'
    return text[: body_match.start()] + f"<body{updated_attrs}>" + text[body_match.end() :]


def append_class(existing: str, extra: str) -> str:
    classes = [item for item in existing.split() if item]
    if extra not in classes:
        classes.append(extra)
    return " ".join(classes)


def ensure_stylesheet(text: str, href: str) -> str:
    if href in text:
        return text

    stylesheet_match = re.search(r'(\s*<link[^>]+rel="stylesheet"[^>]*>)', text)
    if stylesheet_match:
        return (
            text[: stylesheet_match.start()]
            + f'\n<link href="{href}" rel="stylesheet"/>'
            + text[stylesheet_match.start() :]
        )

    head_close = re.search(r"</head>", text)
    if head_close:
        return text[: head_close.start()] + f'\n<link href="{href}" rel="stylesheet"/>\n' + text[head_close.start() :]

    return text


def ensure_brand_link_styles(text: str) -> str:
    return text


def article_header(prefix: str) -> str:
    return f"""<header>
  <nav class="nav">
    <a href="{prefix}/index.html" class="article-brand-link" aria-label="{SITE_NAME} home">
      <div class="brand">
        <div class="brand-mark">JC</div>
        <div class="brand-text">
          <div class="brand-name">{SITE_NAME}</div>
          <div class="brand-role">{SITE_ROLE}</div>
        </div>
      </div>
    </a>
    <ul class="nav-links">
      <li><a href="{prefix}/index.html#overview">Overview</a></li>
      <li><a href="{prefix}/index.html#services">Services</a></li>
      <li><a href="{prefix}/index.html#how-we-work">How we work</a></li>
      <li><a href="{prefix}/index.html#projects">Projects</a></li>
      <li><a href="{prefix}/index.html#insights">Insights</a></li>
      <li><a href="{prefix}/index.html#contact">Contact</a></li>
      <li><a href="{prefix}/articles.html" class="nav-cta active">Blog</a></li>
    </ul>
  </nav>
</header>
"""


def site_footer(prefix: str) -> str:
    return f"""<footer>
  <div class="footer-inner">
    <div>© {COPYRIGHT_YEAR} {SITE_NAME}. All rights reserved.</div>
    <ul class="footer-links">
      <li><a href="{prefix}/articles.html">Blog</a></li>
      <li><a href="{prefix}/pages/impressum.html">Impressum</a></li>
      <li><a href="{prefix}/pages/datenschutz.html">Datenschutz</a></li>
    </ul>
  </div>
</footer>
"""


def build_article_footer(text: str) -> str:
    time_match = re.search(
        r'<time[^>]+datetime="([^"]+)"[^>]*>(.*?)</time>',
        text,
        re.S,
    )
    if time_match:
        iso = time_match.group(1).strip()
        display = time_match.group(2).strip()
        last_updated = f'<p>Published <time datetime="{iso}">{display}</time></p>'
    else:
        last_updated = ""

    return (
        '<footer class="article-footer">'
        f"{last_updated}"
        '<p><a href="../articles.html">Browse all articles</a></p>'
        f'<p class="article-footer-copy">© {COPYRIGHT_YEAR} {SITE_NAME}</p>'
        "</footer>"
    )


def apply_verified_date(path: Path, text: str) -> str:
    verified_date = VERIFIED_MEDIUM_DATES.get(path.name)
    if not verified_date:
        return text

    soup = BeautifulSoup(text, "html.parser")
    display = display_date(verified_date)

    for time_tag in soup.find_all("time"):
        if time_tag.get("datetime"):
            time_tag["datetime"] = verified_date
            time_tag.string = display

    for script_tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        script_text = script_tag.string or script_tag.get_text()
        if not script_text.strip():
            continue
        try:
            payload = json.loads(script_text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("@type") == "Article":
            payload["datePublished"] = verified_date
            payload["dateModified"] = verified_date
            script_tag.string = json.dumps(payload, indent=2, ensure_ascii=False)

    return str(soup)


def normalize_article_markup(path: Path, text: str) -> str:
    replacements = {
        'href="/img/favicon-32x32.png"': 'href="../img/favicon-32x32.png"',
        'href="/articles/assets/style.css"': 'href="assets/style.css"',
        'href="/articles/style.css"': 'href="style.css"',
        'href="/articles/assets/prism.css"': 'href="assets/prism.css"',
        '<main class="page-shell">': '<main class="article">',
        '<article class="article-layout">': '<article class="container">',
        '<figure class="hero">': '<figure class="article-hero">',
        '<h1 id="article-title">': '<h1 class="article-title" id="article-title">',
    }
    for source, target in replacements.items():
        text = text.replace(source, target)

    text = text.replace(
        '<a class="nav-cta active" href="../articles.html">Articles</a>',
        '<a class="nav-cta active" href="../articles.html">Blog</a>',
    )
    text = text.replace(
        '<a href="../articles.html" class="nav-cta active">Articles</a>',
        '<a href="../articles.html" class="nav-cta active">Blog</a>',
    )
    text = text.replace(
        '<a class="nav-cta active" href="./articles.html">Articles</a>',
        '<a class="nav-cta active" href="./articles.html">Blog</a>',
    )
    text = text.replace(
        '<a href="./articles.html" class="nav-cta active">Articles</a>',
        '<a href="./articles.html" class="nav-cta active">Blog</a>',
    )
    text = text.replace(
        '<li><a href="../articles.html">Articles</a></li>',
        '<li><a href="../articles.html">Blog</a></li>',
    )
    text = text.replace(
        '<li><a href="./articles.html">Articles</a></li>',
        '<li><a href="./articles.html">Blog</a></li>',
    )

    text = ensure_stylesheet(text, "../styles.css")
    text = ensure_body_class(text, "article-page")

    if '<nav class="nav">' not in text:
        text = text.replace("<main", article_header("..") + "<main", 1)

    if 'class="article-footer"' not in text:
        text = text.replace("</article>", build_article_footer(text) + "</article>", 1)

    if '<div class="footer-inner">' not in text:
        text = text.replace("</body>", site_footer("..") + "\n</body>", 1)

    return apply_verified_date(path, text)


def format_count(count: int) -> str:
    return f"{count} article" if count == 1 else f"{count} articles"


def article_card(article: ArticleMeta, href: str, featured: bool = False) -> str:
    card_class = "article-card article-card-featured" if featured else "article-card"
    media_class = "article-card-media article-card-media-featured" if featured else "article-card-media"
    body_class = "article-card-body article-card-body-featured" if featured else "article-card-body"
    title_class = "article-card-title article-card-title-featured" if featured else "article-card-title"
    return f"""<article class="{card_class}">
  <a href="{href}" class="{media_class}">
    <img src="{article.image}" alt="{article.title} hero image"/>
  </a>
  <div class="{body_class}">
    <div class="article-card-meta">
      <time datetime="{article.published_iso}">{article.published_display}</time>
      <span>•</span>
      <span>{article.read_time}</span>
    </div>
    <h2 class="{title_class}">
      <a href="{href}">{article.title}</a>
    </h2>
    <p class="article-card-description">{article.description}</p>
    <a href="{href}" class="article-card-link">Read article</a>
  </div>
</article>"""


def render_article_index(articles: list[ArticleMeta], *, depth: int, canonical: str) -> str:
    prefix = ".." if depth == 1 else "."
    css_prefix = "../articles" if depth == 1 else "articles"
    home_prefix = ".." if depth == 1 else "."
    favicon_href = "../img/favicon-32x32.png" if depth == 1 else "img/favicon-32x32.png"
    styles_href = "../styles.css" if depth == 1 else "styles.css"
    article_css_href = f"{css_prefix}/assets/style.css"
    featured = articles[0]
    rest = articles[1:]
    href_for = lambda article: article.pages_href if depth == 1 else article.root_href
    featured_markup = article_card(featured, href_for(featured), featured=True)
    cards_markup = "\n".join(article_card(article, href_for(article)) for article in rest)
    pages_url = canonical

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Articles | {SITE_NAME}</title>
  <meta name="description" content="Technical articles on Android, architecture, performance, testing, security, and product engineering."/>
  <meta name="author" content="{SITE_NAME}"/>
  <link rel="canonical" href="{pages_url}"/>
  <meta property="og:type" content="website"/>
  <meta property="og:title" content="Articles | {SITE_NAME}"/>
  <meta property="og:description" content="Technical articles on Android, architecture, performance, testing, security, and product engineering."/>
  <meta property="og:url" content="{pages_url}"/>
  <meta property="og:image" content="{featured.image}"/>
  <meta property="og:site_name" content="{SITE_TITLE}"/>
  <link rel="icon" type="image/png" sizes="32x32" href="{favicon_href}"/>
  <link rel="stylesheet" href="{styles_href}"/>
  <link rel="stylesheet" href="{article_css_href}"/>
</head>
<body class="article-hub">
{article_header(home_prefix)}
<main class="article-index-main">
  <section class="article-index-hero">
    <div class="article-index-shell">
      <p class="article-index-eyebrow">Engineering writing</p>
      <h1 class="article-index-title">Articles on Android, architecture, delivery, and the work behind reliable software.</h1>
      <p class="article-index-intro">A curated archive of hands-on engineering notes covering Compose, Gradle, testing, security, Wear OS, and shipping production systems.</p>
      <div class="article-index-stats">
        <span>{format_count(len(articles))}</span>
      </div>
    </div>
  </section>

  <section class="article-index-shell article-index-featured">
    <div class="article-section-heading">
      <h2>Featured article</h2>
    </div>
    {featured_markup}
  </section>

  <section class="article-index-shell article-index-listing">
    <div class="article-section-heading">
      <h2>All articles</h2>
    </div>
    <div class="article-card-grid">
      {cards_markup}
    </div>
  </section>
</main>
{site_footer(home_prefix)}
</body>
</html>
"""


def sync_articles() -> dict[str, int]:
    files = article_files()
    modified = 0

    for path in files:
        original = path.read_text(encoding="utf-8")
        updated = normalize_article_markup(path, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            modified += 1

    metas = sort_articles(read_article_meta(path) for path in files)
    articles_html = render_article_index(metas, depth=0, canonical=f"{SITE_URL}/articles.html")
    (ROOT / "articles.html").write_text(articles_html, encoding="utf-8")

    blog_html = render_article_index(metas, depth=1, canonical=f"{SITE_URL}/articles.html")
    (ROOT / "pages" / "blog.html").write_text(blog_html, encoding="utf-8")

    return {
        "article_files": len(files),
        "article_files_modified": modified,
        "index_pages_written": 2,
    }


if __name__ == "__main__":
    report = sync_articles()
    for key, value in report.items():
        print(f"{key}: {value}")
