"""Merge verified public catalogs with the sanitized backup and selected local books.

One-time recovery tool: input folders stay outside the public repository.
Usage: python3 tools/merge_2026.py ARCHIVE_FOLDER WORKSPACE BACKUP_ROOT
"""
import copy, hashlib, html, json, re, shutil, subprocess, sys, unicodedata, zipfile
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
archive,workspace,backup=map(Path,sys.argv[1:4])
site=ROOT/'site'; media=site/'assets/media'
data=json.loads((ROOT/'content/site-2018.json').read_text())
entries=data['entries']; evidence=[]
H=lambda s:html.escape(str(s),quote=True)
def norm(s):
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def slug(s):
    return re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-')
def copy_asset(p,name=None,source=''):
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    dest=media/(digest[:12]+'-'+(name or p.name))
    if not dest.exists():shutil.copyfile(p,dest)
    dest.chmod(0o644)
    evidence.append({'file':dest.name,'sha256':digest,'bytes':dest.stat().st_size,'origin':source or p.name})
    return '/assets/media/'+dest.name
def new_entry(title,path,kind='livro'):
    e={'id':'recovered-'+slug(title),'type':kind,'title':title,'slug':path.strip('/').split('/')[-1],
       'path':path,'date':'','categories':[],'authors':[],'year':'','ebook':False,'cover':None,
       'html':'','summary':'','words':0,'source':'local-editorial'}
    entries.append(e);return e
def issue(title):
    m=re.search(r'(?:Número|número|Nº)\s*(\d+)',title)
    return m[1] if m else ''
