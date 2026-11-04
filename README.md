# Pentagrama Publicações

Reconstrução estática do site, com **2026 como referência principal** e complementos do backup de 2018 e da biblioteca editorial local autorizada.

- Prévia: https://rosacruzaurea.github.io/pentagrama/
- [Estado atual e continuidade](ESTADO.md)
- [Verificação e limitações](docs/VERIFICACAO.md)
- [Conteúdo estruturado](content/site.json)
- [Fontes de 2026 e complementos locais](content/recovery-2026.json)

## Desenvolvimento

HTML, CSS e JavaScript sem framework, sem WordPress, sem backend e sem dependências de runtime. O build usa apenas a biblioteca padrão de Python 3.12+.

```sh
python3 tools/build.py
python3 tools/check.py
```

`site/` é o único diretório publicável. Caminho base: `/pentagrama/`. A branch `preview-pages` contém apenas esse artefato e usa `.nojekyll`. Não publicar a raiz da branch de código. O conteúdo é revisado em PR antes de qualquer alteração em `main`.

A pesquisa e recuperação inicial usaram ferramentas já disponíveis, inclusive BeautifulSoup, pdfinfo e pdftoppm. Os scripts `recover.py`, `read_sql.py`, `import_public.py` e `merge_2026.py` documentam essa importação e recebem entradas privadas fora do repositório; não são necessários para editar ou reconstruir a versão publicada.

## Conteúdo e privacidade

Arquivos de configuração, SQL bruto, contas, pedidos, listas de contato, plugins, PHP e código suspeito do backup não foram importados. O HTML editorial foi sanitizado. Compras e formulários antigos não foram simulados. A prévia não tem analytics ou coleta própria por formulários.

Os áudios públicos recuperados ficam no release `acervo-2018`, separados do Pages. PDFs e EPUBs selecionados ficam no artefato. Alguns arquivos antigos continuam ausentes; as páginas informam isso sem inventar downloads.

Textos, marcas, capas, livros e revistas mantêm seus direitos editoriais. Não são automaticamente licenciados como código aberto. A fonte Glegoo acompanha sua licença OFL em `site/assets/fonts/OFL.txt`.
