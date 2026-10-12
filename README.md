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

## Project order

`data/projects.json` groups work into apps and platforms, client websites, own projects and public code. Array order determines the display order within each section, following the confirmed project chronology. Dates are not displayed. The optional `engagement` field distinguishes client work from full-time or mixed roles.

## Book PDF analytics

The book page uses the existing consent-gated GA4 property. After consent, its PDF links send `book_pdf_download` for the download button and `book_pdf_open` for links that open the PDF. All five PDF links are covered. These events count clicks, not completed downloads or unique readers; declined consent, blocked analytics and direct PDF visits are not counted.

After publishing, verify the events in GA4 Realtime, then use their Event count in the Events report. The `link_location` parameter identifies the header, hero download/open button, excerpt or footer; register it as an event-scoped custom dimension if you want that breakdown in reports. GA4 may also record its automatic `file_download` event; use the custom book events alone for these totals rather than adding both together.
