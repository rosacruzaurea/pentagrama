"""Check generated routes, local assets, content isolation and publication size."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from site_config import BASE, NOINDEX
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
errors=[]
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
        if tag=='meta' and attrs.get('name')=='robots':
            expected='noindex,follow' if NOINDEX else 'index,follow'
            if attrs.get('content')!=expected:errors.append(f'{self.path}: wrong indexing policy')
        if tag in {'iframe','object','embed','base'}:errors.append(f'{self.path}: forbidden {tag}')
        if tag=='script' and attrs.get('src')!=BASE+'/assets/app.js':errors.append(f'{self.path}: unexpected script')
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
expected_robots='User-agent: *\n'+('Disallow: /\n' if NOINDEX else 'Allow: /\n')
if (SITE/'robots.txt').read_text()!=expected_robots:errors.append('robots.txt does not match indexing policy')

files=[]
for p in SITE.rglob('*'):
    if not p.is_file():continue
    rel=str(p.relative_to(SITE));size=p.stat().st_size
    if p.suffix.lower() not in {'.html','.css','.js','.png','.jpg','.jpeg','.gif','.pdf','.epub','.mobi','.ttf','.txt',''} and p.name!='.nojekyll':
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
