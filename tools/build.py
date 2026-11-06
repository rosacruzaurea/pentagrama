"""Build dependency-free HTML/CSS/JS. Run from any directory with Python 3.12+."""
import html
import json
import re
from pathlib import Path
from site_config import BASE, NOINDEX
from blog import render_blog

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=json.loads((ROOT/'content/site.json').read_text())
ENTRIES=DATA['entries']
H=lambda x:html.escape(str(x),quote=True)
U=lambda p: BASE+p if p.startswith('/') else p
BOOKS=sorted([x for x in ENTRIES if x['type']=='livro'],key=lambda x:(x.get('priority',999),x['title'].casefold()))
MAGAZINES=sorted([x for x in ENTRIES if x['type']=='revista'],key=lambda x:(x['year'],int(re.search(r'Número\s+(\d+)',x['title'])[1]) if re.search(r'Número\s+(\d+)',x['title']) else 0),reverse=True)


def date(s):
    y,m,d=s.split('-')
    return f'{d}.{m}.{y}'


def picture(e,cls='',eager=False):
    if e.get('cover'):
        return f'<img class="{cls}" src="{H(U(e["cover"]))}" alt="{H(e["title"])}" loading="{"eager" if eager else "lazy"}" decoding="async">'
    return f'<div class="cover-fallback {cls}" aria-hidden="true"><span>Pentagrama</span><small>{H(e.get("year") or "Acervo")}</small></div>'


