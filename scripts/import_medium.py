#!/usr/bin/env python3
"""Stage missing Medium posts for review; never publish or overwrite existing posts."""
import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape, unescape
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from blog_maintenance import ROOT, fetch, post_id, clean_url

FEED = 'https://medium.com/feed/@jamescullimore'
CONTENT = '{http://purl.org/rss/1.0/modules/content/}encoded'

class Content(HTMLParser):
    """Preserve article prose/code while excluding executable or tracking markup."""
    allowed = set('p h2 h3 h4 h5 h6 ul ol li blockquote pre code strong em b i a figure figcaption img hr br table thead tbody tr th td sup sub del'.split())
    void = {'img', 'hr', 'br'}
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.output = []; self.text = []; self.images = []; self.issues = []; self.skip = 0
        self.feed(raw)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style', 'iframe', 'object'):
            if tag in ('iframe', 'object') or (tag == 'script' and attrs.get('src')): self.issues.append('Embedded content needs manual restoration')
            self.skip += 1; return
        if self.skip: return
        tag = 'h2' if tag == 'h1' else tag
        if tag not in self.allowed: return
        safe = {}
        for key in ('href', 'src', 'alt', 'title', 'colspan', 'rowspan'):
            if key not in attrs: continue
            value = attrs[key]
            if value is None: continue
            if key in ('src', 'href'):
                if not value or any(ord(c) < 32 for c in value): continue
                if urlsplit(value).scheme not in ('http', 'https') and not value.startswith('#'): continue
            safe[key] = value
        if tag == 'img':
            url = safe.get('src', '')
            if not url or 'medium.com/_/stat' in url or attrs.get('width') == '1': return
            safe['alt'] = safe.get('alt', ''); safe['loading'] = 'lazy'; self.images.append(url)
        self.output.append('<' + tag + ''.join(f' {k}="{escape(v, quote=True)}"' for k,v in safe.items()) + '>')
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.void: self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'iframe', 'object'):
            self.skip = max(0, self.skip - 1); return
        if self.skip: return
        tag = 'h2' if tag == 'h1' else tag
        if tag in self.allowed and tag not in self.void: self.output.append(f'</{tag}>')
    def handle_data(self, data):
        if not self.skip:
            self.output.append(escape(data)); self.text.append(data)

def normal_title(title):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', title).lower())

def known_posts(root, articles):
    ids = {post_id(a.get('source_url', '')) for a in articles}
    # Older imports did not store source_url. Their published originals often appear in their HTML.
    for article in articles:
        path = root / article['url'].lstrip('/')
        if path.exists():
            for url in re.findall(r'https?://[^"<>\s]+', path.read_text()):
                if article['url'].rsplit('/',1)[-1][:-5] in url:
                    ids.add(post_id(unescape(url)))
    return ids - {None}

def render(article, body, iso, minutes):
    title = escape(article['title']); desc = escape(article['excerpt'], quote=True)
    canonical = 'https://jamescullimore.dev' + article['url']
    schema = {'@context':'https://schema.org','@type':'BlogPosting','headline':article['title'],'description':article['excerpt'],'datePublished':iso,'image':[article['image']],'author':{'@type':'Person','name':'James Cullimore'},'url':canonical,'mainEntityOfPage':canonical,'inLanguage':'en'}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><meta name="author" content="James Cullimore">
