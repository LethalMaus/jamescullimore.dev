#!/usr/bin/env python3
"""Build the static portfolio pages. Run from any directory; no dependencies required."""
from pathlib import Path
import html, json, re, math, hashlib, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://jamescullimore.dev'
STYLE_VERSION = hashlib.sha256((ROOT / 'styles.css').read_bytes()).hexdigest()[:12]
esc = html.escape
load = lambda name: json.loads((ROOT / 'data' / name).read_text())
projects = load('projects.json')
articles = load('articles.json')
resources = load('resources.json')

def header(active=''):
    links = [('/#services','Services'),('/#how-we-work','Process'),('/projects.html','Work'),('/#insights','Testimonials'),('/blog.html','Blog'),('/#contact','Discuss your project')]
    items = ''.join(f'<li><a href="{url}"'+(' aria-current="page"' if active==label else '')+(' class="contact-link project-cta"' if label=='Discuss your project' else '')+f'>{esc(label)}</a></li>' for url,label in links)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><nav class="site-nav" aria-label="Primary">
<a class="site-brand" href="/" aria-label="James Cullimore Software Engineering home"><img src="/assets/branding/logo-black.png" width="56" height="56" alt=""><span><strong>James Cullimore</strong><small>Software Engineering</small></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-links">Menu +</button><ul class="site-links" id="site-links">{items}</ul>
</nav></header>'''

def footer():
    return (ROOT/'templates/footer.html').read_text().strip()

def page(title,description,path,content,active='',schema=None,scripts='',image='/assets/branding/social-preview.png'):
    url=BASE+path
    body_class = 'home-page' if path == '/' else 'portfolio-page'
    extra_styles = '' if path == '/' else '<link rel="stylesheet" href="/assets/portfolio-pages.css">'
    schema=schema or {'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'url':url}
    image=image if image.startswith('https:') else BASE+image
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | James Cullimore</title><meta name="description" content="{esc(description,quote=True)}"><meta name="author" content="James Cullimore"><meta name="theme-color" content="#fcfcf9">
<link rel="canonical" href="{esc(url)}"><link rel="icon" href="/img/favicon.ico"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title,quote=True)}"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="James Cullimore Software Engineering"><meta property="og:image" content="{esc(image)}"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/styles.css?v={STYLE_VERSION}">{extra_styles}<script defer src="/assets/site.js"></script><script defer src="/assets/analytics-consent.js"></script>{scripts}
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('</','<\\/')}</script>
</head><body class="{body_class}">{header(active)}<main id="main">{content}</main>{footer()}</body></html>'''

def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text+'\n')

def project_card(p):
    pic=f'<img class="project-icon" src="{p["image"]}" alt="" width="64" height="64" loading="lazy">' if p.get('image') else ''
    return f'''<article class="project-card">{pic}<span class="eyebrow">{esc(p['kind'])}</span><h3><a href="/projects/{p['slug']}.html">{esc(p['name'])}</a></h3><p>{esc(p['summary'])}</p><div class="card-bottom"><span>{esc(' · '.join(p['focus']))}</span><span class="card-arrow" aria-hidden="true">↗</span></div></article>'''

def excerpt(text,length=155):
    return text if len(text)<=length else text[:length].rsplit(' ',1)[0].rstrip('.,;:')+'…'

def blog_card(a):
    tags=''.join(f'<span class="blog-tag">{esc(t)}</span>' for t in a['tags'][:3])
    return f'''<article class="blog-card"><a class="blog-card-media" href="{esc(a['url'])}" tabindex="-1" aria-hidden="true"><img src="{esc(a['image'])}" alt="" loading="lazy" width="640" height="360"></a><div class="blog-date">{esc(a['date'])}</div><h2 class="blog-title"><a href="{esc(a['url'])}">{esc(a['title'])}</a></h2><p class="blog-excerpt">{esc(excerpt(a['excerpt']))}</p><div class="blog-tags">{tags}</div></article>'''