def shell(title,body,section='',description='',path='/'):
    nav=''.join(f'<a href="{BASE}/{p+chr(47) if p else ''}"'+(' aria-current="page"' if section==p else '')+f'>{t}</a>' for p,t in [('', 'Home'),('livros','Livros'),('revistas','Revistas'),('quem-somos','Quem somos'),('contato','Contato'),('blog','Blog')])
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; media-src 'self' https://github.com https://*.githubusercontent.com; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'">
<meta name="referrer" content="strict-origin-when-cross-origin"><meta name="robots" content="{'noindex,follow' if NOINDEX else 'index,follow'}">
<title>{H(title)} | Pentagrama</title><meta name="description" content="{H(description or 'Artigos, livros e revistas do acervo de Pentagrama Publicações.')}">
<meta property="og:title" content="{H(title)} | Pentagrama"><meta property="og:type" content="website">
<link rel="stylesheet" href="{BASE}/assets/styles.css"><script defer src="{BASE}/assets/app.js"></script></head>
<body><a class="skip" href="#conteudo">Pular para o conteúdo</a>
<div class="contact-bar"><div class="wrap"><a href="mailto:livros@pentagrama.org.br">livros@pentagrama.org.br</a><span><a href="https://www.facebook.com/pentagramapublicacoes/">Facebook</a><a href="https://www.instagram.com/pentagramapublicacoes/">Instagram</a></span></div></div>
<header class="site-header wrap"><a class="brand" href="{BASE}/" aria-label="Pentagrama, início"><img src="{H(U(DATA['logo']))}" width="456" height="99" alt="Pentagrama Publicações"></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="menu">Menu <span aria-hidden="true">☰</span></button><nav id="menu" aria-label="Navegação principal">{nav}<a class="search-link" href="{BASE}/buscar/">Buscar <span aria-hidden="true">⌕</span></a></nav></header>
<main id="conteudo">{body}</main>
<footer><div class="wrap footer-grid"><div><a class="footer-brand" href="{BASE}/">Pentagrama<span>publicações</span></a><p>Literatura gnóstica, hermética e rosa-cruz.</p></div><div><p class="eyebrow">EXPLORE O ACERVO</p><a href="{BASE}/blog/">Artigos</a><a href="{BASE}/livros/">Livros e e-books</a><a href="{BASE}/revistas/">Revista Pentagrama</a></div><div><p class="eyebrow">CONTATO</p><a href="mailto:livros@pentagrama.org.br">livros@pentagrama.org.br</a></div></div><div class="wrap footer-bottom">Pentagrama Publicações </div></footer>
</body></html>'''


def write(path,title,body,section='',description=''):
    p=SITE/path.strip('/')/'index.html' if path!='404.html' else SITE/'404.html'
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(shell(title,body,section,description,path))


def card(e,filterable=False):
    kind=e['type'];book=kind in {'livro','revista'}
    topic=(e['categories'][0] if e['categories'] else 'Artigo') if kind=='artigo' else ('Revista · '+e['year'] if kind=='revista' else 'E-book gratuito' if e['ebook'] else 'Livro')
    attrs=''
    if filterable:
        search=' '.join(' '.join([e['title'],e['summary'],*e['authors'],*e['categories'],e['year']]).split())
        attrs=f' data-item data-search="{H(search)}" data-tema="{H(json.dumps(e["categories"],ensure_ascii=False))}" data-autor="{H(json.dumps(e["authors"],ensure_ascii=False))}" data-ano="{e["year"]}" data-tipo="{"ebook" if e["ebook"] else kind}"'
    return f'''<article class="card {"book-card" if book else "article-card"}"{attrs}><a class="card-image" href="{U(e['path'])}" tabindex="-1" aria-hidden="true">{picture(e)}</a><div class="card-copy"><p class="eyebrow">{H(topic)}</p><h3><a href="{U(e['path'])}">{H(e['title'])}</a></h3>{'<p class="card-author">'+H(', '.join(e['authors']))+'</p>' if e['authors'] else ''}{'<p class="card-summary">'+H(' '.join(e['summary'].split()))+'</p><p class="card-date">'+date(e['date'])+'</p>' if kind=='artigo' else ''}</div></article>'''


def listing(path,title,intro,items,kind):
    filters=''
    if kind in {'artigos','blog'}:
        values=sorted({t for e in items for t in e['categories']})
        filters=f'<label>Tema<select name="tema"><option value="">Todos os temas</option>'+''.join(f'<option>{H(t)}</option>' for t in values)+'</select></label>'
    elif kind=='livros':
        values=sorted({t for e in items for t in e['authors']})
        filters='<label>Autor<select name="autor"><option value="">Todos os autores</option>'+''.join(f'<option>{H(t)}</option>' for t in values)+'</select></label><label>Formato<select name="tipo"><option value="">Todos os livros</option><option value="ebook">E-books gratuitos</option></select></label>'
    elif kind=='revistas':
        values=sorted({e['year'] for e in items if e['year']},reverse=True)
        filters='<label>Ano<select name="ano"><option value="">Todos os anos</option>'+''.join(f'<option>{H(t)}</option>' for t in values)+'</select></label>'
    content=f'''<section class="page-head wrap"><a class="back-link" href="{BASE}/">Início /</a><p class="eyebrow">{len(items)} PUBLICAÇÕES NO ACERVO</p><h1>{title}</h1><p class="lede">{intro}</p></section>
