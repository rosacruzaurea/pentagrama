"""Select and sanitize public editorial content from private staging data.

Recovery-only tool: uses an existing BeautifulSoup installation. The generated
site and its normal builder have no third-party dependencies. Never commit input.
"""
import base64
import collections
import hashlib
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit, quote, parse_qs

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]).resolve()
data = json.loads(Path(sys.argv[2]).read_text())
audio_dir = Path(sys.argv[3]).resolve()
audio_dir.mkdir(parents=True, exist_ok=True)
media_dir = ROOT/'site/assets/media'
media_dir.mkdir(parents=True, exist_ok=True)
posts = {p['ID']:p for p in data['wp_posts']}
meta = collections.defaultdict(dict)
for row in data['wp_postmeta']:
    meta[row['post_id']][row['meta_key']] = row['meta_value']
terms = {t['term_id']:t for t in data['wp_terms']}
taxa = {t['term_taxonomy_id']:{**t, **terms[t['term_id']]} for t in data['wp_term_taxonomy']}
relations = collections.defaultdict(list)
for row in data['wp_term_relationships']:
    if row['term_taxonomy_id'] in taxa:
        relations[row['object_id']].append(taxa[row['term_taxonomy_id']])
page_slugs = {'quem-somos','jan-van-rijckenborgh','catharose-de-petri','antonin-gadal',
              'mikhail-naimy','johann-valentin-andrea','peter-huijs'}
selected = [p for p in posts.values() if p['post_type'] in {'post','product'} or
            p['post_type']=='page' and p['post_name'] in page_slugs]
routes = {p['ID']:('/produto/' if p['post_type']=='product' else '/')+p['post_name']+'/' for p in selected}
path_map = {urlsplit(p['guid']).path:routes[p['ID']] for p in selected}
path_map.update({route:route for route in routes.values()})
path_map.update({'/':'/','/home/':'/','/blog/':'/artigos/','/loja/':'/livros/',
                 '/autores/':'/livros/','/busca/':'/buscar/','/biblioteca-virtual/':'/revistas/',
                 '/categoria/ebooks/':'/livros/?tipo=ebook','/categoria/livros/':'/livros/',
                 '/categoria/revista_pentagrama/':'/revistas/'})
for tax in taxa.values():
    if tax['taxonomy']=='product_cat':
        if tax['name'].isdigit():
            path_map['/categoria/revista_pentagrama/'+tax['slug']+'/']='/revistas/?ano='+tax['name']
        elif tax['parent']=='126':
            path_map['/categoria/autores/'+tax['slug']+'/']='/livros/?autor='+quote(tax['name'])
    elif tax['taxonomy']=='category':
        path_map['/category/'+tax['slug']+'/']='/artigos/?tema='+quote(tax['name'])
assets, missing, dropped_links, audio_assets = {}, set(), set(), {}


def slug(text):
    s = unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:95] or 'arquivo'


def local_file(url):
    u = urlsplit(html.unescape(url.strip()))
    if u.netloc and not any(x in u.netloc.lower() for x in ['pentagrama.org.br','pentagrama.web2303.uni5.net']):
        return None
    rel = unquote(u.path).lstrip('/')
    if not rel or '..' in Path(rel).parts:
        return None
    p = (source/rel).resolve()
    if not p.is_relative_to(source):
        return None
    if not p.is_file():
        # Preserve exact filenames when a historical upload moved directory.
        candidates = list((source/'wp-content/uploads').rglob(Path(rel).name))
        if len(candidates)==1:
            p=candidates[0]
        else:
            return None
    return p


