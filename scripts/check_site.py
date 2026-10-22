#!/usr/bin/env python3
"""Check public HTML, local links and sitemap entries without external dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__();self.language=None;self.alternates={};self.links=[];self.ids=[];self.h1=0;self.canonical=[];self.description=[];self.refresh=[];self.noindex=False;self.feed(text)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='html':self.language=d.get('lang')
        if tag=='link' and d.get('rel')=='alternate' and d.get('hreflang'):self.alternates[d['hreflang']]=d.get('href')
        if 'id' in d:self.ids.append(d['id'])
        if tag=='meta' and d.get('http-equiv','').lower()=='refresh':self.refresh.append(d.get('content',''))
        if tag=='meta' and d.get('name','').lower() in ['robots','googlebot'] and 'noindex' in d.get('content','').lower():self.noindex=True
        if tag=='h1':self.h1+=1
        if tag=='a' and d.get('href'):self.links.append(d['href'])
        if tag in ['img','script','iframe'] and d.get('src'):self.links.append(d['src'])
        if tag=='link' and d.get('rel')=='stylesheet':self.links.append(d['href'])
        if tag=='link' and d.get('rel')=='canonical':self.canonical.append(d['href'])
        if tag=='meta' and d.get('name')=='description':self.description.append(d.get('content',''))
def resolve(url,source):
    u=urlsplit(url)
    if u.scheme or u.netloc:return None,u.fragment
    p=(ROOT/u.path.lstrip('/') if u.path.startswith('/') else source.parent/unquote(u.path)).resolve() if u.path else source
    if p.is_dir():p=p/'index.html'
    if not p.exists() and not p.suffix and p.with_suffix('.html').exists():p=p.with_suffix('.html')
    return p,unquote(u.fragment)
files={p:p.read_text() for p in ROOT.rglob('*.html') if 'templates' not in p.relative_to(ROOT).parts and not any(part.startswith('.') for part in p.relative_to(ROOT).parts) and p.name!='medium-content.html'}
docs={p:Document(s) for p,s in files.items()}
errors=[]
for p,d in docs.items():
    if len(d.ids)!=len(set(d.ids)):errors.append(f'{p.relative_to(ROOT)}: duplicate IDs')
    for url in d.links:
        target,anchor=resolve(url,p)
        if target is None:continue
        if not target.is_file() or not target.stat().st_size:errors.append(f'{p.relative_to(ROOT)}: missing/empty {url}')
        elif anchor and target in docs and anchor not in docs[target].ids:errors.append(f'{p.relative_to(ROOT)}: missing anchor {url}')
    for schema in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',files[p],re.S):
        try:json.loads(schema)
        except ValueError:errors.append(f'{p.relative_to(ROOT)}: invalid JSON-LD')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//s:loc',ns)]
if len(urls)!=len(set(urls)):errors.append('Duplicate sitemap URLs')
for url in urls:
    path=urlsplit(url).path
    p,_=resolve(path,ROOT/'index.html');d=docs.get(p)
    if not d:errors.append(f'Sitemap: missing {url}');continue
    if d.refresh or d.noindex:errors.append(f'{path}: redirect/noindex page must not be in sitemap')
    if d.h1!=1:errors.append(f'{path}: expected one h1, got {d.h1}')
    if d.canonical!=[url]:errors.append(f'{path}: canonical mismatch {d.canonical}')
    if len(d.description)!=1 or not d.description[0]:errors.append(f'{path}: missing/duplicate description')
# Legacy aliases must lead directly to a substantive, canonical page.
for item in json.loads((ROOT/'data/redirects.json').read_text()):
    source=ROOT/item['path']; d=docs.get(source)
    destination,anchor=resolve(item['destination'],source)
    target=docs.get(destination)
    canonical='https://jamescullimore.dev'+item['destination'].split('#',1)[0]
    if not d or d.refresh!=['0;url='+item['destination']] or d.canonical!=[canonical]:
        errors.append(f'{item["path"]}: invalid redirect or canonical')
    if not target or target.refresh or target.noindex or target.canonical!=[canonical]:
        errors.append(f'{item["path"]}: redirect destination is not a canonical indexable page')
    if anchor and target and anchor not in target.ids:errors.append(f'{item["path"]}: missing redirect anchor')
    if 'https://jamescullimore.dev/'+item['path'] in urls:errors.append(f'{item["path"]}: redirect present in sitemap')
# Each translated service must point both ways, while keeping its own canonical.
for item in json.loads((ROOT/'data/services-de.json').read_text()):
    en='/services/'+item['slug']+'/'
    de='/de/leistungen/'+item['de_slug']+'/'
    expected={'en':'https://jamescullimore.dev'+en,'de':'https://jamescullimore.dev'+de,'x-default':'https://jamescullimore.dev'+en}
    for lang,path in [('en',en),('de',de)]:
        target,_=resolve(path,ROOT/'index.html');d=docs.get(target)
        if not d or d.language!=lang or d.alternates!=expected:
            errors.append(f'{path}: incorrect language or reciprocal alternates')
        if d and expected[lang] not in urls:errors.append(f'{path}: translated service missing from sitemap')
# Watch pages must expose the configured video in static HTML, with verified metadata.
for item in json.loads((ROOT/'data/videos.json').read_text()):
    path='/videos/'+item['slug']+'/'
    target,_=resolve(path,ROOT/'index.html');text=files.get(target,'')
    schemas=[json.loads(raw) for raw in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',text,re.S)]
    video=next((obj for obj in schemas if obj.get('@type')=='VideoObject'),{})
    embed='https://www.youtube-nocookie.com/embed/'+item['id']
    if video.get('embedUrl')!=embed or f'src="{embed}"' not in text or not video.get('uploadDate') or not video.get('thumbnailUrl'):
        errors.append(f'{path}: missing visible video or video metadata')
print(f'Checked {len(docs)} HTML files and {len(urls)} sitemap URLs.')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print('Local links, anchors, sitemap metadata and JSON-LD passed.')
