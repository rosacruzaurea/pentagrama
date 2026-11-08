"""Staging-only interactive approximation, using real catalog metadata, never PDF text."""
import json
from pathlib import Path
from seo import google_search, pdf_paths, plain


def render_demo(site, shell, entries, base):
    data = []
    for entry in entries:
        if entry['type'] not in {'livro', 'revista'}:
            continue
        data.append({'title': entry['title'], 'summary': plain(entry['summary']),
                     'authors': ', '.join(entry['authors']), 'url': base + entry['path'],
                     'pdf': bool(pdf_paths([entry]))})
    component = google_search().replace('data-engine-id="', 'data-unused-engine-id="', 1)
    component = component.replace('action="https://www.google.com/search"', 'action="#"').replace(' target="_blank"', '')
    component = component.replace(' Os filtros do acervo continuam disponíveis acima.', '')
    component = component.replace('A busca abre em outra aba e envia os termos a um serviço externo somente ao pesquisar. Nem todo o acervo pode estar indexado.', 'Demonstração local. Ative o JavaScript para experimentar a busca simulada.')
    component = component.replace('type="submit"', 'type="submit" disabled')
    body = f'''<section class="page-head wrap"><a class="back-link" href="{base}/buscar/">← Voltar à busca no acervo</a><p class="eyebrow">PRÉVIA INTERATIVA</p><h1>Buscar no conteúdo</h1><p class="lede">Demonstração com resultados ilustrativos. Nenhuma consulta é enviada a um serviço externo.</p></section>
<section class="wrap catalog"><p class="demo-notice">Esta simulação pesquisa títulos e descrições do catálogo, não o texto dos PDFs. A aparência final e os resultados dependerão do mecanismo configurado.</p>{component}</section>'''
    html = shell('Demonstração da busca no conteúdo', body, path='/demo-busca/')
    html = html.replace('</head>', f'<script defer src="{base}/demo-busca/demo.js"></script></head>')
    folder = site / 'demo-busca'
    folder.mkdir(exist_ok=True)
    (folder / 'index.html').write_text(html)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    script = (Path(__file__).parent / 'search-demo.js').read_text()
    (folder / 'demo.js').write_text('const demoEntries = ' + payload + ';\n' + script)
