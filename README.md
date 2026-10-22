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

## Enquiry and app-store click analytics

The homepage, generated portfolio pages (excluding Elchem), and StarJar, Watchful
and Don't Go To Bed landing pages use `assets/conversion-analytics.js` with the
existing consent-gated GA4 property. `contact_click` records email/phone link
intent; `app_store_click` records known product store links with `app_id`,
`store`, `page_path` and `link_location`. Email addresses, phone numbers and
message contents are not included in these custom events. Support contacts
are also clicks; do not interpret all contact events as sales leads.

These are not completed enquiries or app installs. Declined/revoked consent
and blocked analytics are not counted. After publishing, verify events in GA4
Realtime and register the event parameters as custom dimensions for reporting.
Compare store clicks with actual acquisition figures in the store consoles.

With the preview server and isolated Chrome running, test mobile product pages,
keyboard navigation and conversion consent (analytics requests blocked) using:

```sh
node scripts/conversion_check.cjs
```

## Service pages and product previews

`data/services.json` supplies the three service pages under `/services/`.
The build renders their scope, relevant projects, FAQs and enquiry links through
the shared page shell, adds their canonical URLs to the sitemap and preserves
existing product policy URLs even when they have no modification date.
Homepage service links live in `templates/home.html`.

StarJar’s `chores-and-stars.webp` and `reward-store.webp` come from its existing
English Pixel 9 marketing captures (`screenshot1.png` and `screenshot3.png`).
Watchful’s `watchlist-preview.webp` comes from the iPhone 6.9-inch
`01-less-checking.png` in its September 2026 Apple Store Kit. These are compressed
720px-wide copies, with no changes to the depicted UI. Captions identify the
example content and platform; each image links to a larger view.

## Indexing and old addresses

`data/redirects.json` maps known former URLs to their current destinations.
The build writes immediate HTML redirects because this site uses static GitHub
Pages hosting. Redirect canonicals omit fragments, while contact links retain
`#contact` for visitors. Redirects are deliberately excluded from the sitemap;
Search Console may correctly report them as “Page with redirect”.

The old Wear OS handover article address redirects to the version used by the
blog and sitemap. Former `/pages/` navigation routes and the old Gradle article
link are also retained. Removed drafts without a corresponding replacement
remain 404s. `404.html` helps visitors navigate without redirecting unrelated
missing URLs to the homepage; GitHub Pages retains their 404 status.

The static checker verifies redirect targets, matching canonicals, valid anchors,
and that redirect/noindex pages do not enter the sitemap. To investigate Google’s
selected canonical for a specific URL, use its Search Console URL Inspection
report: HTTP checks alone cannot reveal Google’s indexing decision.

### App search content

StarJar, Watchful and Don’t Go To Bed have static, visible product FAQs and
`MobileApplication` JSON-LD in their landing pages. Keep schema descriptions,
platforms, download links and free-download offers consistent with visible copy.
No ratings or reviews are asserted: this markup alone does not meet Google’s
software-app rich-result requirements. FAQs are for visitors, without FAQ rich-result markup.

Pricing and released features were checked against the public App Store listings
on 22 October 2026 (IDs 6758762270, 6812295504 and 6812278045), StarJar’s Google
Play listing, and the existing product support pages. Watchful’s monthly credit
plans are described as iOS options; do not infer Android availability or ship
features from unreleased local app sources. Prices and plan availability remain
in the stores rather than hard-coded here.

Don’t Go To Bed’s hero artwork comes from
`DontGoToBed/composeApp/src/commonMain/composeResources/drawable/`.
Daddy uses the front frame of `papa_original_marketing_v1.png`: x=127, y=31,
width=302, height=498, matching `RefreshedCharacterArt.kt`. The website’s
`papa-marketing-front.webp` is a lossless extraction of that frame. Do not use
the standalone `papa_front.png` portrait: James corrected that choice on
22 October 2026. The obsolete website `papa-approved.webp` has been removed.
Leo’s 13 October refresh and Ian’s 4 October refresh remain lossless WebP
copies of their original `leo_front.png` and `ian_front.png`, preserving alpha.