<link rel="canonical" href="{canonical}"><meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{escape(article['image'], quote=True)}"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/articles/assets/style.css"><link rel="stylesheet" href="/articles/assets/generated-article.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')}</script>
</head><body class="article-page"><header class="site-header"><nav class="site-nav"><a href="/blog.html">James Cullimore · Blog</a></nav></header>
<main id="main" class="article"><article class="container"><header class="article-header"><p class="article-category">{escape(' | '.join(article['tags']))}</p><h1 class="article-title">{title}</h1><div class="article-meta">By James Cullimore · <time datetime="{iso}">{article['date'].split(' • ')[0]}</time> · {minutes} min read</div></header><section class="article-content">{body}</section><p><a href="{escape(article['source_url'], quote=True)}">Read the original on Medium</a></p></article></main><footer class="site-footer"><a href="/blog.html">All articles</a></footer></body></html>
'''

def stage(root, xml, output):
    articles = json.loads((root / 'data/articles.json').read_text())
    ids = known_posts(root, articles)
    urls = {a['url'] for a in articles}; titles = {normal_title(a['title']) for a in articles}
    items = ET.fromstring(xml).findall('./channel/item')
    if not items: raise ValueError('Feed contains no items; check the feed response')
    candidates = []; skipped = []; seen = set()
    for item in items:
        title = item.findtext('title', '').strip()
        source = clean_url(item.findtext('link', ''))
        if urlsplit(source).hostname not in ('medium.com','jamescullimore.medium.com','levelup.gitconnected.com'):
            raise ValueError(f'Unexpected article host: {source}')
        identifier = post_id(source)
        slug = re.sub(r'-[a-f0-9]{12}$', '', urlsplit(source).path.rsplit('/',1)[-1])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or not identifier or not title:
            raise ValueError(f'Article needs a valid title, slug and post ID: {source}')
        route = '/articles/' + slug + '.html'
        if identifier in ids or route in urls or normal_title(title) in titles:
            skipped.append(source); continue
        if identifier in seen: continue
        seen.add(identifier)
        raw = item.findtext(CONTENT, '')
        if not raw: raise ValueError(f'Missing article body: {title}')
        parsed = Content(raw)
        plain = ' '.join(parsed.text)
        words = plain.split()
        issues = list(dict.fromkeys(parsed.issues))
        embeds = re.findall(r'https://medium.com/media/[^"<>\s]+', raw)
        if embeds: issues.append('Restore and verify code embeds: ' + ', '.join(dict.fromkeys(embeds)))
        if len(words) < 150: issues.append('Feed content may be truncated; compare with the published post')
        if not parsed.images: issues.append('Select and verify a hero image')
        date = parsedate_to_datetime(item.findtext('pubDate', ''))
        minutes = max(1, math.ceil(len(words)/200))
        paragraphs = re.findall(r'<p>(.*?)</p>', ''.join(parsed.output), re.S)
        excerpt = unescape(re.sub('<[^>]+>', '', paragraphs[0])) if paragraphs else plain
        excerpt = ' '.join(excerpt.split())
        if len(excerpt)>240: excerpt=excerpt[:240].rsplit(' ',1)[0]+'…'
        article = {'url':route,'image':parsed.images[0] if parsed.images else '/assets/branding/social-preview.png','date':f'{date:%b} {date.day}, {date.year} • {minutes} min read','title':title,'excerpt':excerpt,'tags':[c.text for c in item.findall('category') if c.text][:3] or ['Android'],'source_url':source,'featured_in':[]}
        candidates.append({'article':article,'published_at':date.isoformat(),'file':slug+'.html','reviewed':False,'issues':issues,'html':render(article, ''.join(parsed.output), date.date().isoformat(), minutes)})
    # Never overwrite an earlier review, even when there are no new candidates.
    if output.exists() and any(output.iterdir()): raise ValueError('Output folder is not empty; choose a fresh --output to preserve previous reviews')
    output.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        (output/candidate['file']).write_text(candidate.pop('html'))
    manifest = {'checked_at':datetime.now(timezone.utc).isoformat(),'feed_items':len(items),'already_present':len(skipped),'note':'RSS includes only recent posts. Review prose, metadata, images, tags and code against Medium. Reading times are local estimates. Restore missing embeds, clear resolved issues and set reviewed=true before applying. No website files have changed.','candidates':candidates}
    (output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(f'{len(candidates)} missing posts staged; {len(skipped)} already present. Review {output / "manifest.json"}')
    return manifest

def apply(root, output):
    manifest = json.loads((output/'manifest.json').read_text())
    articles = json.loads((root/'data/articles.json').read_text())
    existing_urls = {a['url'] for a in articles}; existing_ids = known_posts(root, articles)
    pending = []; seen = set()
    for item in manifest['candidates']:
        a = item['article']; url = a['url']; identifier = post_id(a['source_url'])
        if url in existing_urls or identifier in existing_ids: continue
        if not item.get('reviewed') or item.get('issues'): raise ValueError(f'Post still needs review: {a["title"]}')
        if not re.fullmatch(r'/articles/[a-z0-9-]+\.html',url) or not identifier: raise ValueError('Invalid article URL or source ID')
        if url in seen: raise ValueError('Duplicate article destination in manifest')
        seen.add(url)
        target = root/url.lstrip('/'); source = (output/item['file']).resolve()
        if not source.is_relative_to(output.resolve()): raise ValueError('Staged file must remain inside output folder')
        if target.exists(): raise ValueError(f'Refusing to overwrite {target}')
        body = source.read_text()
        if a['url'] not in body: raise ValueError('Staged HTML and article metadata disagree; review canonical URL')
        pending.append((a,target,body))
    if pending:
        # Compare actual publication dates rather than relying on the feed's order.
        combined = [a for a,_,_ in pending]+articles
        def date_key(a):
            value=a['date'].split(' • ')[0]
            for fmt in ('%b %d, %Y','%B %d, %Y'):
                try:return datetime.strptime(value,fmt)
                except ValueError:pass
            raise ValueError(f'Unrecognised article date: {value}')
        combined.sort(key=date_key,reverse=True)
        for a,target,body in pending:
            target.parent.mkdir(parents=True,exist_ok=True); target.write_text(body)
        (root/'data/articles.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n')
    print(f'Applied {len(pending)} reviewed posts. Run scripts/build_site.py and scripts/check_site.py. Nothing was published.')
    return len(pending)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feed-file',type=Path,help='Use a saved RSS feed for offline checks')
    parser.add_argument('--output',type=Path,default=ROOT/'.jc/medium-imports'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    parser.add_argument('--apply',action='store_true',help='Apply reviewed candidates from --output; skips posts already imported')
    args=parser.parse_args()
    try:
        if args.apply: apply(ROOT,args.output)
        else:
            if args.feed_file:xml=args.feed_file.read_text()
            else:
                status,_,xml=fetch(FEED)
                if status!=200:raise ValueError(f'Medium feed returned HTTP {status}')
            stage(ROOT,xml,args.output)
    except (ValueError,OSError,ET.ParseError) as error:
        parser.exit(1,str(error)+'\n')

if __name__=='__main__':main()