def playlist_link():
    return f'<a class="text-link" href="{esc(resources["youtube_playlist"])}">Watch more talks</a>' if resources.get('youtube_playlist') else '<a class="text-link" href="/courses.html">More talks &amp; courses ↗</a>'

home=(ROOT/'templates/home.html').read_text()
home=home.replace('{{playlist_link}}',playlist_link())
own_slugs = ['dont-go-to-bed', 'starjar', 'watchful', 'elchem']
own_cards = []
for slug in own_slugs:
    p = next(p for p in projects if p['slug'] == slug)
    own_cards.append(f'<article class="work-card"><img class="own-product-icon" src="{esc(p["image"])}" alt="" width="56" height="56" loading="lazy"><h3 class="work-title"><a href="/projects/{p["slug"]}.html">{esc(p["name"])}</a></h3><p class="work-text">{esc(p["summary"])}</p></article>')
home=home.replace('{{own_projects}}', ''.join(own_cards))
write('index.html',page('Android, IoT & Kotlin Multiplatform Engineering','Senior Android, IoT and Kotlin Multiplatform engineering. Build mobile products, modernize existing apps, and improve testing with James Cullimore.','/',home,schema=load('organization.json')))

intro='<section class="page-intro"><div class="section-inner"><span class="eyebrow">The project catalogue</span><h1>Work, in a little more detail.</h1><p class="lead">Client collaborations, independent products and public engineering examples. Explore the context, the contribution and the product behind each project.</p><nav class="project-tabs" aria-label="Project categories"><a href="#client-work">Client work</a><a href="#own-projects">Own projects</a><a href="#public-code">GitHub projects</a></nav></div></section>'
groups=''
for kind,anchor,heading in [('Client work','client-work','Client collaborations'),('Own projects','own-projects','Apps, games & developer tools'),('Public code','public-code','GitHub examples & experiments')]:
    groups+=f'<section class="project-group" id="{anchor}"><span class="eyebrow">{kind}</span><h2>{heading}</h2><div class="project-grid">'+''.join(project_card(p) for p in projects if p['kind']==kind)+'</div></section>'
content=intro+'<div class="section"><div class="section-inner">'+groups+'<div class="section-actions"><a class="text-link" href="https://github.com/LethalMaus?tab=repositories">More projects on GitHub</a></div></div></div>'
schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Projects by James Cullimore','url':BASE+'/projects.html','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+'/projects/'+p['slug']+'.html','name':p['name']} for i,p in enumerate(projects)]}}
write('projects.html',page('Projects — Client Work, Apps & Games','Explore client engineering work, StarJar, Don’t Go To Bed, Android Security Training, Elchem and Watchful. Project details, product sites and app links.','/projects.html',content,'Work',schema))

# The training landing page shares the company shell and has its own scoped layout.
training = (ROOT/'templates/security-training.html').read_text()
write('android-security-training/index.html', page('Android Security Training & Workshops', 'Hands-on Android security workshops led by James Cullimore. Explore four practical modules, vulnerable and secure app labs, and tailored team training.', '/android-security-training/', training, scripts='<link rel="stylesheet" href="/android-security-training/training.css">'))