<section class="wrap catalog" data-catalog><form class="filters" role="search"><label class="search-field">Buscar no acervo<input type="search" name="q" placeholder="Título, tema ou autor" autocomplete="off"></label>{filters}<button type="reset" class="button button-light">Limpar filtros</button></form>
<noscript><p>As publicações estão listadas abaixo. Para usar a busca e os filtros, ative o JavaScript no navegador.</p></noscript><p class="result-count" role="status" aria-live="polite" data-count>{len(items)} publicações</p>
<div class="card-grid {"books-grid" if kind in ["livros","revistas"] else ""}">{''.join(card(e,True) for e in items)}</div>
<div class="empty" data-empty hidden><h2>Nenhuma publicação encontrada</h2><p>Tente outro termo ou limpe os filtros.</p></div><button class="button more" type="button" data-more hidden>Mostrar mais publicações</button></section>'''
    write(path,title,content,kind)


# Home structure, headings, palette and typography from the archived 2026 site.
modern=sorted([e for e in BOOKS if e.get('source')=='web-2026'],key=lambda e:e.get('priority',999))
featured_books=[e for e in modern if e['ebook']][:6]
new_mag=next(e for e in MAGAZINES if e['year']=='2025' and '2'==re.search(r'Número\s+(\d+)',e['title'])[1])
home=f'''<h1 class="sr-only">Pentagrama Publicações</h1><section class="hero"><img src="{U(DATA['hero'])}" alt="Fênix, pássaro de fogo, sobre fundo azul" width="1687" height="439" fetchpriority="high"><div class="hero-caption wrap"><p>A Fênix, ou pássaro de fogo que renasce das cinzas, nos traz o conceito de imortalidade e é o símbolo do mistério solar egípcio Ísis Osíris e Hórus.</p></div></section>
<section class="wrap home-section"><div class="section-heading"><div><h2>e-Books em destaque</h2><p class="section-subtitle">gratuitos</p></div><a class="button button-light" href="{BASE}/livros/?tipo=ebook">Ver Todos</a></div><div class="card-grid home-books">{''.join(card(e) for e in featured_books)}</div></section>
<section class="blog-band"><div class="wrap blog-feature"><div class="blog-title"><h2>Blog</h2><a class="logon-word" href="{BASE}/blog/">LOGON</a></div><div><p>Você se encontra fazendo perguntas fundamentais sobre a vida?</p><p>Você costuma se perguntar: qual o sentido da minha existência?</p><p>Você acredita que deve haver algo além das trivialidades do dia-a-dia, que justifique a sua vida?</p><p>Se sim, então LOGON pode ser para você.</p><a class="text-link" href="{BASE}/blog/">Visite o Blog →</a></div></div></section>
<section class="wrap home-section"><div class="section-heading"><h2>Lançamentos</h2><a class="button button-light" href="{BASE}/livros/">Ver Todos</a></div><div class="card-grid books-grid">{''.join(card(e) for e in modern[:4])}</div></section>
<section class="wrap magazine-feature"><a class="magazine-cover" href="{U(new_mag['path'])}">{picture(new_mag)}</a><div><h2>Revista 2025 | Ano 1 Número 2</h2><p>A Revista Pentagrama é a revista trimestral do Lectorium Rosicrucianum, que reúne seleções de serviços templários proferidos em seus templos no Brasil.</p><p>A Revista constitui um espaço de encontro entre reflexão, autoconhecimento e vivência espiritual. Mais que apresentar ideias, buscamos oferecer ao leitor a oportunidade de voltar-se para si mesmo e conectar-se com um horizonte mais amplo, onde pensamentos, sentimentos e impulso de agir se harmonizam.</p><p>Que esta publicação inspire cada um, de forma livre e consciente, a entrar no fluxo dessa transformação, permitindo que a Luz interior se manifeste e encontre expressão no mundo.</p><a class="button" href="{U(new_mag['path'])}">Ver revista</a></div></section>
<section class="books-band"><div class="wrap home-section"><div class="section-heading"><h2>Mais Lidos</h2><a class="text-link" href="{BASE}/livros/">Ver Todos →</a></div><div class="card-grid books-grid">{''.join(card(e) for e in modern[:4])}</div></div></section>'''
write('/','Pentagrama Publicações',home)
write('/blog/', 'Blog', render_blog(ROOT, BASE, H), 'blog', 'Artigos LOGON de 2026 e o acervo de Pentagrama Publicações.')
listing('/livros/','Livros','Obras da tradição gnóstica, hermética e rosa-cruz. Sinopses, autores e e-books disponíveis no acervo.',BOOKS,'livros')
listing('/revistas/','Revista Pentagrama','As edições recentes e o acervo histórico da Revista Pentagrama. Selecione um ano ou encontre um tema.',MAGAZINES,'revistas')
listing('/buscar/','Encontre sua próxima leitura','Pesquise títulos, temas e autores em todo o acervo.',BOOKS+MAGAZINES,'buscar')

for e in ENTRIES:
    kind=e['type']; book=kind in {'livro','revista'}
    parent='/artigos/' if kind=='artigo' else '/revistas/' if kind=='revista' else '/livros/' if book else '/'
    label='Artigos' if kind=='artigo' else 'Revistas' if kind=='revista' else 'Livros' if book else 'Início'
    body=re.sub(r'(?P<a>(?:href|src)=")(?P<p>/[^\"]*)',lambda m:m['a']+BASE+m['p'],e['html'])
    title=H(e['title'])
    metadata=(date(e['date'])+' · '+str(max(1,round(e['words']/200)))+' min de leitura') if kind=='artigo' else H(', '.join(e['authors']) or e['year'])
    if book:
        content=f'<div class="wrap detail-top"><a class="back-link" href="{BASE+parent}">← {label}</a></div><article class="wrap book-detail"><div class="book-cover">{picture(e,eager=True)}</div><div><p class="eyebrow">'+('REVISTA PENTAGRAMA' if kind=='revista' else 'BIBLIOTECA PENTAGRAMA')+f'</p><h1>{title}</h1><p class="byline">{metadata}</p><div class="prose">{body or "<p>Consulte as informações desta publicação.</p>"}</div></div></article>'
    else:
        content=f'<div class="wrap detail-top"><a class="back-link" href="{BASE+parent}">← {label}</a></div><article class="reading"><header class="reading-head"><p class="eyebrow">{H(e["categories"][0] if e["categories"] else "PENTAGRAMA PUBLICAÇÕES")}</p><h1>{title}</h1><p class="byline">{metadata}</p></header>'
        if e.get('cover'):
            content+=f'<div class="reading-cover">{picture(e,eager=True)}</div>'
        content+=f'<div class="prose">{body}</div></article>'
    related=[x for x in (MAGAZINES if kind=='revista' else BOOKS) if x['id']!=e['id']][:3]
    content+=f'<section class="wrap home-section related"><div class="section-heading"><h2>Continue a leitura</h2><a class="text-link" href="{BASE+parent}">Ver {label.lower()} ↗</a></div><div class="card-grid">'+''.join(card(x) for x in related)+'</div></section>'
    write(e['path'],e['title'],content,parent.strip('/'),e['summary'])
    for alias in e.get('aliases',[]):
        write(alias,e['title'],content,parent.strip('/'),e['summary'])

# Retire the reconstruction-only page from existing generated artifacts.
(SITE/'sobre-o-acervo'/'index.html').unlink(missing_ok=True)
write('/contato/','Contato',f'<article class="reading about"><h1>Contato</h1><div class="prose"><p>Pentagrama Publicações</p><p><a href="mailto:livros@pentagrama.org.br">livros@pentagrama.org.br</a></p><p><a href="https://www.facebook.com/pentagramapublicacoes/">Facebook</a> · <a href="https://www.instagram.com/pentagramapublicacoes/">Instagram</a></p><p>Entre em contato pelo e-mail acima.</p></div></article>','contato')
write('404.html','Página não encontrada',f'<section class="reading about"><p class="eyebrow">PENTAGRAMA</p><h1>Esta página não está no acervo.</h1><p>O endereço pode ter mudado. Encontre a publicação pela busca ou volte ao início.</p><a class="button" href="{BASE}/buscar/">Buscar no acervo</a> <a href="{BASE}/">Voltar ao início</a></section>')
(SITE/'.nojekyll').write_text('')
(SITE/'robots.txt').write_text('User-agent: *\n' + ('Disallow: /\n' if NOINDEX else 'Allow: /\n'))
print(json.dumps({'pages':len(list(SITE.rglob('*.html'))),'books':len(BOOKS),'magazines':len(MAGAZINES),'base':BASE}))
