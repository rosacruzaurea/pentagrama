# Estado canônico

Atualizado em 2026-11-04. Responsável pela solicitação e revisão: Dani.

## Entrega vigente

- **Prévia publicada e verificada:** https://rosacruzaurea.github.io/pentagrama/
- **PR aberto, sem merge:** https://github.com/rosacruzaurea/pentagrama/pull/1
- Branch de código: `feat/recuperacao-estatica-2026`.
- Fonte do artefato vigente: `4d6bf3d6bea41ecb4c1743b6d9568e9dc9228265`. Commits posteriores apenas documentais não alteram esse artefato.
- Publicação: `preview-pages:/`, commit `f6555e973a152215ebafd6b9e74a51f0fd28f64c`.
- Árvore publicada: `8808cadd87d592706538bb970baf8bf40c522cbe`.
- Build Pages aprovado: https://github.com/rosacruzaurea/pentagrama/actions/runs/41832471136
- CI do código aprovada: https://github.com/rosacruzaurea/pentagrama/actions/runs/41832381933
- Main permanece em `43e8e547407ec4188a136b7e4cc94dcb9342e52d`.
- HTTPS ativo, sem CNAME. O domínio pentagrama.org.br não foi alterado.
- Recuperação da prévia anterior: `f30cdfed890d57057a8b930c329137c29e9dd9e4`; não exige restaurar banco.

## Escopo e conteúdo

Pedido: reconstrução HTML/CSS/JS, priorizando conteúdo e identidade visual de 2026. Backup de 2018 e biblioteca local completam lacunas. Não há WordPress, backend, vendas ou formulários simulados.

O artefato possui 358 páginas/aliases, 77 artigos, 70 registros na categoria de livros (incluindo Agenda 2016), 124 revistas e páginas institucionais. Foram acrescentados arquivos de 22 obras do acervo local. A conferência dos arquivos brutos recuperou mais 25 publicações e 2 revistas que não estavam vinculadas corretamente no banco.

Há 213 PDFs no artefato e 2 EPUBs locais incorporados. Os 52 áudios estão no [release acervo-2018](https://github.com/rosacruzaurea/pentagrama/releases/tag/acervo-2018), com tamanho e SHA-256 conferidos. O artefato Pages tem 825.490.608 bytes, abaixo do limite de 1 GB.

## Lacunas e evidências

- [Lista completa de faltantes](docs/FALTANTES.md): 5 livros do catálogo sem PDF/EPUB, 9 revistas sem PDF, 2 livros somente em EPUB, 3 PDFs extras que são apenas avisos. Entre o silêncio e a luz tem miolo sem capa.
- [Verificação](docs/VERIFICACAO.md), [manifesto](docs/artifact-manifest.json), [HTTP público](docs/public-http-check.json), relatórios de browser e capturas em docs/.
- Os 42 recursos HTTP verificados, incluindo todos os 27 PDFs adicionais, responderam 200 com hash idêntico ao artefato.
- Busca, filtros, reset, paginação, menu/Escape e link EPUB passaram no navegador público mobile. Desktop e leitura sem JavaScript foram verificados nos lotes documentados; não houve teste em Safari/iOS.
- O áudio de amostra carregou metadados com controles ativos, sem autoplay. Não foi executada uma audição completa de todos os arquivos.

## Fontes e privacidade

1. HTML oficial arquivado em 2026, inclusive home, catálogos e sinopses recuperadas.
2. Arquivos e banco WordPress de 2018 fornecidos pela equipe.
3. Biblioteca local autorizada, com identificação pelas fichas e páginas iniciais das obras.

As capturas não comprovam recuperação integral do catálogo de 2026. Arquivos originais, SQL, contas, configurações e código não editorial permanecem fora do repositório, em armazenamento restrito. Nenhum WordPress ou banco foi iniciado.

## Próxima decisão

Revisão da Dani pelo Pages e pelo PR. Merge em main permanece pendente de pedido explícito. A prévia não é a migração do domínio institucional.