testimonials=load('testimonials.json') if (ROOT/'data/testimonials.json').exists() else json.loads((ROOT/'testimonials.json').read_text())
testimonial_names={'jc-bachmann':'J&C Bachmann','benefits-me':'Benefits.me','lexoffice':'Lexoffice','marktgalerie':'Marktmeister Pro','neurofly':'Neurofly','farmerjoe':'farmerJoe'}
for p in projects:
    path='/projects/'+p['slug']+'.html'
    tags=''.join(f'<span>{esc(t)}</span>' for t in p['focus'])
    image=f'<img src="{p["image"]}" alt="{esc(p["name"])}" loading="lazy">' if p.get('image') else ''
    links=''.join(f'<a href="{esc(link["url"])}">{esc(link["label"])} <span aria-hidden="true">↗</span></a>' for link in p['links'])
    quote=''
    t=next((t for t in testimonials if t['company']==testimonial_names.get(p['slug'])),None)
    if t:
        quote=f'<section><h2>From the client</h2><blockquote><p>“{esc(t["text"])}”</p><cite>{esc(t["author"])}, {esc(t["company"])}</cite></blockquote></section>'
    outcome = f'<section><h2>The result</h2><p>{esc(p["outcome"])}</p></section>' if p.get('outcome') else ''
    content=f'''<section class="page-intro"><div class="section-inner"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/projects.html">Projects</a> / {esc(p['name'])}</nav><span class="eyebrow">{p['kind']}</span><h1>{esc(p['name'])}</h1><p class="lead">{esc(p['summary'])}</p><div class="detail-tags">{tags}</div><a class="text-link" href="#project-links">Project links <span aria-hidden="true">↓</span></a></div></section>
<section class="section"><div class="section-inner detail-layout"><div class="detail-content"><section><h2>{"The brief" if p.get("outcome") else "The project"}</h2><p>{esc(p['context'])}</p></section><section><h2>{'Inside the product' if p['kind']=='Own projects' else 'What it demonstrates' if p['kind']=='Public code' else 'What we delivered' if p.get('outcome') else 'The contribution'}</h2><ul>{''.join('<li>'+esc(w)+'</li>' for w in p['work'])}</ul></section>{outcome}{quote}<section><h2>Working on something similar?</h2><p>Tell us about your product, your team and the support you need.</p><a class="button" href="/#contact">Discuss your project ↗</a></section></div><aside class="detail-aside" id="project-links">{image}<h2>Explore the project</h2>{links}<hr><a href="/projects.html">← All projects</a></aside></div></section>'''
    schema={'@context':'https://schema.org','@type':'WebPage','name':p['name']+' — project details','description':p['summary'],'url':BASE+path,'breadcrumb':{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Projects','item':BASE+'/projects.html'},{'@type':'ListItem','position':3,'name':p['name'],'item':BASE+path}]}}
    write(path.lstrip('/'),page(p['name']+' — Project Details',p['summary'],path,content,'Work',schema,image=p['image'] if p.get('image') and not p['image'].endswith('.svg') else '/assets/branding/social-preview.png'))

courses=''.join(f'<article class="service"><span class="eyebrow">{esc(c["platform"])}</span><h3>{esc(c["title"])}</h3><p>{esc(c["description"])}</p><a class="text-link" href="{esc(c["url"])}">View course ↗</a></article>' for c in resources['courses'])
content=f'''<section class="page-intro"><div class="section-inner"><span class="eyebrow">Learn from practical experience</span><h1>Courses, talks &amp; workshops</h1><p class="lead">Explore conference videos, learn with droidcon Academy, or bring a focused Android workshop to your team.</p></div></section><section class="section"><div class="section-inner community-grid"><div><h2>Watch a talk</h2><p class="lead">Engineering ideas, lessons from delivery, and the decisions behind better Android apps.</p></div><div><div class="video-frame"><iframe src="https://www.youtube-nocookie.com/embed/MXHt0_2iKgA" title="James Cullimore conference talk" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>{playlist_link()}</div></div></section><section class="section soft"><div class="section-inner"><div class="section-heading-row"><h2>Learn at your own pace</h2><a class="text-link" href="{esc(resources['academy_profile'])}">My droidcon Academy profile ↗</a></div><div class="course-grid">{courses}<article class="service"><span class="eyebrow">Team workshop</span><h3>Android Security Training</h3><p>Hands-on labs with vulnerable and secure app variants. Inspect, fix and verify Android security issues.</p><a class="text-link" href="/android-security-training/">Explore the syllabus ↗</a></article><article class="service"><span class="eyebrow">Free book</span><h3>5 Minute Bedtime Stories for Android Devs</h3><p>Short stories about production surprises, developer folklore and the decisions every mobile team recognises.</p><a class="text-link" href="/5-minute-bedtime-stories-for-android-devs.html">Read the book ↗</a></article></div></div></section>'''
write('courses.html',page('Android Courses, Talks & Workshops','Watch James Cullimore’s conference videos, explore droidcon Academy courses and book practical Android security training for your team.','/courses.html',content,'Courses'))

page_count=math.ceil(len(articles)/12)
def blog_path(n): return '/blog.html' if n==1 else f'/blog/page-{n}.html'
for n in range(1,page_count+1):
    path=blog_path(n)
    pagination='<nav class="pagination" aria-label="Blog pages">'+''.join(f'<a href="{blog_path(i)}"'+(' aria-current="page"' if i==n else '')+f' aria-label="Page {i}">{i}</a>' for i in range(1,page_count+1))+'</nav>'
    if n<page_count: pagination=pagination.replace('</nav>',f'<a href="{blog_path(n+1)}" rel="next">Next →</a></nav>')
    content=f'''<section class="page-intro"><div class="section-inner"><span class="eyebrow">The engineering notebook</span><h1>Notes from the work.</h1><p class="lead">Android development, architecture, performance, security and the experience of building software.</p><form class="blog-tools" role="search" hidden><label>Search articles<input id="blog-search" type="search" placeholder="Try Kotlin, testing or security…" autocomplete="off"></label><label>Topic<select id="blog-topic"><option value="">All topics</option><option>Security</option><option>Testing</option><option>Performance</option><option>Architecture</option><option>Compose</option><option>IoT &amp; Wear OS</option><option>Developer life</option></select></label></form><p class="blog-status" id="blog-status" role="status">{len(articles)} articles · Page {n} of {page_count}</p></div></section><section class="section"><div class="section-inner"><div class="blog-grid" id="blog-grid">{''.join(blog_card(a) for a in articles[(n-1)*12:n*12])}</div>{pagination}<button class="button secondary" id="more-results" type="button" hidden>Show more results</button></div></section>'''
    schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Engineering articles'+(f' — page {n}' if n>1 else ''),'url':BASE+path,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+a['url'],'name':a['title']} for i,a in enumerate(articles[(n-1)*12:n*12])]}}
    write(path.lstrip('/'),page('Android Engineering Blog'+(f' — Page {n}' if n>1 else ''),'Practical articles on Android, Kotlin, testing, security, architecture and software delivery.'+(f' Browse page {n} of the archive.' if n>1 else ''),path,content,'Blog',schema,scripts='<script defer src="/assets/blog.js"></script>'))

def redirect(path,dest,title):
    write(path,f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><link rel="canonical" href="{BASE+dest}"><meta http-equiv="refresh" content="0;url={dest}"></head><body><p><a href="{dest}">{esc(title)}</a></p></body></html>')
redirect('starjar.html','/starjar/','Continue to StarJar')
redirect('talks.html','/courses.html','Courses, talks & workshops')
redirect('articles.html','/blog.html','Continue to the blog')
redirect('contact.html','/#contact','Contact James Cullimore')
redirect('team.html','/','James Cullimore Software Engineering')

# Keep authored articles and legal text, while synchronizing the shared navigation.
for f in [*(ROOT/'articles').glob('*.html'),ROOT/'impressum.html',ROOT/'datenschutz.html']:
    s=f.read_text()
    if '<nav class="nav">' not in s and 'class="site-nav"' not in s: continue
    s=re.sub(r'<a class="skip-link" href="#main">Skip to content</a>\s*','',s)
    s=re.sub(r'<header(?: class="site-header")?>.*?</header>',header('Blog' if f.parent.name=='articles' else ''),s,count=1,flags=re.S)
    s=re.sub(r'<footer(?: class="site-footer")?>.*?</footer>',footer(),s,flags=re.S)
    if 'id="main"' not in s: s=re.sub(r'<main\b', '<main id="main"',s,count=1)
    if '/assets/site.js' not in s: s=s.replace('</head>','<script defer src="/assets/site.js"></script>\n</head>')
    if f.name in ['impressum.html','datenschutz.html']:
        if 'rel="canonical"' not in s: s=s.replace('</head>',f'<link rel="canonical" href="{BASE}/{f.name}">\n</head>')
        if 'name="description"' not in s:
            desc='Anbieterkennzeichnung und Kontaktinformationen von James Cullimore Software Engineering.' if f.name=='impressum.html' else 'Informationen zum Datenschutz auf der Website von James Cullimore Software Engineering.'
            s=s.replace('</head>',f'<meta name="description" content="{desc}">\n</head>')
    s=s.replace('../pages/impressum.html','/impressum.html').replace('../pages/datenschutz.html','/datenschutz.html').replace('../articles.html','/blog.html')
    s=s.replace('href="/how-i-cut-my-gradle-build-time-by-50-8f3c57534ce6"','href="/articles/how-i-cut-my-gradle-build-time-by-50.html"')
    if f.parent.name == 'articles' and '<pre' in s:
        if '/assets/code-highlight.js' not in s:
            s=s.replace('</head>', '<link rel="stylesheet" href="/assets/code-highlight.css"><script defer src="/assets/vendor/highlight/highlight.min.js"></script><script defer src="/assets/vendor/highlight/kotlin.min.js"></script><script defer src="/assets/vendor/highlight/groovy.min.js"></script><script defer src="/assets/code-highlight.js"></script>\n</head>')
    f.write_text(s)

# List canonical, substantive pages only, retaining known publication/modification dates.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
old=ET.parse(ROOT/'sitemap.xml')
dates={u.find('s:loc',ns).text:u.find('s:lastmod',ns).text for u in old.findall('s:url',ns) if u.find('s:lastmod',ns) is not None}
urls=[BASE+'/',BASE+'/projects.html',BASE+'/courses.html',*[BASE+blog_path(n) for n in range(1,page_count+1)],BASE+'/impressum.html',BASE+'/datenschutz.html',*[BASE+'/projects/'+p['slug']+'.html' for p in projects],*[BASE+a['url'] for a in articles],BASE+'/starjar/',BASE+'/elchem/',BASE+'/android-security-training/',BASE+'/5-minute-bedtime-stories-for-android-devs.html']
urls += [url for url in dates if '/watchful/' in url or '/dontgotobed/' in url]
ET.register_namespace('',ns['s']);tree=ET.Element('{'+ns['s']+'}urlset')
for url in dict.fromkeys(urls):
    node=ET.SubElement(tree,'url');ET.SubElement(node,'loc').text=url
    # Existing article dates reflect content updates, not template-only changes.
    date=dates.get(url) if '/articles/' in url or '/watchful/' in url or '/dontgotobed/' in url else '2026-09-28'
    if date: ET.SubElement(node,'lastmod').text=date
ET.indent(tree,space='  ')
ET.ElementTree(tree).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print(f'Built homepage, {len(projects)} project details, courses, {page_count} blog pages and sitemap.')

# Content-based asset URLs keep previews and deployed pages current after edits.
from urllib.parse import urlsplit
versioned = ['styles.css', 'assets/site.js', 'assets/analytics-consent.js', 'assets/portfolio-pages.css', 'assets/portfolio-links.css', 'assets/code-highlight.js', 'assets/code-highlight.css', 'android-security-training/training.css', 'elchem/style.css', 'dontgotobed/styles.css']
asset_versions = {(ROOT/name).resolve(): hashlib.sha256((ROOT/name).read_bytes()).hexdigest()[:12] for name in versioned}
for f in ROOT.rglob('*.html'):
    if 'templates' in f.relative_to(ROOT).parts or any(part.startswith('.') for part in f.relative_to(ROOT).parts): continue
    def version_asset(match):
        attr, url = match.groups()
        parts = urlsplit(url)
        if parts.scheme or parts.netloc: return match.group(0)
        target = (ROOT / parts.path.lstrip('/') if parts.path.startswith('/') else f.parent / parts.path).resolve()
        digest = asset_versions.get(target)
        return f'{attr}="{parts.path}?v={digest}"' if digest else match.group(0)
    text = f.read_text()
    updated = re.sub(r'(href|src)="([^"<>]+)"', version_asset, text)
    if updated != text: f.write_text(updated)
