"""Blog editorial: reference structure plus a reviewed static LOGON selection."""
import json
from datetime import date as Date
from urllib.parse import urlsplit


def render_blog(root, base, escape):
    data = json.loads((root / 'content/blog-logon.json').read_text())
    entries = data['entries']
    seen = set()
    for e in entries:
        u = urlsplit(e['url'])
        assert u.scheme == 'https' and u.netloc == 'logon.media' and u.path.startswith('/pt-br/logon_article/')
        assert e['url'] not in seen
        seen.add(e['url'])
        assert Date.fromisoformat(e['date']).year == int(data['year'])
        assert e['date'] <= data['updated']
        assert e['image'].startswith('/assets/') and '..' not in e['image']
        assert (root / 'site' / e['image'].lstrip('/')).is_file()
    h = escape
    def shortdate(value):
        y, m, d = value.split('-')
        return f'{d}.{m}.{y}'
    cards = []
    for e in entries:
        cards.append(f'''<article class="logon-card" data-item data-search="{h(e['title']+' '+e['summary']+' '+e['author'])}">
<a class="logon-image" href="{h(e['url'])}" tabindex="-1" aria-hidden="true"><img src="{base+h(e['image'])}" alt="" loading="lazy" decoding="async"></a>
<div class="logon-copy"><h3><a href="{h(e['url'])}">{h(e['title'])}</a></h3>
<p class="logon-date"><time datetime="{e['date']}">{shortdate(e['date'])}</time> · LOGON</p>
<p>{h(e['summary'])}</p><a class="logon-read" href="{h(e['url'])}">Leia na LOGON »</a>
<small class="logon-credit">Imagem: {h(e['image_credit'])}</small></div></article>''')
    highlights = ''.join(f'<li><a href="{h(e["url"])}">{h(e["title"])}</a></li>' for e in entries[:4])
    return f'''<div class="wrap blog-layout" data-catalog>
<div class="blog-main"><section class="logon-intro" aria-labelledby="logon-heading">
<h1 id="logon-heading" class="blog-section-title">Artigos Logon</h1>
<div class="logon-questions"><p>Você se encontra fazendo perguntas fundamentais sobre a vida?</p>
<p>Você costuma se perguntar: qual o sentido da minha existência?</p>
<p>Você acredita que deve haver algo além das trivialidades do dia-a-dia, que justifique a sua vida?</p>
<p>Se sim, então LOGON pode ser para você.</p></div>
<p>LOGON explora uma nova perspectiva do desenvolvimento do ser humano e das mudanças na sociedade do século 21, que emergem na arte, na ciência e na religião.</p>
<p>Publicamos artigos de muitos autores, oriundos de diversos países e contextos e que, assim como você, foram tocados por essas questões. Suas contribuições são inspiradas por sua busca pelo significado da vida.</p>
<a class="logon-discover" href="https://logon.media/pt-br/">Conheça a revista digital LOGON</a></section>
<section class="logon-selection" aria-labelledby="logon-current"><h2 id="logon-current">Leituras de {h(data['year'])}</h2>
<p class="blog-selection-note">Uma seleção de artigos em português. A leitura completa é feita na LOGON.</p>
<p class="result-count" role="status" aria-live="polite" data-count>{len(entries)} publicações</p>
<div class="logon-grid">{''.join(cards)}</div>
<div class="empty" data-empty hidden><h3>Nenhuma publicação encontrada</h3><p>Tente outro termo ou limpe a busca.</p></div>
<button class="button more" type="button" data-more hidden>Mostrar mais publicações</button>
<p class="blog-updated">Seleção atualizada em {shortdate(data['updated'])}. <a href="https://logon.media/pt-br/">Veja outras publicações na LOGON »</a></p></section>
</div>
<aside class="blog-sidebar" aria-label="Navegação do Blog"><section class="blog-side-box blog-search"><h2>Busca</h2>
<form class="filters" role="search"><label>Buscar nos artigos LOGON de {h(data['year'])}<input type="search" name="q" maxlength="300" placeholder="Pesquisa…" autocomplete="off"></label><button type="reset" class="button button-light">Limpar busca</button></form>
<noscript><p>Os artigos estão listados nesta página. Ative o JavaScript para filtrar a seleção.</p></noscript></section>
<section class="blog-side-box"><h2>Acompanhe FB</h2><a class="blog-facebook" href="https://www.facebook.com/pentagramapublicacoes/">Pentagrama no Facebook ↗</a></section>
<section class="blog-side-box"><h2>Destaques</h2><ul>{highlights}</ul></section>
<section class="blog-side-box"><h2>Explore o acervo</h2><ul><li><a href="{base}/livros/">Livros e e-books</a></li><li><a href="{base}/revistas/">Revista Pentagrama</a></li></ul></section></aside></div>'''
