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
# Preserve the editorial order within each section from the project catalogue.
project_groups = [('Apps & platforms', 'client-work', 'Apps & platforms'), ('Client websites', 'client-websites', 'Client websites'), ('Own projects', 'own-projects', 'Apps, games & developer tools'), ('Public code', 'public-code', 'GitHub examples & experiments')]
projects = [p for kind, _, _ in project_groups for p in projects if p['kind'] == kind]

articles = load('articles.json')
resources = load('resources.json')
services = load('services.json')
services_de = load('services-de.json')
project_summaries_de = load('project-summaries-de.json')
article_services = load('article-services.json')
videos = load('videos.json')
guides = load('guides.json')

def guide_path(guide):
    return guide.get('path', '/guides/' + guide['slug'] + '/')

def header(active='', lang='en'):
    if lang == 'de':
        return header_de()
    links = [('/#services','Services'),('/#how-we-work','Process'),('/projects.html','Work'),('/#insights','Testimonials'),('/blog.html','Blog'),('/#contact','Discuss your project')]
    items = ''.join(f'<li><a href="{url}"'+(' aria-current="page"' if active==label else '')+(' class="contact-link project-cta"' if label=='Discuss your project' else '')+f'>{esc(label)}</a></li>' for url,label in links)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><nav class="site-nav" aria-label="Primary">
<a class="site-brand" href="/" aria-label="James Cullimore Software Engineering home"><img src="/assets/branding/logo-black.png" width="56" height="56" alt=""><span><strong>James Cullimore</strong><small>Software Engineering</small></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-links">Menu +</button><ul class="site-links" id="site-links">{items}</ul>
</nav></header>'''

def footer(lang='en'):
    if lang == 'de':
        return (ROOT/'templates/footer-de.html').read_text().strip()
    return (ROOT/'templates/footer.html').read_text().strip()

def header_de():
    return '<a class="skip-link" href="#main">Zum Inhalt</a><header class="site-header"><nav class="site-nav" aria-label="Hauptnavigation"><a class="site-brand" href="/de/leistungen/"><img src="/assets/branding/logo-black.png" width="56" height="56" alt=""><span><strong>James Cullimore</strong><small>Softwareentwicklung</small></span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-links">Menü +</button><ul class="site-links" id="site-links"><li><a href="/de/leistungen/">Leistungen</a></li><li><a href="/projects.html" hreflang="en">Projekte (Englisch)</a></li><li><a href="/apps/" hreflang="en">Apps (Englisch)</a></li><li><a class="contact-link" href="mailto:info@jamescullimore.dev?subject=Projektanfrage">Projekt besprechen</a></li></ul></nav></header>'

def page(title,description,path,content,active='',schema=None,scripts='',image='/assets/branding/social-preview.png',lang='en',alternates=None):
    url=BASE+path
    alternate_tags = ''.join(f'<link rel="alternate" hreflang="{code}" href="{BASE}{route}">' for code,route in (alternates or {}).items())
    if path != '/projects/elchem.html':
        scripts += '<script defer src="/assets/conversion-analytics.js"></script>'
    body_class = 'home-page' if path == '/' else 'portfolio-page service-page' if path.startswith(('/services/', '/de/leistungen/')) else 'portfolio-page'
    extra_styles = '' if path == '/' else '<link rel="stylesheet" href="/assets/portfolio-pages.css">'
    schema=schema or {'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'url':url}
    image=image if image.startswith('https:') else BASE+image
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | James Cullimore</title><meta name="description" content="{esc(description,quote=True)}"><meta name="author" content="James Cullimore"><meta name="theme-color" content="#fcfcf9">
<link rel="canonical" href="{esc(url)}">{alternate_tags}<link rel="icon" href="/img/favicon.ico"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title,quote=True)}"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="James Cullimore Software Engineering"><meta property="og:image" content="{esc(image)}"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/styles.css?v={STYLE_VERSION}">{extra_styles}<script defer src="/assets/site.js"></script><script defer src="/assets/analytics-consent.js"></script>{scripts}
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('</','<\\/')}</script>
</head><body class="{body_class}">{header(active,lang)}<main id="main">{content}</main>{footer(lang)}</body></html>'''

def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text+'\n')

def project_card(p):
    pic=f'<img class="project-icon" src="{p["image"]}" alt="" width="64" height="64" loading="lazy">' if p.get('image') else ''
    return f'''<article class="project-card">{pic}<span class="eyebrow">{esc(p.get('engagement', p['kind']))}</span><h3><a href="/projects/{p['slug']}.html">{esc(p['name'])}</a></h3><p>{esc(p['summary'])}</p><div class="card-bottom"><span>{esc(' · '.join(p['focus']))}</span><span class="card-arrow" aria-hidden="true">↗</span></div></article>'''

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
product_paths = {'dont-go-to-bed': '/dontgotobed/', 'starjar': '/starjar/', 'watchful': '/watchful/'}
for i, slug in enumerate(own_slugs):
    if slug in product_paths:
        name = next(p['name'] for p in projects if p['slug'] == slug)
        own_cards[i] = own_cards[i].replace('</article>', f'<p><a class="text-link app-download-link" href="{product_paths[slug]}">Explore {esc(name)} &amp; get the app</a></p></article>')