def pdf_cover(p,name):
    target=media/(name+'-capa')
    if not target.with_suffix('.jpg').exists():
        crop=['-x','375','-y','20','-W','366','-H','510'] if name=='revista-2025-2' else []
        subprocess.run(['pdftoppm','-f','1','-l','1','-scale-to','750',*crop,'-singlefile','-jpeg','-jpegopt','quality=85',str(p),str(target)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return '/assets/media/'+target.with_suffix('.jpg').name

catalog=json.loads((archive/'CATALOGOS-2026.json').read_text())
descriptions={norm(e['title']):e for e in json.loads((archive/'CONTEUDO-PUBLICO.json').read_text())['books']}
for kind,collection in [('livro','livros'),('revista','revistas')]:
    for priority,item in enumerate(catalog[collection]['items']):
        title=item['title'];path=urlsplit(item['url']).path
        matches=[e for e in entries if e['type']==kind and norm(e['title'])==norm(title)]
        if kind=='revista':
            year=re.search(r'20\d\d|19\d\d',title)
            matches=[e for e in entries if e['type']==kind and year and e['year']==year[0] and issue(e['title'])==issue(title)]
        e=next((e for e in matches if e['ebook']),matches[0] if matches else None)
        if e:
            e.setdefault('aliases',[]).append(e['path']);e['backup_title']=e['title']
        else:e=new_entry(title,path,kind)
        e.update(title=title,path=path,priority=priority,source='web-2026',source_url=item['source'],original_cover_url=item['cover_url'])
        if kind=='revista':
            year=re.search(r'20\d\d|19\d\d',title)
            if year:e['year']=year[0]
        desc=descriptions.get(norm(title))
        if desc:
            e['html']=''.join('<p>'+H(p.strip())+'</p>' for p in desc['description'].split('\n') if p.strip())
            e['summary']=' '.join(desc['description'].split())[:230]
            e['source_url']=desc['source']
        if not e['html']:
            e['html']='<p>Obra presente no catálogo de Pentagrama Publicações preservado em 2026.</p>'
            e['summary']='Obra do catálogo de Pentagrama Publicações.'
        if not e['cover']:
            matches=list((backup/'wp-content/uploads').rglob(Path(urlsplit(item['cover_url']).path).name))
            if len(matches)==1:e['cover']=copy_asset(matches[0],source='backup-2018: '+str(matches[0].relative_to(backup)))

# Public 2025 magazine PDFs recovered from archived official URLs.
for number in (1,2):
    p=archive/'recuperado'/f'revista-pentagrama-2025-ano1-numero{number}.pdf'
    e=next(e for e in entries if e['type']=='revista' and e['year']=='2025' and issue(e['title'])==str(number))
    link=copy_asset(p,source='Wayback: PDF oficial Revista Pentagrama 2025, número '+str(number))
    e['html']=f'<p>Revista Pentagrama, ano 1, número {number}, 2025.</p><p><a href="{link}">Ler ou baixar a revista completa (PDF)</a></p>'
    e['cover']=pdf_cover(p,f'revista-2025-{number}')
    e['summary']=f'Revista Pentagrama, ano 1, número {number}, 2025.'

# Title/edition checked against front matter, not inferred from a filename alone.
local_books=[
 ('Rosacruz Áurea: Uma Escola Iniciática para o século XXI','rosacruz-escola-iniciatica.pdf','2025'),
 ('Caos Exterior, Despertar Interior','downloads/caos-exterior-despertar-interior.pdf','2021'),
 ('Iniciação e libertação','memory/estudo/pdfs/iniciacao-e-libertacao.epub','2024'),
 ('Inspirações para um novo tempo','memory/estudo/pdfs/inspiracoes-para-um-novo-tempo.epub','2023'),
 ('A Busca da Nova Consciência','downloads/busca-nova-consciencia.pdf','2020'),
 ('Saúde e Espiritualidade: A Cura','downloads/saude-espiritualidade-cura.pdf','2018'),
 ('Os Sete Raios do Espírito e a transformação da vida humana','sete-raios-espirito.pdf','2016'),
 ('A grande revolução','memory/estudo/classicas/grande-revolucao.pdf',''),
 ('A Gnosis Chinesa','memory/estudo/classicas/livro-pentagrama-7416.pdf',''),
 ('O mistério iniciático cristão: Dei gloria intacta','memory/estudo/classicas/livro-pentagrama-7464.pdf',''),
 ('Filosofia elementar da Rosacruz moderna','memory/estudo/classicas/livro-pentagrama-7497.pdf','2003'),
 ('A Gnose em sua atual manifestação','memory/estudo/classicas/livro-pentagrama-7504.pdf',''),
 ('O Verbo Vivente','memory/estudo/classicas/livro-pentagrama-7604.pdf',''),
 ('Os mistérios gnósticos da Pistis Sophia','memory/estudo/classicas/livro-pentagrama-8681.pdf',''),
 ('A veste-de-luz do novo homem','memory/estudo/classicas/livro-pentagrama-8698.pdf',''),
 ('O chamado da Fraternidade da Rosa-Cruz','memory/estudo/classicas/livro-pentagrama-8724.pdf',''),
 ('A luz do mundo','memory/estudo/pdfs/a-luz-do-mundo.pdf','2012'),
 ('Transfiguração','memory/estudo/pdfs/transfiguracao.pdf','2003'),
 ('A Tríplice Aliança da Luz','memory/estudo/pdfs/triplice-alianca-da-luz.pdf',''),
 ('O novo homem','producao/livros-classicos/o-novo-homem.pdf','2016'),
 ('A Confessio da Fraternidade da Rosacruz','producao/livros-classicos/confessio-fraternitatis.pdf',''),
]
local_report=[]
for title,relative,year in local_books:
    p=workspace/relative
    matches=[e for e in entries if e['type']=='livro' and norm(e['title'])==norm(title)]
    if not matches:matches=[new_entry(title,'/livros/'+slug(title)+'/')]
    missing=[e for e in matches if not re.search(r'href="[^\"]+\.(?:pdf|epub)',e['html'])]
    if not missing:continue
    url=copy_asset(p,slug(title)+p.suffix,source='Biblioteca local autorizada: '+title)
    cover=None
    if p.suffix=='.epub':
        with zipfile.ZipFile(p) as z:
            opf=next(n for n in z.namelist() if n.endswith('.opf'))
            root=ET.fromstring(z.read(opf)); ns={'o':'http://www.idpf.org/2007/opf'}
            coverid=next((x.get('content') for x in root.findall('.//o:meta',ns) if x.get('name')=='cover'),None)
            item=next((x for x in root.findall('.//o:item',ns) if x.get('id')==coverid or 'cover-image' in x.get('properties','')),None)
            if item is not None:
                imagepath=str(Path(opf).parent/item.get('href'));imagebytes=z.read(imagepath)
                dest=media/(slug(title)+'-capa'+Path(imagepath).suffix)
                dest.write_bytes(imagebytes);cover='/assets/media/'+dest.name
    for e in missing:
        e['html']+=f'<p><a href="{url}">Baixar livro ({p.suffix[1:].upper()})</a></p>'
        if year:e['download_edition']=year
        e['ebook']=True;e['local_complement']=True
        if not e['year']:e['year']=year
        if cover:e['cover']=cover
        elif not e['cover']:e['cover']=pdf_cover(p,slug(title))
        if not e['summary']:e['summary']='Edição de Pentagrama Publicações, disponível para leitura.'
    local_report.append({'title':title,'format':p.suffix[1:],'edition':year or 'ver ficha editorial do arquivo','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})

# One additional supplied editorial volume survives as its interior PDF, without cover.
interiors=list((workspace.parent/'media/inbound').glob('miolo_I_Entre_o_sile_ncio_e_a_luz_2---*.pdf'))
if len(interiors)==1:
    p=interiors[0];title='Entre o silêncio e a luz: reflexões de uma jornada espiritual'
    e=new_entry(title,'/livros/entre-o-silencio-e-a-luz/')
    url=copy_asset(p,'entre-o-silencio-e-a-luz-miolo.pdf',source='Biblioteca local autorizada: '+title)
    e.update(ebook=True,local_complement=True,summary='Miolo do livro, preservado no acervo local.',
             html=f'<p>Volume de Pentagrama Publicações preservado no acervo local. O arquivo disponível contém o miolo do livro, sem a capa.</p><p><a href="{url}">Baixar miolo do livro (PDF)</a></p>')
    local_report.append({'title':title,'format':'pdf','edition':'Rosto: 2025; CIP: 2024. Divergência preservada, sem inferir correção. Miolo sem capa.','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})

# Consolidate duplicate print/e-book catalog cards, retaining every historical route.
bytitle={}; consolidated=[]
for e in sorted(entries,key=lambda e:(e.get('priority',999),not e.get('ebook',False))):
    key=(e['type'],norm(e['title']))
    if e['type']!='livro' or key not in bytitle:
        bytitle[key]=e;consolidated.append(e);continue
    target=bytitle[key]
    target.setdefault('aliases',[]).extend([e['path'],*e.get('aliases',[])])
    target.setdefault('merged_backup_ids',[]).append(e['id'])
    if not target.get('cover'):target['cover']=e.get('cover')
    # Preserve unique download URLs from the alternate historical card.
    for m in re.finditer(r'<a href="([^\"]+\.(?:pdf|epub|mobi))"[^>]*>(.*?)</a>',e['html'],re.S):
        if m[1] not in target['html']:target['html']+='<p>'+m[0]+'</p>'
data['entries']=consolidated
data['logo']=copy_asset(archive/'recuperado/pentagrama-logo-2019.png',source='Logo referido no site2026; binário recuperado do arquivo web')
data['hero']=copy_asset(backup/'wp-content/uploads/2016/05/banner_2-1687x439.png',source='Backup2018: banner com mesmo nome e composição da referência2026')
data['source_priority']=['web-2026','wordpress-2018-12-03','local-editorial']
data['reference_home']='https://web.archive.org/web/20260710195647/https://pentagrama.org.br/'
for e in data['entries']:
    if e['type']=='livro':
        e['ebook']=bool(re.search(r'href="/assets/[^\"]+\.(?:pdf|epub|mobi)"',e['html']))
    e['words']=len(re.sub('<[^>]+>',' ',e['html']).split())
    if e.get('aliases'):e['aliases']=sorted(set(e['aliases'])-{e['path']})
(ROOT/'content/site.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(ROOT/'content/recovery-2026.json').write_text(json.dumps({'assets':evidence,'local_books':local_report,'catalogs':catalog},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'entries':len(consolidated),'local_books_added':len(local_report),'modern_catalog_items':40}))
