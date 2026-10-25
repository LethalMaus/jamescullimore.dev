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

Blog entries in `data/articles.json` may include `featured_in`, an array of
`name`, `url` and optional `edition` fields. Each URL must point to the edition
or page that links to that article. The builder renders these links as pills
on archive cards and article headers; `assets/blog.js` renders the same pills
in search results. An empty array means no feature is selected for display.
Keep feature research and unresolved leads in `.jc/blog-feature-audit.json`.
The displayed selection contains 37 mentions across 25 articles and eight
publications. Keep it focused on the selected developer and testing newsletters;
exclude aggregators, general reference links, Habr and AppTractor. The full
research record is retained separately. Counts in the credibility strip are
calculated from the displayed data.

`data/publications.json` records locally hosted publication icons and their
original sources. Other publications use typographic initials. Archive cards
show two badges with a native expandable list; article pages show all selected
badges.

The October 2026 audit checked all 66 articles; eight Kotlin Weekly editions
were unavailable, so the recorded features are not an exhaustive claim.

Run `node scripts/blog_features_check.cjs` with the preview server and Chrome
endpoint above to check feature links, search, topic filters, pagination,
responsive layouts, and the two latest imported posts. The imported posts
retain the published RSS text, with code restored from James's public gists;
their reading times are local estimates at 200 words per minute.

The blog's **Show → Featured articles** filter combines with text search and
topic filtering. `/blog/featured.html` is a static collection of all selected
featured articles, so homepage links and readers without JavaScript still
reach the collection. The homepage publication strip sits before the enquiry
section as supporting evidence; it does not replace the service offer or
client testimonials.

### Medium imports and link maintenance

Prepare missing recent posts without changing the site:

```sh
python3 scripts/import_medium.py
```

The command fetches the public Medium RSS feed, compares post IDs, permalinks
and titles against the catalogue, and creates a fresh review folder under
`.jc/medium-imports/`. RSS contains only recent posts, so run this after new
publications; it is not a complete historical archive sync. A saved feed can
be checked offline with `--feed-file /path/to/feed.xml`.

Review each staged HTML page and its `manifest.json` entry against Medium.
Check the full text, title, excerpt, tags, date, images and code examples.
The importer removes executable/tracking markup and flags embedded content
for manual restoration rather than silently publishing an incomplete post.
Restore and verify any missing code, clear resolved `issues`, and set
`reviewed` to `true`. Apply the reviewed folder explicitly:

```sh
python3 scripts/import_medium.py --apply --output .jc/medium-imports/REVIEW_FOLDER
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Applying skips already imported posts and refuses to overwrite existing files.
Neither preparation nor application commits, pushes or deploys anything.
Do not reuse a non-empty staging directory: this protects review edits.

Check feature links and stored original Medium URLs, or include every external
hyperlink in the indexed article pages:

```sh
python3 scripts/check_blog_links.py
python3 scripts/check_blog_links.py --include-article-links
```

Reports go to `.jc/blog-maintenance/link-report.json` and `.txt`. Failed
requests are retried once. HTTP 404/410 and recognised soft-404 pages are
reported separately from access restrictions, server errors and network
failures. Every result retains its referring articles. Review failures in a
browser before assuming a link is broken. Links and badges are never removed
or edited. Repeated missing-page responses for Kotlin Weekly, Android Weekly
and jetc.dev produce brief message drafts in the report; nothing is sent.
The eight previously unavailable, unselected Kotlin Weekly editions remain
in the historical research audit and are not added to the recurring check.

`.github/workflows/blog-maintenance.yml` prepares recent Medium imports and
checks all article/feature links monthly, on the first day at 08:23 UTC, or on
manual dispatch. It has read-only repository permission and saves reports and
staged posts in a 60-day Actions artifact. Review failures mark the run as
failed; notification delivery depends on your GitHub settings. The schedule
starts only after the workflow is on the default branch and Actions is enabled.
It never applies imports, publishes changes, or contacts newsletter authors.

Run `python3 scripts/test_blog_maintenance.py` for offline import and link-check
regressions. Browser coverage for the featured collection, combined filters,
and homepage strip is included in `node scripts/blog_features_check.cjs`.

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

### Website discovery and conversion routes

`/apps/` is the visitor-facing directory for the three released apps and Elchem, labelled in development. Its cards
lead to product landing pages; app project details do the same. Client project
pages link to services that cite them as relevant work. The shared footer and
homepage expose the directory without changing the product-page designs.

`data/article-services.json` contains deliberate article-to-service mappings.
The build adds one contextual recommendation after each selected article and
replaces it on subsequent builds. Keep these mappings relevant to the article;
do not automatically add sales messages to every post. The article body and
publication date remain authored content.

### German services and video pages

`data/services-de.json` contains the German versions of the three English
services. `data/project-summaries-de.json` supplies translated summaries of the
same project evidence. `/de/leistungen/` is the German services directory.
Each translated service has its own canonical URL and reciprocal `en`, `de`
and `x-default` links. The directory is not declared an alternate of the
English homepage because its scope differs. Navigation and consent controls
follow the page language; the saved consent choice is shared across languages.

`data/videos.json` generates `/videos/` and one watch page per public video.
Titles, channel identity and thumbnails were checked with YouTube oEmbed on
22 October 2026; publication timestamps were verified from the public watch
pages. The player is in static HTML, uses the privacy-enhanced YouTube domain,
and does not autoplay. VideoObject metadata uses the verified upload date and
thumbnail. Embedding does not guarantee video-search indexing.

For a new tutorial, add its public video ID, verified publication timestamp,
accurate title, summary, product route and useful written context to the
catalogue, then rebuild. Label tutorials separately from trailers. Do not
relabel old footage as current or publish local App Review recordings merely
because they exist. Keep tutorial summaries grounded in the actual recording;
chapters, transcripts and step-by-step instructions need a content review.

Run `python3 scripts/check_site.py` to validate language alternates, video
embeds and metadata alongside the existing site checks.

### Client decision guides

`data/guides.json` supplies metadata and service/project links for authored
content in `templates/guides/`. The builder generates each `/guides/<slug>/`
page with a canonical URL, Article metadata and sitemap entry. Relevant
services, case studies and the first blog archive page link back to the guide.

The modernisation guide uses the J&C Bachmann and Zuriga facts recorded in
`data/projects.json` and links to Android's official Compose migration guidance.
Keep project examples factual; do not imply measured savings or outcomes that
are not documented. Publication dates belong to the authored content.

The guide catalogue also supports explicit `path`, `lang` and reciprocal
`translation` fields. English/German modernisation guides link to each other
and to their corresponding service page. `check_site.py` validates their
language metadata and sitemap inclusion.

StarJar and Watchful have written `/getting-started/` walkthroughs. Their
instructions use the existing product/support documentation and current
website screenshots. Examples are labelled as examples, not screenshots of
that exact workflow. Keep Watchful's own-key and iOS credit options distinct.
When a tutorial is published, verify its content and add it to the video
catalogue before linking it from the corresponding walkthrough. Do not use
trailer metadata for a tutorial that does not yet exist.

### Blog and analytics checks

`node scripts/blog_check.cjs` checks every article in `data/articles.json` and
all six archive pages at 320, 390 and 1440 pixels, plus enlarged text. It requires
the local preview on port 8765 and an isolated Chrome CDP endpoint on 9223
(override with `AUDIT_ORIGIN` / `AUDIT_CDP_PORT`). It reports broken images,
page overflow, heading problems and uncontained code blocks to
`/tmp/blog-audit.json`. External image failures may need a network recheck.
Google Analytics hosts are blocked during these layout checks.

Authored articles now receive the same consent and conversion scripts as the
portfolio pages when built. The static checker guards against losing them.
`conversion_check.cjs` verifies store-click behaviour before consent, after
acceptance, after decline and after revocation. These events indicate clicks,
not completed installs or submitted enquiries. Browser tests alone do not
prove events reached a particular GA4 property: check its stream measurement
ID and confirm receipt in Realtime or DebugView.

For this site's current growth work, review Search Console weekly for indexing
issues and new queries. Use 28-day comparisons for content decisions once
there is enough history, and a monthly review after the site settles. Review
again after major changes or an alert. Consent-based Analytics will not count
all Search Console visits, and query totals may omit anonymised searches.

### Product-page performance and service evidence

StarJar uses compressed copies of the same approved artwork and WOFF2 versions
of the existing Nunito fonts. The Arial fallback uses matching ascent/descent
metrics to reduce movement while Nunito loads. Original assets remain available.
DGTB uses small display copies of the existing Leo/Ian artwork and icon; Daddy
still uses the exact approved front-frame extraction documented above.

The three released product pages use `assets/video-preview.js` and `.css` to
load YouTube players after activation. Their initial links work without
JavaScript; enhanced buttons support keyboard activation and focus the player.
The dedicated `/videos/` pages retain static embeds and VideoObject metadata.
Public YouTube thumbnails are stored under `assets/video-posters/`.

`data/service-evidence.json` selects a documented case study and an exact excerpt
from an existing published testimonial for each service. The builder validates
that excerpts match their source text. German pages translate the project
context but label testimonial excerpts as English originals. Do not convert a
quote about one company into evidence about a different engagement, or reuse
project-specific savings as promises for future work.

Run `node scripts/video_check.cjs` for activation, fallback and service layout
checks. `node scripts/performance_check.cjs` measures the three live released-app
pages at 390px, 150ms simulated latency, 1.6Mbps download and 4x CPU slowdown,
with cache disabled and Analytics hosts blocked. Override `AUDIT_ORIGIN` for a
local preview and `PERF_REPORT` for the output path. Results are laboratory
observations, not real-user Core Web Vitals. Resource Timing byte totals omit
cross-origin resources without timing permission and iframe subresources.
Compare live before/after measurements; local hosting uses different compression.

Account snapshots and review notes belong in ignored `reports/private/`, not in
the published site. Check indexing roughly a week after a change, then use a
28-day performance review once data is available. No automatic review schedule
is created by these scripts.