home=home.replace('{{own_projects}}', ''.join(own_cards))
write('index.html',page('Freelance Android & Kotlin Multiplatform Developer','Freelance Android and Kotlin Multiplatform development, app security and test automation. Based in Germany, working in English and German.','/',home,schema=load('organization.json')))

intro='<section class="page-intro"><div class="section-inner"><span class="eyebrow">The project catalogue</span><h1>Work, in a little more detail.</h1><p class="lead">Client collaborations, work from employed roles, independent products and public engineering examples. Explore the context, the contribution and the product behind each project.</p><nav class="project-tabs" aria-label="Project categories"><a href="#client-work">Apps &amp; platforms</a><a href="#client-websites">Client websites</a><a href="#own-projects">Own projects</a><a href="#public-code">GitHub projects</a></nav></div></section>'
groups=''
for kind,anchor,heading in project_groups:
    groups+=f'<section class="project-group" id="{anchor}"><span class="eyebrow">{esc(kind)}</span><h2>{esc(heading)}</h2><div class="project-grid">'+''.join(project_card(p) for p in projects if p['kind']==kind)+'</div></section>'
content=intro+'<div class="section"><div class="section-inner">'+groups+'<div class="section-actions"><a class="text-link" href="https://github.com/LethalMaus?tab=repositories">More projects on GitHub</a></div></div></div>'
schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Projects by James Cullimore','url':BASE+'/projects.html','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+'/projects/'+p['slug']+'.html','name':p['name']} for i,p in enumerate(projects)]}}
write('projects.html',page('Projects — Client Work, Apps & Games','Explore client engineering work, StarJar, Don’t Go To Bed, Android Security Training, Elchem and Watchful. Project details, product sites and app links.','/projects.html',content,'Work',schema))

# A visitor-facing directory, separate from engineering case studies.
discovery_paths = {**product_paths, 'elchem': '/elchem/'}
app_summaries = {
    'starjar': ('Chores and rewards for families', 'Create chores, review completed tasks and let children save stars for rewards you choose together.', 'Free plan; optional Premium adds unlimited tasks and rewards, plus multiple child profiles.'),
    'watchful': ('Personal alerts for public web updates', 'Describe the prices, releases or other public information you want to follow. Watchful checks for matches and links to the sources.', 'Two active watchers with your own AI API key; provider usage costs are separate. The iOS app also offers monthly AI credit plans.'),
    'dont-go-to-bed': ('A family building and exploration adventure', 'Play solo or together on the same trusted Wi-Fi. Build a path, explore the world and find Mammy before nightfall.', 'All characters and gameplay are free. Optional tips support development.'),
    'elchem': ('Explore a world of elements and encounters', 'Follow a real-world map, discover encounters and prepare with elements, recipes and equipment.', 'In development. Explore the gameplay preview and follow the project.')
}
app_cards = ''
for slug, (heading, description, pricing) in app_summaries.items():
    app = next(p for p in projects if p['slug'] == slug)
    platform = 'Android · In development' if slug == 'elchem' else 'Android & iOS'
    action = 'Explore Elchem' if slug == 'elchem' else f'Explore {app["name"]} & download'
    watch = next(video for video in videos if video['product_path'] == discovery_paths[slug])
    app_cards += f'<article class="app-discovery-card"><img src="{esc(app["image"])}" width="72" height="72" alt=""><span class="eyebrow">{esc(platform)}</span><h2>{esc(app["name"])}</h2><h3>{esc(heading)}</h3><p>{esc(description)}</p><p class="app-plan">{esc(pricing)}</p><a class="button" href="{discovery_paths[slug]}">{esc(action)}</a><a class="text-link" href="/videos/{watch['slug']}/">Watch the {esc(app["name"])} trailer</a></article>'
