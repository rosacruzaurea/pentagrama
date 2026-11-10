"""Canonical metadata and discovery files from the published editorial inventory."""
from content_search import ENGINE_ID
import html
import json
import re
from html.parser import HTMLParser
from urllib.parse import quote, urlsplit
from xml.etree import ElementTree as ET

ORIGIN = 'https://pentagrama.org.br'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', NS)


# Catalogue names with unambiguous entity types. Unknown/traditional attributions
# stay visible in the catalogue but are not asserted as people in structured data.
AUTHOR_TYPES = {
    'Lectorium Rosicrucianum': 'Organization',
    'Jan van Rijckenborgh': 'Person', 'Catharose de Petri': 'Person',
    'Antonin Gadal': 'Person', 'J. A. Comenius': 'Person',
    'Gideon Jasper Ouseley': 'Person', 'Francisco Casanueva Freijo': 'Person',
    'Klaus Bielau': 'Person', 'Benita Kleiberg': 'Person',
    'J L G de Hartog Meyjes': 'Person', 'Karl von Eckartshausen': 'Person',
    'Mikhail Naimy': 'Person', 'Peter Huijs': 'Person',
}


def structured_authors(entry):
    names = entry.get('authors', [])
    # Do not silently drop one member of a coauthorship with an unknown type.
    if not names or any(name not in AUTHOR_TYPES for name in names):
        return []
    return [{'@type': AUTHOR_TYPES[name], 'name': name} for name in names]


def absolute(path):
    return ORIGIN + quote('/' + path.lstrip('/'), safe='/%-._~')


def plain(text):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', text)).split())


def description(text):
    text = plain(text)
    return text if len(text) <= 170 else text[:167].rsplit(' ', 1)[0] + '…'


class Downloads(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        u = urlsplit(href)
        if tag == 'a' and not u.scheme and not u.netloc and u.path.startswith('/assets/') and u.path.lower().endswith('.pdf'):
            self.paths.add(u.path)


def pdf_paths(entries):
    parser = Downloads()
    for entry in entries:
        parser.feed(entry['html'])
    return sorted(parser.paths)


def metadata(title, text, path, canonical, entry, logo, noindex):
    h = lambda value: html.escape(str(value), quote=True)
    url = absolute(canonical)
    title = title if title == 'Pentagrama Publicações' else title + ' | Pentagrama'
    if entry and not plain(text).casefold().startswith(entry['title'].casefold()):
        text = entry['title'] + '. ' + text
    desc = description(text or 'Livros, e-books gratuitos e revistas sobre a tradição gnóstica, hermética e rosa-cruz. Conheça o acervo de Pentagrama Publicações.')
    image = absolute(entry.get('cover') or logo) if entry else absolute(logo)
    hidden = noindex or path in {'404.html', '/buscar/'}
    head = f'<meta name="robots" content="{"noindex,follow" if hidden else "index,follow"}"><title>{h(title)}</title><meta name="description" content="{h(desc)}">'
    if path != '404.html':
        head += f'<link rel="canonical" href="{h(url)}">'
    head += f'<meta property="og:site_name" content="Pentagrama Publicações"><meta property="og:locale" content="pt_BR"><meta property="og:type" content="website"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{h(url)}"><meta property="og:image" content="{h(image)}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{h(title)}"><meta name="twitter:description" content="{h(desc)}"><meta name="twitter:image" content="{h(image)}">'
    if path == '404.html':
        return head
    graph = [
        {'@type': 'Organization', '@id': ORIGIN + '/#organization', 'name': 'Pentagrama Publicações', 'url': ORIGIN + '/', 'logo': absolute(logo)},
        {'@type': 'WebSite', '@id': ORIGIN + '/#website', 'url': ORIGIN + '/', 'name': 'Pentagrama Publicações', 'inLanguage': 'pt-BR', 'publisher': {'@id': ORIGIN + '/#organization'}},
        {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'pt-BR', 'isPartOf': {'@id': ORIGIN + '/#website'}}
    ]
    if entry and entry['type'] in {'livro', 'revista'}:
        work = {'@type': 'Book' if entry['type'] == 'livro' else 'PublicationIssue', '@id': url + '#publication', 'name': entry['title'], 'url': url, 'description': desc}
        authors = structured_authors(entry) if entry['type'] == 'livro' else []
        if authors:
            work['author'] = authors
        if entry.get('cover'):
            work['image'] = absolute(entry['cover'])
        # Do not turn unverified dates, prices or ratings into structured claims.
        files = pdf_paths([entry])
        if files:
            work['encoding'] = [{'@type': 'MediaObject', 'contentUrl': absolute(p), 'encodingFormat': 'application/pdf'} for p in files]
        graph[2]['mainEntity'] = {'@id': work['@id']}
        graph.append(work)
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return head + '<script type="application/ld+json">' + data + '</script>'


def write_sitemaps(site, routes, entries):
    def save(name, paths):
        root = ET.Element(f'{{{NS}}}urlset')
        for path in sorted(set(paths)):
            ET.SubElement(ET.SubElement(root, f'{{{NS}}}url'), f'{{{NS}}}loc').text = absolute(path)
        ET.ElementTree(root).write(site / name, encoding='utf-8', xml_declaration=True)
    save('sitemap-pages.xml', [p for p in routes if p not in {'404.html', '/buscar/'}])
    save('sitemap-pdfs.xml', pdf_paths(entries))
    root = ET.Element(f'{{{NS}}}sitemapindex')
    for name in ['sitemap-pages.xml', 'sitemap-pdfs.xml']:
        ET.SubElement(ET.SubElement(root, f'{{{NS}}}sitemap'), f'{{{NS}}}loc').text = absolute('/' + name)
    ET.ElementTree(root).write(site / 'sitemap.xml', encoding='utf-8', xml_declaration=True)


def google_search():
    engine = html.escape(ENGINE_ID, quote=True)
    return f'''<details class="google-search" data-engine-id="{engine}"><summary>Buscar no conteúdo</summary><p>Pesquise no texto das páginas e dos PDFs indexados. Os filtros do acervo continuam disponíveis acima.</p>
<form action="https://www.google.com/search" method="get" target="_blank" rel="noopener noreferrer" role="search" aria-label="Buscar no conteúdo">
<input type="hidden" name="as_sitesearch" value="pentagrama.org.br"><label class="search-field">O que você procura?<input type="search" name="q" required maxlength="300" placeholder="Ex.: alquimia, alma ou nome do autor"></label><label>Pesquisar em<select name="as_filetype"><option value="">Páginas e documentos</option><option value="pdf">Somente PDFs</option></select></label><button class="button" type="submit">Buscar no conteúdo</button></form>
<p class="google-search-note" data-search-note>A busca abre em outra aba e envia os termos a um serviço externo somente ao pesquisar. Nem todo o acervo pode estar indexado.</p>
<p role="status" aria-live="polite" data-content-status></p>
<a data-content-fallback hidden target="_blank" rel="noopener noreferrer">Abrir resultados em outra aba</a>
<div data-content-results hidden></div></details>'''
