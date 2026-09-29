# James Cullimore website

Static website served directly from this repository. No frontend framework or deployment build is required.

## Editing

- `templates/home.html` and `templates/footer.html`: homepage and shared footer.
- `templates/security-training.html` and `android-security-training/training.css`: security workshop landing page.
- `data/`: project catalogue, article index, courses and organization metadata.
- `articles/`: authored article pages.
- `styles.css` and `assets/`: shared styles, scripts and images.
- Product folders contain their landing pages, product assets and privacy pages. StarJar lives at `starjar/index.html`, served at `/starjar/`.

Edit generated pages through their source templates or data, then rebuild:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

The build regenerates the homepage, project details, courses, blog pagination, legacy redirects and sitemap. It also synchronizes article and legal-page navigation. Other product landing pages are edited directly. Shared assets receive content-based version URLs to prevent stale CSS or JavaScript.

## Preview and validation

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://localhost:8765. Static checks validate local links, anchors, structured data and sitemap metadata.

Optional browser checks require Node 22+, the preview server, and an isolated Chromium browser running with `--remote-debugging-port=9223`:

```sh
node scripts/browser_check.cjs
```

`AUDIT_CDP_PORT` and `AUDIT_ORIGIN` can override the defaults. Screenshots go to `/tmp`.

Article code highlighting uses locally hosted Highlight.js 11.11.1 (`assets/vendor/highlight/`, BSD-3-Clause licence included). The enhancement preserves the authored code and leaves it readable without JavaScript.

## URLs and local notes

Canonical URLs use `https://jamescullimore.dev`. Legacy routes, including `/starjar.html`, retain static redirects with fallback links. StarJar privacy-policy URLs remain unchanged. Shared fonts and store badges stay in `assets/`.

Private handoffs, reviews, audits and drafts belong in the Git-ignored `.jc/` folder. Keep website templates, data and maintenance scripts with the site so it can be rebuilt. The build script does not commit, push or deploy changes.