app_content = f'<section class="page-intro"><div class="section-inner"><span class="eyebrow">Made by James Cullimore</span><h1>Apps for everyday life.<br>Games for a little adventure.</h1><p class="lead">Chore rewards, personal web alerts, a family adventure and Elchem’s world of elements. Explore the apps you can download and the game still in development.</p></div></section><section class="section"><div class="section-inner app-discovery-grid">{app_cards}</div></section><section class="section soft"><div class="section-inner"><h2>Need help building your own app?</h2><p class="lead">I also work with product teams on Android and Kotlin Multiplatform development, app modernisation and automated testing.</p><a class="text-link" href="/services/android-kotlin-multiplatform/">Explore Android and KMP development services</a></div></section>'
app_schema = {'@context':'https://schema.org','@type':'CollectionPage','name':'Apps and games for Android and iOS','url':BASE+'/apps/','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+discovery_paths[slug]} for i,slug in enumerate(app_summaries)]}}
write('apps/index.html', page('Apps & Games for Android and iOS', 'Explore StarJar, Watchful and Don’t Go To Bed for Android and iOS, plus Elchem’s map-based adventure in development. Screenshots, gameplay and app links.', '/apps/', app_content, schema=app_schema))

# Dedicated watch pages keep the video as the primary content.
video_cards = ''
for video in videos:
    path = '/videos/' + video['slug'] + '/'
    youtube = 'https://www.youtube.com/watch?v=' + video['id']
    embed = 'https://www.youtube-nocookie.com/embed/' + video['id']
    thumbnail = 'https://i.ytimg.com/vi/' + video['id'] + '/hqdefault.jpg'
    video_cards += f'<article class="video-library-card"><a href="{path}"><img src="{thumbnail}" width="480" height="360" alt="" loading="lazy"><h2>{esc(video["title"])}</h2></a><p>{esc(video["description"])}</p><span class="eyebrow">{esc(video["kind"])}</span></article>'
    content = f'<section class="page-intro"><div class="section-inner"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/videos/">App videos</a> / {esc(video["product"])}</nav><h1>{esc(video["title"])}</h1><p class="lead">{esc(video["description"])}</p></div></section><section class="section"><div class="section-inner video-watch"><div class="video-watch-frame"><iframe src="{embed}" title="{esc(video["title"])}" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div><p class="video-context">{esc(video["note"])}</p><p><a class="text-link" href="{youtube}">Watch on YouTube</a> · Published <time datetime="{video["upload_date"]}">{video["upload_date"][:10]}</time></p><h2>About {esc(video["product"])}</h2><p class="lead">{esc(video["context"])}</p><div class="service-actions"><a class="button" href="{video["product_path"]}">Explore {esc(video["product"])}</a><a class="text-link" href="/videos/">More app videos</a></div></div></section>'
    schema = {'@context':'https://schema.org','@type':'VideoObject','@id':BASE+path+'#video','name':video['title'],'description':video['description'],'thumbnailUrl':[thumbnail],'uploadDate':video['upload_date'],'embedUrl':embed,'url':BASE+path,'mainEntityOfPage':BASE+path,'publisher':{'@type':'Person','name':'James Cullimore','url':BASE+'/'}}
    write(path.lstrip('/')+'index.html', page(video['title'],video['description'],path,content,schema=schema,image=thumbnail))
video_intro = '<section class="page-intro"><div class="section-inner"><span class="eyebrow">See the apps in action</span><h1>App and game videos</h1><p class="lead">Explore the official trailers for StarJar, Watchful, Don’t Go To Bed and Elchem, then visit each app’s page for current features and availability.</p></div></section>'
write('videos/index.html', page('App & Game Videos','Watch StarJar, Watchful, Don’t Go To Bed and Elchem videos. Official trailers with product information and links to explore each app.','/videos/',video_intro+'<section class="section"><div class="section-inner video-library-grid">'+video_cards+'</div></section>'))

# Authored guides share metadata and reciprocal translation links.
for guide in guides:
    path = guide_path(guide)
    lang = guide.get('lang', 'en')
    content = (ROOT / 'templates/guides' / (guide['slug'] + '.html')).read_text()
    alternates = None
    if guide.get('translation'):
        translated = next(g for g in guides if g['slug'] == guide['translation'])
        alternates = {lang: path, translated.get('lang', 'en'): guide_path(translated)}
        alternates['x-default'] = alternates['en']
        switch = '<nav class="language-switch" aria-label="'+('Seitensprache' if lang == 'de' else 'Page language')+'">'+''.join(f'<span aria-current="page" lang="{code}">{label}</span>' if code == lang else f'<a href="{alternates[code]}" hreflang="{code}" lang="{code}">{label}</a>' for code,label in [('en','English'),('de','Deutsch')])+'</nav>'
        content = content.replace('<span class="eyebrow">',switch+'<span class="eyebrow">',1)
    schema = {'@context':'https://schema.org','@type':'Article','headline':guide['title'],'description':guide['description'],'datePublished':guide['date'],'author':{'@type':'Person','name':'James Cullimore','url':BASE+'/'},'mainEntityOfPage':BASE+path,'inLanguage':lang}
    write(path.lstrip('/')+'index.html', page(guide['title'],guide['description'],path,content,schema=schema,scripts='<link rel="stylesheet" href="/assets/guides.css">',lang=lang,alternates=alternates))

# Service evidence is drawn from the existing catalogue and published testimonials.
service_evidence = load('service-evidence.json')
testimonials=load('testimonials.json') if (ROOT/'data/testimonials.json').exists() else json.loads((ROOT/'testimonials.json').read_text())
def evidence_block(service_slug, lang='en'):
    item = next(e for e in service_evidence if e['service'] == service_slug)
    project = next(p for p in projects if p['slug'] == item['project'])
    testimonial = next(t for t in testimonials if t['author'] == item['author'])
    assert item['excerpt'] in testimonial['text'], 'Testimonial excerpts must match the published source'
    de = lang == 'de'
    context = item['de']['context'] if de else project['context']
    work = item['de']['work'] if de else ' '.join(project['work'])
    outcome = item['de'].get('outcome') if de else project.get('outcome')
    result = f'<dt>{"Dokumentiertes Ergebnis" if de else "Documented result"}</dt><dd>{esc(outcome)}</dd>' if outcome else ''
    caveat = '<p class="evidence-note">Results from this project’s environment; not a forecast for another codebase.</p>' if not de and item['project'] == 'blackned' else ''
    return f'''<div class="service-evidence"><div><span class="eyebrow">{"Ein konkretes Beispiel" if de else "A closer look"}</span><h3>{esc(project['name'])}</h3><dl><dt>{"Die Aufgabe" if de else "The brief"}</dt><dd>{esc(context)}</dd><dt>{"Mein Beitrag" if de else "My contribution"}</dt><dd>{esc(work)}</dd>{result}</dl>{caveat}<a href="/projects/{project['slug']}.html" hreflang="en">{"Projektbeschreibung lesen (Englisch)" if de else "Read the project details"}</a></div><aside><h3>{"Aus der Zusammenarbeit mit" if de else "From the team at"} {esc(testimonial['company'])}</h3><blockquote lang="en"><p>“{esc(item['excerpt'])}”</p><cite>{esc(testimonial['author'])}, {esc(testimonial['company'])}</cite></blockquote><p class="evidence-note">{"Auszug aus dem veröffentlichten Originalzitat auf Englisch." if de else "Excerpt from the published testimonial."}</p><a href="/projects/{item['quote_project']}.html" hreflang="en">{"Vollständiges Zitat und Projekt (Englisch)" if de else "Read the full testimonial and project"}</a></aside></div>'''

# Focused service pages use the same shell and verified project catalogue.
from urllib.parse import quote
for service in services:
    path = '/services/' + service['slug'] + '/'
    translated = next(item for item in services_de if item['slug'] == service['slug'])
    de_path = '/de/leistungen/' + translated['de_slug'] + '/'
    alternates = {'en':path, 'de':de_path, 'x-default':path}
    email = 'mailto:info@jamescullimore.dev?subject=' + quote(service['subject'])
    work = ''.join(f'<article class="service"><span class="service-number" aria-hidden="true">0{i+1}</span><h3>{esc(title)}</h3><p>{esc(body)}</p></article>' for i, (title, body) in enumerate(service['work']))
    evidence = evidence_block(service['slug'])
    proof = ''.join(project_card(next(p for p in projects if p['slug'] == slug)) for slug in service['proof'])
    questions = ''.join(f'<details><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>' for question, answer in service['questions'])
    guide_link = ''.join(f'<p class="service-reading"><a class="text-link" href="/guides/{guide["slug"]}/">Read the guide: {esc(guide["title"])}</a></p>' for guide in guides if guide.get('service') == service['slug'] and guide.get('lang', 'en') == 'en')
    related = ''.join(f'<a href="/services/{other["slug"]}/">{esc(other["title"])}</a>' for other in services if other != service)
    content = f'''<section class="page-intro"><div class="section-inner"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/#services">Services</a></nav><nav class="language-switch" aria-label="Page language"><span aria-current="page" lang="en">English</span><a href="{de_path}" hreflang="de" lang="de">Deutsch</a></nav><span class="eyebrow">{esc(service['title'])}</span><h1>{esc(service['heading'])}</h1><p class="lead">{esc(service['intro'])}</p><div class="service-actions"><a class="button" href="{email}">Discuss your project</a><a class="text-link" href="#relevant-work">See relevant work</a></div><p class="service-byline">James Cullimore <span aria-hidden="true">·</span> Based in Germany <span aria-hidden="true">·</span> English &amp; German</p></div></section>
<section class="section"><div class="section-inner"><h2>Where I can help</h2><p class="lead">{esc(service['fit'])}</p><div class="service-deliverables">{work}</div></div></section>
<section class="section soft"><div class="section-inner"><h2>A manageable first step</h2><p class="service-reading">{esc(service['start'])}</p>{guide_link}</div></section>
<section class="section" id="relevant-work"><div class="section-inner"><span class="eyebrow">From the project catalogue</span><h2>Relevant work</h2>{evidence}<div class="project-grid">{proof}</div></div></section>
<section class="section soft"><div class="section-inner service-faq"><h2>Before we start</h2>{questions}</div></section>
<section class="section service-enquiry"><div class="section-inner"><h2>Tell me where you need help.</h2><p class="service-reading">{esc(service['prompt'])}</p><div class="service-actions"><a class="button" href="{email}">Email James about your project</a><a class="text-link" href="/#contact">Other ways to get in touch</a></div><nav class="related-services" aria-label="Related services">{related}<a href="/android-security-training/">Android security workshops</a></nav></div></section>'''
    schema = {'@context':'https://schema.org', '@type':'Service', 'name':service['title'], 'description':service['description'], 'url':BASE+path, 'provider':{'@type':'Person','name':'James Cullimore','url':BASE+'/'}}
    write(path.lstrip('/')+'index.html', page(service['title'], service['description'], path, content, schema=schema, alternates=alternates))

# German services have self canonicals and reciprocal language alternates.
for service in services_de:
    original = next(item for item in services if item['slug'] == service['slug'])
    path = '/de/leistungen/' + service['de_slug'] + '/'
    en_path = '/services/' + service['slug'] + '/'
    email = 'mailto:info@jamescullimore.dev?subject=' + quote(service['subject'])
    work = ''.join(f'<article class="service"><span class="service-number" aria-hidden="true">0{i+1}</span><h3>{esc(title)}</h3><p>{esc(body)}</p></article>' for i,(title,body) in enumerate(service['work']))
    evidence = evidence_block(service['slug'], 'de')
    proof = ''
    for slug in original['proof']:
        project = next(item for item in projects if item['slug'] == slug)
        proof += f'<article class="project-card"><span class="eyebrow">Projekterfahrung</span><h3><a href="/projects/{slug}.html" hreflang="en">{esc(project["name"])}</a></h3><p>{esc(project_summaries_de[slug])}</p><div class="card-bottom"><span>Projektbeschreibung auf Englisch</span><span aria-hidden="true">↗</span></div></article>'
    questions = ''.join(f'<details><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>' for question,answer in service['questions'])
    guide_link = ''.join(f'<p class="service-reading"><a class="text-link" href="{guide_path(guide)}">Zum Leitfaden: {esc(guide["title"])}</a></p>' for guide in guides if guide.get('service') == service['slug'] and guide.get('lang') == 'de')
    related = ''.join(f'<a href="/de/leistungen/{other["de_slug"]}/">{esc(other["title"])}</a>' for other in services_de if other != service)
    content = f'''<section class="page-intro"><div class="section-inner"><nav class="breadcrumbs" aria-label="Seitenpfad"><a href="/de/leistungen/">Leistungen</a></nav><nav class="language-switch" aria-label="Seitensprache"><a href="{en_path}" hreflang="en" lang="en">English</a><span aria-current="page" lang="de">Deutsch</span></nav><span class="eyebrow">{esc(service['title'])}</span><h1>{esc(service['heading'])}</h1><p class="lead">{esc(service['intro'])}</p><div class="service-actions"><a class="button" href="{email}">Projekt besprechen</a><a class="text-link" href="#relevante-projekte">Passende Projekte ansehen</a></div><p class="service-byline">James Cullimore · Standort Deutschland · Deutsch und Englisch</p></div></section>
<section class="section"><div class="section-inner"><h2>Wobei ich helfen kann</h2><p class="lead">{esc(service['fit'])}</p><div class="service-deliverables">{work}</div></div></section>
<section class="section soft"><div class="section-inner"><h2>Ein überschaubarer erster Schritt</h2><p class="service-reading">{esc(service['start'])}</p>{guide_link}</div></section>
<section class="section" id="relevante-projekte"><div class="section-inner"><h2>Passende Projekterfahrung</h2>{evidence}<div class="project-grid">{proof}</div></div></section>
<section class="section soft"><div class="section-inner service-faq"><h2>Vor der Zusammenarbeit</h2>{questions}</div></section>
<section class="section service-enquiry"><div class="section-inner"><h2>Wo brauchen Sie Unterstützung?</h2><p class="service-reading">{esc(service['prompt'])}</p><div class="service-actions"><a class="button" href="{email}">James zum Projekt schreiben</a><a class="text-link" href="mailto:info@jamescullimore.dev">info@jamescullimore.dev</a></div><nav class="related-services" aria-label="Weitere Leistungen">{related}</nav></div></section>'''
    schema = {'@context':'https://schema.org','@type':'Service','name':service['title'],'description':service['description'],'url':BASE+path,'provider':{'@type':'Person','name':'James Cullimore','url':BASE+'/'}}
    write(path.lstrip('/')+'index.html', page(service['title'],service['description'],path,content,schema=schema,lang='de',alternates={'en':en_path,'de':path,'x-default':en_path}))

service_cards_de = ''.join(f'<article class="project-card"><h2><a href="/de/leistungen/{item["de_slug"]}/">{esc(item["title"])}</a></h2><p>{esc(item["fit"])}</p><a class="text-link" href="/de/leistungen/{item["de_slug"]}/">Leistung ansehen</a></article>' for item in services_de)
content_de = f'<section class="page-intro"><div class="section-inner"><span class="eyebrow">James Cullimore · Freiberuflicher Softwareentwickler</span><h1>Android-Entwicklung, Modernisierung und zuverlässigere Releases.</h1><p class="lead">Ich unterstütze Produktteams bei Android und Kotlin Multiplatform, bei der Übernahme bestehender Apps sowie bei Tests und Build-Prozessen. Standort Deutschland, Zusammenarbeit auf Deutsch und Englisch, überwiegend remote.</p><div class="service-actions"><a class="button" href="mailto:info@jamescullimore.dev?subject=Projektanfrage">Projekt besprechen</a><a class="text-link" href="/#services" hreflang="en" lang="en">Services in English</a></div></div></section><section class="section"><div class="section-inner"><div class="project-grid">{service_cards_de}</div></div></section>'
write('de/leistungen/index.html', page('Android-Freelancer in Deutschland – Leistungen','Android, Kotlin Multiplatform, App-Modernisierung, Testautomatisierung und Gradle-Optimierung. Freiberufliche Entwicklung mit James Cullimore.','/de/leistungen/',content_de,lang='de'))

# The training landing page shares the company shell and has its own scoped layout.
training = (ROOT/'templates/security-training.html').read_text()
write('android-security-training/index.html', page('Android Security Training & Workshops', 'Hands-on Android security workshops led by James Cullimore. Explore four practical modules, vulnerable and secure app labs, and tailored team training.', '/android-security-training/', training, scripts='<link rel="stylesheet" href="/android-security-training/training.css">'))

testimonial_names={'jc-bachmann':'J&C Bachmann','benefits-me':'Benefits.me','lexoffice':'Lexoffice','marktgalerie':'Marktmeister Pro','neurofly':'Neurofly','farmerjoe':'farmerJoe'}
for p in projects:
    path='/projects/'+p['slug']+'.html'
    tags=''.join(f'<span>{esc(t)}</span>' for t in p['focus'])
    image=f'<img src="{p["image"]}" alt="{esc(p["name"])}" loading="lazy">' if p.get('image') else ''
    links=''.join(f'<a href="{esc(link["url"])}">{esc(link["label"])} <span aria-hidden="true">↗</span></a>' for link in p['links'])
    quote=''
    t=next((t for t in testimonials if t['company']==testimonial_names.get(p['slug'])),None)
    if t:
        quote=f'<section><h2>From the team</h2><blockquote><p>“{esc(t["text"])}”</p><cite>{esc(t["author"])}, {esc(t["company"])}</cite></blockquote></section>'
    next_step = '<section><h2>Working on something similar?</h2><p>Tell us about your product, your team and the support you need.</p><a class="button" href="/#contact">Discuss your project ↗</a></section>'
    if p['slug'] in product_paths:
        next_step = f'<section><h2>Try {esc(p["name"])}.</h2><p>See the app in action, read the FAQs and choose your store.</p><a class="button" href="{product_paths[p["slug"]]}">Explore {esc(p["name"])} &amp; download</a><p><a href="/apps/">Browse all apps and games</a></p></section>'
    else:
        relevant = [service for service in services if p['slug'] in service['proof']]
        if relevant:
            next_step = '<section><h2>Need similar help?</h2><p>Explore the relevant services and how we can start.</p><ul>' + ''.join(f'<li><a href="/services/{service["slug"]}/">{esc(service["title"])}</a></li>' for service in relevant) + '</ul><a class="button" href="/#contact">Discuss your project</a></section>'
    decision_links = ''.join(f'<p><a href="/guides/{guide["slug"]}/">{esc(guide["title"])}</a></p>' for guide in guides if p['slug'] in guide.get('projects', []) and guide.get('lang', 'en') == 'en')
    if decision_links:
        next_step += '<section><h2>Planning a similar change?</h2>'+decision_links+'</section>'
    outcome = f'<section><h2>The result</h2><p>{esc(p["outcome"])}</p></section>' if p.get('outcome') else ''
    content=f'''<section class="page-intro"><div class="section-inner"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/projects.html">Projects</a> / {esc(p['name'])}</nav><span class="eyebrow">{esc(p.get('engagement', p['kind']))}</span><h1>{esc(p['name'])}</h1><p class="lead">{esc(p['summary'])}</p><div class="detail-tags">{tags}</div><a class="text-link" href="#project-links">Project links <span aria-hidden="true">↓</span></a></div></section>
<section class="section"><div class="section-inner detail-layout"><div class="detail-content"><section><h2>{"The brief" if p.get("outcome") else "The project"}</h2><p>{esc(p['context'])}</p></section><section><h2>{'Inside the product' if p['kind']=='Own projects' else 'What it demonstrates' if p['kind']=='Public code' else 'What we delivered' if p.get('outcome') else 'The contribution'}</h2><ul>{''.join('<li>'+esc(w)+'</li>' for w in p['work'])}</ul></section>{outcome}{quote}{next_step}</div><aside class="detail-aside" id="project-links">{image}<h2>Explore the project</h2>{links}<hr><a href="/projects.html">← All projects</a></aside></div></section>'''
    schema={'@context':'https://schema.org','@type':'WebPage','name':p['name']+' — project details','description':p['summary'],'url':BASE+path,'breadcrumb':{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Projects','item':BASE+'/projects.html'},{'@type':'ListItem','position':3,'name':p['name'],'item':BASE+path}]}}
    write(path.lstrip('/'),page(p['name']+' — Project Details',p['summary'],path,content,'Work',schema,image=p['image'] if p.get('image') and not p['image'].endswith('.svg') else '/assets/branding/social-preview.png'))

talk_slides=''.join(f'<article class="service"><span class="eyebrow">Talk slides</span><h3>{esc(t["title"])}</h3><p>{esc(t["description"])}</p><a class="text-link" href="{esc(t["url"])}">View slides on Speaker Deck ↗</a></article>' for t in resources['talk_slides'])
courses=''.join(f'<article class="service"><span class="eyebrow">{esc(c["platform"])}</span><h3>{esc(c["title"])}</h3><p>{esc(c["description"])}</p><a class="text-link" href="{esc(c["url"])}">View course ↗</a></article>' for c in resources['courses'])
content=f'''<section class="page-intro"><div class="section-inner"><span class="eyebrow">Learn from practical experience</span><h1>Courses, talks &amp; workshops</h1><p class="lead">Explore conference videos and slides, learn with droidcon Academy, or bring a focused Android workshop to your team.</p></div></section><section class="section soft"><div class="section-inner"><div class="section-heading-row"><h2>Learn at your own pace</h2><a class="text-link" href="{esc(resources['academy_profile'])}">My droidcon Academy profile ↗</a></div><div class="course-grid">{courses}<article class="service"><span class="eyebrow">Team workshop</span><h3>Android Security Training</h3><p>Hands-on labs with vulnerable and secure app variants. Inspect, fix and verify Android security issues.</p><a class="text-link" href="/android-security-training/">Explore the syllabus ↗</a></article><article class="service"><span class="eyebrow">Free book</span><h3>5 Minute Bedtime Stories for Android Devs</h3><p>Short stories about production surprises, developer folklore and the decisions every mobile team recognises.</p><a class="text-link" href="/5-minute-bedtime-stories-for-android-devs.html">Read the book ↗</a></article></div></div></section><section class="section"><div class="section-inner community-grid"><div><h2>Watch a talk</h2><p class="lead">Engineering ideas, lessons from delivery, and the decisions behind better Android apps.</p></div><div><div class="video-frame"><iframe src="https://www.youtube-nocookie.com/embed/MXHt0_2iKgA" title="James Cullimore conference talk" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>{playlist_link()}</div></div></section><section class="section" id="talk-slides"><div class="section-inner"><div class="section-heading-row"><h2>Browse the talk slides</h2><a class="text-link" href="{esc(resources['speakerdeck_profile'])}">All decks on Speaker Deck ↗</a></div><p>Revisit a talk or explore the slides at your own pace.</p><div class="course-grid">{talk_slides}</div></div></section>'''
write('courses.html',page('Android Courses, Talks & Workshops','Watch James Cullimore’s conference videos, browse Speaker Deck slides, explore droidcon Academy courses and book Android security training.','/courses.html',content,'Courses'))

page_count=math.ceil(len(articles)/12)
def blog_path(n): return '/blog.html' if n==1 else f'/blog/page-{n}.html'
for n in range(1,page_count+1):
    path=blog_path(n)
    pagination='<nav class="pagination" aria-label="Blog pages">'+''.join(f'<a href="{blog_path(i)}"'+(' aria-current="page"' if i==n else '')+f' aria-label="Page {i}">{i}</a>' for i in range(1,page_count+1))+'</nav>'
    if n<page_count: pagination=pagination.replace('</nav>',f'<a href="{blog_path(n+1)}" rel="next">Next →</a></nav>')
    content=f'''<section class="page-intro"><div class="section-inner"><span class="eyebrow">The engineering notebook</span><h1>Notes from the work.</h1><p class="lead">Android development, architecture, performance, security and the experience of building software.</p><form class="blog-tools" role="search" hidden><label>Search articles<input id="blog-search" type="search" placeholder="Try Kotlin, testing or security…" autocomplete="off"></label><label>Topic<select id="blog-topic"><option value="">All topics</option><option>Security</option><option>Testing</option><option>Performance</option><option>Architecture</option><option>Compose</option><option>IoT &amp; Wear OS</option><option>Developer life</option></select></label></form><p class="blog-status" id="blog-status" role="status">{len(articles)} articles · Page {n} of {page_count}</p></div></section><section class="section"><div class="section-inner"><div class="blog-grid" id="blog-grid">{''.join(blog_card(a) for a in articles[(n-1)*12:n*12])}</div>{pagination}<button class="button secondary" id="more-results" type="button" hidden>Show more results</button></div></section>'''
    if n == 1:
        guide_links = ''.join(f'<li><a href="/guides/{guide["slug"]}/">{esc(guide["title"])}</a><p>{esc(guide["description"])}</p></li>' for guide in guides if guide.get('service') and guide.get('lang', 'en') == 'en')
        content += '<section class="section soft"><div class="section-inner"><h2>Planning work on an existing app?</h2><ul>'+guide_links+'</ul></div></section>'
    schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Engineering articles'+(f' — page {n}' if n>1 else ''),'url':BASE+path,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+a['url'],'name':a['title']} for i,a in enumerate(articles[(n-1)*12:n*12])]}}
    write(path.lstrip('/'),page('Android Engineering Blog'+(f' — Page {n}' if n>1 else ''),'Practical articles on Android, Kotlin, testing, security, architecture and software delivery.'+(f' Browse page {n} of the archive.' if n>1 else ''),path,content,'Blog',schema,scripts='<script defer src="/assets/blog.js"></script>'))

def redirect(path,dest,title):
    canonical = BASE + dest.split('#', 1)[0]
    write(path,f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><link rel="canonical" href="{canonical}"><meta http-equiv="refresh" content="0;url={dest}"></head><body><p><a href="{dest}">{esc(title)}</a></p></body></html>')
for item in load('redirects.json'):
    redirect(item['path'], item['destination'], item['title'])

# GitHub Pages retains HTTP 404 while rendering this helpful fallback.
missing = page('Page not found', 'Find services, apps and articles by James Cullimore.', '/404.html', '<section class="page-intro"><div class="section-inner"><span class="eyebrow">404 · Page not found</span><h1>That page is no longer here.</h1><p class="lead">The address may be out of date or mistyped. These links will help you find your way.</p><nav class="project-tabs" aria-label="Find a page"><a href="/">Home</a><a href="/#services">Services</a><a href="/projects.html">Projects &amp; apps</a><a href="/blog.html">Articles</a><a href="/#contact">Contact James</a></nav></div></section>')
missing = missing.replace(f'<link rel="canonical" href="{BASE}/404.html">', '<meta name="robots" content="noindex, follow">')
write('404.html', missing)

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
    if f.parent.name == 'articles':
        for asset in ['analytics-consent.js', 'conversion-analytics.js']:
            if '/assets/' + asset not in s:
                s = s.replace('</head>', f'<script defer src="/assets/{asset}"></script>\n</head>')
        s = re.sub(r'<!-- article-service:start -->.*?<!-- article-service:end -->', '', s, flags=re.S)
        recommendation = next((item for item in article_services if f.stem in item['articles']), None)
        if recommendation:
            box = f'<!-- article-service:start --><aside class="article-service" aria-labelledby="article-service-title"><h2 id="article-service-title">{esc(recommendation["heading"])}</h2><p>{esc(recommendation["copy"])}</p><a href="{recommendation["destination"]}">{esc(recommendation["label"])}</a></aside><!-- article-service:end -->'
            s = s.replace('</main>', box + '</main>', 1)
            if '/assets/article-service.css' not in s:
                s = s.replace('</head>', '<link rel="stylesheet" href="/assets/article-service.css">\n</head>')
    f.write_text(s)

# List canonical, substantive pages only, retaining known publication/modification dates.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
old=ET.parse(ROOT/'sitemap.xml')
dates={u.find('s:loc',ns).text:u.find('s:lastmod',ns).text for u in old.findall('s:url',ns) if u.find('s:lastmod',ns) is not None}
urls=[BASE+'/',BASE+'/apps/',BASE+'/projects.html',BASE+'/courses.html',*[BASE+blog_path(n) for n in range(1,page_count+1)],BASE+'/impressum.html',BASE+'/datenschutz.html',*[BASE+'/projects/'+p['slug']+'.html' for p in projects],*[BASE+a['url'] for a in articles],BASE+'/starjar/',BASE+'/elchem/',BASE+'/android-security-training/',BASE+'/5-minute-bedtime-stories-for-android-devs.html']
# Retain existing product URLs, including policy pages without lastmod values.
urls += [u.find('s:loc', ns).text for u in old.findall('s:url', ns) if any(folder in u.find('s:loc', ns).text for folder in ['/watchful/', '/dontgotobed/', '/elchem/', '/scrumscore/'])]
urls += [BASE + guide_path(guide) for guide in guides]
urls += [BASE + '/videos/'] + [BASE + '/videos/' + video['slug'] + '/' for video in videos]
urls += [BASE + '/de/leistungen/'] + [BASE + '/de/leistungen/' + service['de_slug'] + '/' for service in services_de]
urls += [BASE + '/services/' + service['slug'] + '/' for service in services]
ET.register_namespace('',ns['s']);tree=ET.Element('{'+ns['s']+'}urlset')
for url in dict.fromkeys(urls):
    node=ET.SubElement(tree,'url');ET.SubElement(node,'loc').text=url
    # Existing article dates reflect content updates, not template-only changes.
    date=dates.get(url)
    if date: ET.SubElement(node,'lastmod').text=date
ET.indent(tree,space='  ')
ET.ElementTree(tree).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print(f'Built homepage, {len(projects)} project details, courses, {page_count} blog pages and sitemap.')

# Content-based asset URLs keep previews and deployed pages current after edits.
from urllib.parse import urlsplit
versioned = ['styles.css', 'assets/site.js', 'assets/analytics-consent.js', 'assets/book-analytics.js', 'assets/conversion-analytics.js', 'starjar/styles.css', 'watchful/assets/style.css', 'assets/portfolio-pages.css', 'assets/portfolio-links.css', 'assets/article-service.css', 'assets/guides.css', 'assets/video-preview.css', 'assets/video-preview.js', 'assets/code-highlight.js', 'assets/code-highlight.css', 'android-security-training/training.css', 'elchem/style.css', 'dontgotobed/styles.css']
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
