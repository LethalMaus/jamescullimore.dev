#!/usr/bin/env python3
"""Report external link failures without modifying articles or sending messages."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from blog_maintenance import ROOT, fetch

class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.urls = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        url = dict(attrs).get('href', '')
        if tag == 'a' and url.startswith(('http://', 'https://')):
            self.urls.append(url)

def classify(status, body):
    title = re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I)
    title = re.sub('<[^>]+>', '', title.group(1)).strip() if title else ''
    if status in (404, 410): return 'missing'
    if status in (401, 403, 429): return 'access_limited'
    if status >= 500: return 'server_error'
    if not 200 <= status < 300: return 'http_error'
    if re.search(r'^(?:404|410)(?:\s|:|$)|\b(?:page not found|page could not be found)\b', title, re.I): return 'soft_404'
    return 'ok'

def check(url, timeout):
    try:
        status, destination, body = fetch(url, timeout)
        return {'url': url, 'status': status, 'destination': destination, 'result': classify(status, body)}
    except Exception as error:
        return {'url': url, 'status': None, 'result': 'network_error', 'error': str(error)}

def run(root, output, include_article_links=False, timeout=20):
    articles = json.loads((root / 'data/articles.json').read_text())
    targets = {}
    for article in articles:
        links = [(f['url'], f['name']) for f in article.get('featured_in', [])]
        if article.get('source_url'): links.append((article['source_url'], 'Medium'))
        if include_article_links:
            links += [(url, 'Article link') for url in Links((root / article['url'].lstrip('/')).read_text()).urls]
        for url, publisher in links:
            if urlsplit(url).hostname in ('jamescullimore.dev', 'www.jamescullimore.dev'): continue
            entry = {'article': article['url'], 'publisher': publisher}
            if entry not in targets.setdefault(url, []): targets[url].append(entry)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda url: check(url, timeout), targets))
    # Retry failures once, recording both attempts instead of treating blocking as a dead link.
    failures = [r for r in results if r['result'] != 'ok']
    with ThreadPoolExecutor(max_workers=4) as pool:
        retries = dict(zip((r['url'] for r in failures), pool.map(lambda r: check(r['url'], timeout), failures)))
    for result in results:
        result['references'] = targets[result['url']]
        if result['url'] in retries:
            retry = retries[result['url']]
            result['retry'] = retry
            if retry['result'] == 'ok': result['result'] = 'recovered'
    broken = [r for r in results if r['result'] in ('missing', 'soft_404') and r.get('retry', {}).get('result') in ('missing', 'soft_404')]
    publisher_urls = {}
    for result in broken:
        for reference in result['references']:
            if reference['publisher'] in ('Kotlin Weekly', 'Android Weekly', 'jetc.dev'):
                publisher_urls.setdefault(reference['publisher'], set()).add(result['url'])
    drafts = {name: 'Hey! I noticed these archive links are showing a page-not-found error:\n' + '\n'.join(sorted(urls)) + '\nHave they moved to different URLs?' for name, urls in publisher_urls.items()}
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'scope': 'features, original sources' + (', all article links' if include_article_links else ''), 'checked': len(results), 'needs_review': sum(r['result'] not in ('ok', 'recovered') for r in results), 'results': results, 'publisher_message_drafts': drafts, 'note': 'No badges or articles were changed. No messages were sent. Verify failures in a browser before contacting publishers; access limits and network failures are not proof of a dead link.'}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'link-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    lines = [f"Checked {report['checked']} URLs; {report['needs_review']} need review.", report['note'], '']
    lines += [f"{r['result']}: {r['url']}" for r in results if r['result'] not in ('ok', 'recovered')]
    for name, draft in drafts.items(): lines += ['', f'DRAFT FOR {name} — NOT SENT', draft]
    (output / 'link-report.txt').write_text('\n'.join(lines) + '\n')
    print(lines[0]); print(f'Report: {output / "link-report.json"}')
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.jc/blog-maintenance')
    parser.add_argument('--include-article-links', action='store_true', help='Also check every external hyperlink in all indexed articles')
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--fail-on-review', action='store_true', help='Return a non-zero exit code if any URLs need review')
    args = parser.parse_args()
    report = run(ROOT, args.output, args.include_article_links, args.timeout)
    return 1 if args.fail_on_review and report['needs_review'] else 0

if __name__ == '__main__': raise SystemExit(main())
