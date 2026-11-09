"""Check generated routes, local assets, content isolation and publication size."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from site_config import BASE, NOINDEX
from content_search import ENGINE_ID, SEARCH_ROUTES, content_security_policy
from seo import ORIGIN, NS, absolute, pdf_paths
from xml.etree import ElementTree as ET
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
errors=[]
content=json.loads((ROOT/'content/site.json').read_text())
if any(e['type']=='artigo' for e in content['entries']):errors.append('Retired article archive remains in content')
if (SITE/'artigos/index.html').exists():errors.append('Retired article catalog remains in artifact')
links=0
for entry in json.loads((ROOT/'content/site.json').read_text())['entries']:
    if entry['type']=='livro':
        available=bool(re.search(r'href="/assets/[^\"]+\.(?:pdf|epub|mobi)"',entry['html']))
        if entry['ebook']!=available:errors.append(f"E-book filter does not reflect available download: {entry['title']}")


class Check(HTMLParser):
    def __init__(self,path):
        super().__init__();self.path=path;self.headings=0
    def handle_starttag(self,tag,attrs):
        global links
        attrs=dict(attrs)
        if tag=='h1':self.headings+=1
        if tag=='meta' and attrs.get('http-equiv')=='Content-Security-Policy':
            route='/' + self.path.removesuffix('index.html')
            if attrs.get('content')!=content_security_policy(bool(ENGINE_ID) and route in SEARCH_ROUTES):errors.append(f'{self.path}: unexpected CSP')
        if tag=='input' and attrs.get('type')=='search' and attrs.get('name')=='q' and attrs.get('maxlength')!='300':errors.append(f'{self.path}: search input must limit length to 300')
        if tag=='meta' and attrs.get('name')=='robots':
            expected='noindex,follow' if NOINDEX or self.path in {'404.html','buscar/index.html'} else 'index,follow'
            if attrs.get('content')!=expected:errors.append(f'{self.path}: wrong indexing policy')
        if tag in {'iframe','object','embed','base'}:errors.append(f'{self.path}: forbidden {tag}')
        if tag=='script' and not (attrs.get('src')==BASE+'/assets/app.js' or (self.path in {'buscar/index.html','livros/index.html','revistas/index.html'} and attrs.get('src')==BASE+'/assets/content-search.js') or (attrs.get('type')=='application/ld+json' and not attrs.get('src'))):errors.append(f'{self.path}: unexpected script')
        if any(k.lower().startswith('on') for k in attrs):errors.append(f'{self.path}: event handler')
        for key in ['href','src']:
            url=attrs.get(key)
            if not url or url.startswith('#'):continue
            u=urlsplit(url)
            if u.scheme not in {'','https','mailto'}:errors.append(f'{self.path}: unsafe URL scheme {url}')
            if not u.netloc and u.scheme!='mailto':
                links+=1
                if not u.path.startswith(BASE+'/'):
                    errors.append(f'{self.path}: outside project base {url}');continue
                p=(SITE/unquote(u.path.removeprefix(BASE+'/'))).resolve()
                if not p.is_relative_to(SITE.resolve()):errors.append(f'{self.path}: traversal');continue
                if p.is_dir():p=p/'index.html'
                if not p.is_file():errors.append(f'{self.path}: missing {url}')
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)


if (SITE/'sobre-o-acervo'/'index.html').exists():errors.append('Retired reconstruction page remains in artifact')
expected_robots='User-agent: *\n'+('Disallow: /\n' if NOINDEX else 'Allow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
if (SITE/'robots.txt').read_text()!=expected_robots:errors.append('robots.txt does not match indexing policy')

expected_routes={'index.html','404.html','blog/index.html','livros/index.html','revistas/index.html','buscar/index.html','contato/index.html'}
for e in content['entries']:
    for route in [e['path'],*e.get('aliases',[])]:expected_routes.add(route.strip('/')+'/index.html')
if (SITE/'demo-busca').exists():errors.append('Demo directory must not be present in ordinary/production artifacts')
actual_routes={str(p.relative_to(SITE)) for p in SITE.rglob('*.html')}
if actual_routes != expected_routes:errors.append({'unexpected_routes':sorted(actual_routes-expected_routes),'missing_routes':sorted(expected_routes-actual_routes)})

# Verify canonical pages, duplicate aliases and discovery of every linked PDF.
canonical_routes={'/','/blog/','/livros/','/revistas/','/contato/'}
canonical_routes.update(e['path'] for e in content['entries'])
canonicals={p:p for p in canonical_routes|{'/buscar/'}}
for e in content['entries']:
    for alias in e.get('aliases',[]):canonicals[alias]=e['path']
for path,target in canonicals.items():
    f=SITE/path.strip('/')/'index.html'
    if not f.is_file():continue
    source=f.read_text()
    matches=re.findall(r'<link rel="canonical" href="([^"\n]+)"',source)
    if matches != [absolute(target)]:errors.append(f'{path}: canonical does not match preferred URL')
    if len(re.findall(r'<meta name="description"',source))!=1:errors.append(f'{path}: missing/duplicate description')
    blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)
    if len(blocks)!=1:errors.append(f'{path}: missing/duplicate JSON-LD graph')
    for block in blocks:
        try:
            data=json.loads(block)
            if data.get('@context')!='https://schema.org' or not data.get('@graph'):errors.append(f'{path}: invalid schema graph')
        except ValueError:errors.append(f'{path}: invalid JSON-LD')
for name,paths in [('sitemap-pages.xml',canonical_routes),('sitemap-pdfs.xml',pdf_paths(content['entries']))]:
    tree=ET.parse(SITE/name)
    locs=[x.text for x in tree.findall('.//{'+NS+'}loc')]
    if set(locs)!={absolute(p) for p in paths} or len(locs)!=len(set(locs)):errors.append(f'{name}: discovery inventory mismatch')
index=ET.parse(SITE/'sitemap.xml')
if {x.text for x in index.findall('.//{'+NS+'}loc')}!={ORIGIN+'/sitemap-pages.xml',ORIGIN+'/sitemap-pdfs.xml'}:errors.append('sitemap index mismatch')
for path in ['/buscar/','/livros/','/revistas/']:
    source=(SITE/path.strip('/')/'index.html').read_text()
    if f'data-engine-id="{ENGINE_ID}"' not in source:errors.append(f'{path}: incorrect content search configuration')
    if 'action="https://www.google.com/search"' not in source or 'name="as_sitesearch" value="pentagrama.org.br"' not in source:errors.append(f'{path}: missing scoped Google search')

files=[]
for p in SITE.rglob('*'):
    if not p.is_file():continue
    rel=str(p.relative_to(SITE));size=p.stat().st_size
    if p.suffix.lower() not in {'.html','.css','.js','.png','.jpg','.jpeg','.gif','.pdf','.epub','.mobi','.ttf','.txt','.xml',''} and p.name!='.nojekyll':
        errors.append(f'Forbidden publication file {rel}')
    if size>95*1024*1024:errors.append(f'File too large for Git {rel}')
    if p.suffix in {'.html','.css','.js'}:
        s=p.read_text()
        if re.search(r'DB_PASSWORD|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|ghp_[a-zA-Z0-9]{20}|AKIA[0-9A-Z]{16}|<\?php',s):errors.append(f'Secret/server marker {rel}')
        if p.suffix=='.html':
            check=Check(rel);check.feed(s)
            if check.headings!=1:errors.append(f'{rel}: h1 count {check.headings}')
    files.append({'path':rel,'bytes':size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
size=sum(f['bytes'] for f in files)
if size>=950000000:errors.append('Pages artifact too close to 1GB limit')
result={'html_pages':len(list(SITE.rglob('*.html'))),'local_links_checked':links,'files':len(files),'bytes':size,'errors':errors}
(ROOT/'docs/artifact-manifest.json').write_text(json.dumps({'summary':result,'files':files},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