def asset(url):
    if url in assets:
        return assets[url]['url']
    p=local_file(url)
    if not p:
        missing.add(url)
        return None
    ext=p.suffix.lower()
    if ext not in {'.jpg','.jpeg','.png','.gif','.pdf','.mp3','.epub','.mobi'}:
        return None
    original=p
    if ext in {'.jpg','.jpeg','.png'} and p.stat().st_size>500000:
        candidates=[]
        for q in p.parent.glob(p.stem+'-*'+p.suffix):
            m=re.search(r'-(\d+)x(\d+)(?:-min)?$',q.stem)
            if m and 300<=int(m[1])<=1400 and q.stat().st_size<1500000:
                candidates.append(q)
        if candidates:
            p=max(candidates,key=lambda x:int(re.search(r'-(\d+)x',x.stem)[1]))
    b=p.read_bytes()
    if ext=='.pdf' and not b.startswith(b'%PDF-'):
        raise ValueError('Invalid PDF '+str(p.relative_to(source)))
    if ext in {'.jpg','.jpeg'} and not b.startswith(b'\xff\xd8'):
        raise ValueError('Invalid JPEG')
    if ext=='.png' and not b.startswith(b'\x89PNG'):
        raise ValueError('Invalid PNG')
    digest=hashlib.sha256(b).hexdigest()
    name=digest[:12]+'-'+slug(p.stem)+ext
    if ext=='.mp3':
        dest=audio_dir/name
        url_out='https://github.com/rosacruzaurea/pentagrama/releases/download/acervo-2018/'+name
        audio_assets[name]={'file':name,'bytes':len(b),'sha256':digest,'source':str(original.relative_to(source)),'url':url_out}
    else:
        dest=media_dir/name
        url_out='/assets/media/'+name
    if not dest.exists():
        shutil.copyfile(p,dest)
        dest.chmod(0o644)
    assets[url]={'url':url_out,'source':str(original.relative_to(source)),
                 'selected':str(p.relative_to(source)),'sha256':digest,'bytes':len(b)}
    return url_out


def link(url):
    url=html.unescape(url.strip())
    if url.startswith('#'):
        return None  # Original widget anchors are not stable after sanitization.
    u=urlsplit(url)
    if u.scheme not in {'','http','https'}:
        return None
    if Path(unquote(u.path)).suffix.lower() in {'.pdf','.mp3','.epub','.mobi','.png','.jpg','.jpeg'}:
        return asset(url)
    if not u.netloc or u.netloc.lower() in {'pentagrama.org.br','www.pentagrama.org.br','pentagrama.web2303.uni5.net'}:
        if parse_qs(u.query).get('p',[''])[0] in routes:
            return routes[parse_qs(u.query)['p'][0]]
        result=path_map.get(unquote(u.path).rstrip('/')+'/')
        if not result:
            dropped_links.add(url)
        return result
    # Old sales flows and contact endpoints are not revived in a historical preview.
    if any(x in u.netloc.lower() for x in ['amazon.','catavento','livrariacultura','saraiva']):
        return None
    return url.replace('http://','https://',1)


ALLOWED={'p','div','br','strong','b','em','i','u','s','blockquote','h2','h3','h4',
         'ul','ol','li','sup','sub','a','img','figure','figcaption','hr','table',
         'thead','tbody','tr','th','td','audio','source','small','span'}


