# Contexto técnico

- Stack: HTML/CSS/JavaScript, geração com Python 3.12+; sem backend ou banco.
- Produção: `main` → GitHub Actions → `site/` → https://pentagrama.org.br/.
- Staging: repositório `pentagrama-staging`, branch `gh-pages`, raiz; artefato com base `/pentagrama-staging`, `noindex` e sem domínio próprio.
- Filtro de revistas: rótulos combinam ano civil e editorial quando comprovados nos títulos; números não são extrapolados. Valores/URLs continuam usando o ano civil.
- Conteúdo: 70 registros de livros, 124 revistas, 7 páginas institucionais e seleção de 8 artigos LOGON de 2026. Seleção editorial manual.
- Identidade: branco, dourado `#B18400`, Glegoo, faixa rosa/azul; referência visual de 2026 registrada em `content/blog-logon.json` e `content/site.json`.
- Fontes de edição: `content/`, `tools/build.py`, `tools/blog.py`, `tools/seo.py`, `site/assets/`. Build e checks no README.
- Fluxo: branch → PR → staging → revisão → merge; somente o merge publica em produção. PRs e Actions são a fonte do estado de integração/deploy.
- Recuperação: reverter o commit pertinente por PR e republicar o artefato; não requer restauração de banco.
- Limites editoriais: disponibilidade de arquivo não comprova integralidade ou edição. Há exemplares amostrais e vínculos que ainda precisam de cotejo; consultar `docs/FALTANTES.md` e `content/missing-publications.json`.
- SEO: canonicals, metadados estruturados, sitemaps de páginas/PDFs e pesquisa Google opcional. Procedimento de comprovação no Search Console em [SEO](docs/SEO.md); rastreabilidade não comprova indexação.
- Busca no conteúdo: mecanismo público configurado em `content/search.json`, resultados reais via callback seguro, sem liberar eval. [Configuração e limites](docs/BUSCA-CONTEUDO.md). Demo retirada. Português do Brasil observado na prévia pública. Anúncios/Nonprofit e compatibilidade completa de CSP permanecem sujeitos a homologação do painel externo.
- Busca local: limite de 300 caracteres no HTML, na leitura de URL e no processamento; índice normalizado por carregamento e deduplicação de termos. Testes de regressão em `tools/catalog-search.test.mjs` e `tools/search-browser-check.mjs`.
- Limites de teste: Chrome desktop/mobile simulado; Safari/iOS e dispositivos físicos não homologados.

Mudanças por versão: [CHANGELOG.md](CHANGELOG.md). Evidências transitórias ficam fora da árvore versionada; não registrar conversas, nomes de solicitantes ou histórico de execução aqui.

## Candidato SEO

Autoria Book derivada do catálogo em `tools/seo.py`; critérios e relação completa em [REVISAO-AUTORIA](docs/REVISAO-AUTORIA.md). 62 registros elegíveis, oito preservados sem autor estruturado. Sem alterações de rotas, PDFs ou conteúdo visível.

Complemento de interface no mesmo candidato: ícones SVG locais nas redes sociais, com aria-label/title e destinos preservados. Sem novas dependências ou páginas.
