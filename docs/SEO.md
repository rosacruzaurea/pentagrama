# SEO e descoberta dos PDFs

## Implementação

- `tools/seo.py` gera títulos, descrições, canonical, Open Graph e JSON-LD a partir do catálogo editorial. Não produz avaliações, preços, datas nem promessas de rich results.
- URLs canônicas são sempre `https://pentagrama.org.br/`, inclusive nos aliases antigos. Caminho de hospedagem não redefine a identidade pública do conteúdo.
- `sitemap.xml` referencia `sitemap-pages.xml` e `sitemap-pdfs.xml`. Os inventários são derivados das rotas primárias e dos links PDF do catálogo. Aliases, busca interna e página 404 não entram no sitemap de páginas. Não há `lastmod` artificial.
- Produção permite rastreamento e anuncia o sitemap em `robots.txt`. Busca interna e 404 usam `noindex,follow`. Staging continua com `SITE_NOINDEX=1`, `Disallow: /` e sem CNAME; os sitemaps nele apontam exclusivamente para produção. Não submetê-los como propriedade de staging.
- Livros, revistas e busca geral oferecem **Buscar no conteúdo**, limitada ao domínio público e com opção de PDFs. Sem ID configurado, usa formulário nativo em outra aba, sem scripts de terceiros. Com ID, carrega o Programmable Search somente na submissão e apresenta resultados internos. [Configuração, privacidade e ativação](BUSCA-CONTEUDO.md).
- Os filtros locais continuam independentes. Sem JavaScript, todo o catálogo e a pesquisa Google permanecem acessíveis.

## Verificação após publicação em produção

1. Confirmar que o deploy corresponde ao commit aprovado e verificar HTML, canonical, robots, ambos os sitemaps e PDFs pelo domínio público.
2. Na propriedade verificada `pentagrama.org.br` do Google Search Console, enviar `https://pentagrama.org.br/sitemap.xml`. É necessário acesso à propriedade; não colocar credenciais no repositório. Se ainda não houver verificação, definir o método com o responsável antes de alterar domínio ou DNS.
3. Inspecionar URLs prioritárias (páginas e PDFs) e registrar: URL, data, estado indexado/não indexado e motivo informado. Solicitar indexação das URLs prioritárias elegíveis; o sitemap é o caminho para descoberta em lote, não uma garantia.
4. Acompanhar os relatórios de indexação e sitemaps. Não confundir teste ao vivo/rastreabilidade com presença no índice, nem uma consulta `site:` vazia com prova de ausência.
5. Revisar os PDFs com criptografia, restrições ou ausência de texto. Preferir originais editoriais desbloqueados; caso necessário, preparar OCR com revisão de fidelidade e preservação dos originais. Não retirar proteções nem substituir arquivos silenciosamente.

Publicar um sitemap não assegura rastreamento, inclusão, prazo ou posição no Google. A busca opcional mostra somente resultados já conhecidos pelo buscador; não substitui a busca local completa do catálogo. Canonical também é um sinal, não uma ordem garantida.

## Testes

`python3 tools/check.py` verifica rotas, canonicals, JSON-LD e a correspondência integral dos dois inventários de sitemap. `tools/seo-browser-check.mjs` valida fluxos desktop/mobile, ausência de envio ao Google antes da submissão, parâmetros de domínio/tipo/termo, nova aba sem opener, aliases e funcionamento sem JavaScript. O destino externo é interceptado no teste: ele comprova a submissão, não a existência de resultados no índice Google.

## Referências

- [Sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Tipos de arquivo indexáveis](https://developers.google.com/search/docs/crawling-indexing/indexable-file-types)
- [Limites do operador site:](https://developers.google.com/search/docs/monitor-debug/search-operators/all-search-site)
- [PDFs no Google, orientação de 2011](https://developers.google.com/search/blog/2011/09/pdfs-in-google-search-results): ressalvas sobre criptografia e OCR; não usar essa orientação antiga como diagnóstico atual de cada URL.

## Limites da busca local

A consulta local `q` tem limite de 300 unidades UTF-16, consistente com `maxlength` do HTML. O limite também é aplicado ao ler a URL e antes de processar eventos; não depende apenas da interface. Consultas maiores são truncadas no campo e no processamento. O texto do catálogo é normalizado uma vez por carregamento, e palavras repetidas na consulta são consideradas uma única vez. A busca continua sem distinção de maiúsculas ou acentos; filtros, contagem e paginação mantêm seu comportamento. Esse controle reduz trabalho na aba, não é proteção contra DDoS da hospedagem.