def clean(raw):
    def decode(m):
        try:
            return unquote(base64.b64decode(m[1].strip(),validate=True).decode())
        except (ValueError,UnicodeError):
            return ''
    raw=re.sub(r'\[vc_raw_html\](.*?)\[/vc_raw_html\]',decode,raw,flags=re.S)
    raw=re.sub(r'\[audio[^\]]*mp3="([^"]+)"[^\]]*\](?:\[/audio\])?',
               lambda m:'<audio controls preload="none" src="'+html.escape(m[1],quote=True)+'"></audio>',raw)
    raw=re.sub(r'\[vc_single_image[^\]]*image="(\d+)"[^\]]*\]',
               lambda m:'<img src="/wp-content/uploads/'+html.escape(meta[m[1]].get('_wp_attached_file',''))+'" alt="">',raw)
    raw=re.sub(r'\[/?(?:vc_[a-z_]+|laborator_[a-z_]+|caption|embed|audio|siteorigin_widget)[^\]]*\]','',raw)
    soup=BeautifulSoup(raw,'html.parser')
    for comment in soup.find_all(string=lambda x:isinstance(x,Comment)):
        comment.extract()
    for tag in list(soup.find_all(True)):
        if tag.name is None or tag.attrs is None:
            continue
        if tag.name in {'script','style','form','input','button','object','embed','noscript','svg','link','meta'}:
            tag.decompose();continue
        if tag.name=='iframe':
            u=link(tag.get('src',''))
            if u:
                replacement=soup.new_tag('a',href=u)
                replacement.string='Abrir conteúdo externo'
                tag.replace_with(replacement)
            else:
                tag.decompose()
            continue
        if any('preco' in x for x in tag.get('class',[])):
            tag.decompose();continue
        if tag.name=='h1':
            tag.name='h2'
        if tag.name not in ALLOWED:
            tag.unwrap();continue
        attrs={}
        if tag.name=='a':
            original_url=tag.get('href','')
            u=link(original_url)
            if not u:
                if original_url in missing:
                    tag.replace_with('Arquivo não localizado no backup.')
                else:
                    tag.unwrap()
                continue
            attrs={'href':u}
            if u.startswith('https://'):
                attrs['rel']='noopener noreferrer'
        if tag.name in {'img','audio','source'}:
            u=asset(tag.get('src',''))
            if not u:
                tag.decompose();continue
            attrs={'src':u}
            if tag.name=='img':
                attrs.update({'alt':tag.get('alt',''),'loading':'lazy','decoding':'async'})
            if tag.name=='audio':
                attrs.update({'controls':'','preload':'none','aria-label':'Ouvir este texto'})
        tag.attrs=attrs
    # Legacy inline spans and layout wrappers have no semantics worth retaining.
    for tag in list(soup.find_all('span')):
        tag.unwrap()
    for tag in reversed(soup.find_all(['div','p','h2','h3'])):
        if not tag.get_text(strip=True) and not tag.find(['img','audio','br']):
            tag.decompose()
    return str(soup).strip()


entries=[]
for p in selected:
    pt=p['post_type']; ts=relations[p['ID']]
    cats=[t['name'] for t in ts if t['taxonomy']=='category']
    pcats=[t['slug'] for t in ts if t['taxonomy']=='product_cat']
    kind='artigo' if pt=='post' else 'pagina' if pt=='page' else 'revista' if 'revista_pentagrama' in pcats else 'livro'
    authors=[t['name'] for t in ts if t['taxonomy']=='product_cat' and t['parent']=='126']
    years=[t['name'] for t in ts if t['taxonomy']=='product_cat' and re.fullmatch(r'\d{4}',t['name'])]
    raw=p['post_content'] if pt!='product' else p['post_excerpt']+'\n'+p['post_content']
    body=clean(raw)
    thumb=meta[p['ID']].get('_thumbnail_id')
    cover=asset('/wp-content/uploads/'+meta[thumb]['_wp_attached_file']) if thumb and meta[thumb].get('_wp_attached_file') else None
    text=BeautifulSoup(body,'html.parser').get_text(' ',strip=True)
    entries.append({'id':p['ID'],'type':kind,'title':html.unescape(p['post_title']),
        'slug':p['post_name'],'path':routes[p['ID']],'date':p['post_date'][:10],
        'categories':cats,'authors':authors,'year':years[0] if years else '',
        'ebook':bool({'ebooks','e-books-home'}&set(pcats)),'cover':cover,'html':body,
        'summary':text[:220].rsplit(' ',1)[0]+('…' if len(text)>220 else ''),
        'words':len(text.split()),'source':'wordpress-2018-12-03'})
logo=asset('/wp-content/uploads/2016/03/logobookstore.png')
(ROOT/'content/site.json').write_text(json.dumps({'source_date':'2018-12-03','logo':logo,'entries':entries},ensure_ascii=False,indent=2)+'\n')
manifest={'files':list({v['url']:v for v in assets.values()}.values()),'audio':list(audio_assets.values()),
          'missing_files':sorted(missing),'unmapped_legacy_links':sorted(dropped_links)}
(ROOT/'content/media-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'entries':dict(collections.Counter(x['type'] for x in entries)),
 'site_media_bytes':sum(p.stat().st_size for p in media_dir.iterdir()),'audio_files':len(audio_assets),
 'audio_bytes':sum(x['bytes'] for x in audio_assets.values()),'missing':len(missing)},ensure_ascii=False))
