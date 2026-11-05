# Pentagrama Publicações

Site estático de Pentagrama Publicações. O histórico da reconstrução e suas fontes permanece na documentação técnica, fora do artefato publicado.

- Endereço Pages atual (domínio próprio ainda pendente): https://rosacruzaurea.github.io/pentagrama/
- [Estado atual e continuidade](ESTADO.md)
- [Verificação e limitações](docs/VERIFICACAO.md)
- [Lista de livros e revistas faltantes](docs/FALTANTES.md)
- [Conteúdo estruturado](content/site.json)
- [Fontes de 2026 e complementos locais](content/recovery-2026.json)

## Desenvolvimento

HTML, CSS e JavaScript sem framework, sem WordPress, sem backend e sem dependências de runtime. O build usa apenas a biblioteca padrão de Python 3.12+.

```sh
python3 tools/build.py
python3 tools/check.py
```

`site/` é o único diretório publicável. O workflow de deploy usa `main`, gera e valida o site, e publica somente `site/`. A branch `preview-pages` pertence ao fluxo anterior e não é mais a origem selecionada. Não publicar a raiz do repositório. Toda alteração passa por PR antes de `main`; o merge dispara o deploy.

- `PAGES_BASE_PATH`: caminho-base, padrão `/pentagrama`; vazio para domínio próprio na raiz. O workflow lê `base_path` de `actions/configure-pages` sem alterar o domínio.
- `SITE_NOINDEX=1`: build de desenvolvimento com noindex e bloqueio de crawlers; padrão `0` para site oficial. Isto não é controle de acesso.
- [Proposta dev/produção](docs/AMBIENTES.md): dois repositórios Pages, uma única fonte de código; ainda não provisionados.
- [Verificação desta mudança](docs/SITE-OFICIAL.md).

A pesquisa e recuperação inicial usaram ferramentas já disponíveis, inclusive BeautifulSoup, pdfinfo e pdftoppm. Os scripts `recover.py`, `read_sql.py`, `import_public.py` `merge_2026.py` e `recover_unlinked.py` documentam essa importação e recebem entradas privadas fora do repositório; não são necessários para editar ou reconstruir a versão publicada.

## Conteúdo e privacidade

Arquivos de configuração, SQL bruto, contas, pedidos, listas de contato, plugins, PHP e código suspeito do backup não foram importados. O HTML editorial foi sanitizado. Compras e formulários antigos não foram simulados. O site não tem analytics ou coleta própria por formulários.

Os áudios públicos recuperados ficam no release `acervo-2018`, separados do Pages. PDFs e EPUBs selecionados ficam no artefato. Alguns arquivos antigos continuam ausentes; as páginas informam isso sem inventar downloads.

Textos, marcas, capas, livros e revistas mantêm seus direitos editoriais. Não são automaticamente licenciados como código aberto. A fonte Glegoo acompanha sua licença OFL em `site/assets/fonts/OFL.txt`.

Na reimportação, executar `recover_unlinked.py` após `merge_2026.py`: ele recupera PDFs existentes mas não vinculados corretamente no banco. O inventário de faltantes considera arquivos reais, não apenas links da base.

## Domínio personalizado

`site/CNAME` registra `pentagrama.org.br` na raiz do artefato público. No deploy atual por GitHub Actions, o Pages ignora esse arquivo: o domínio efetivo é definido em Settings → Pages. O workflow já obtém a base de URLs dessa configuração. O arquivo não configura DNS nem comprova emissão do certificado HTTPS.

Ao publicar manualmente em `pentagrama-staging` por branch, não copiar o `CNAME` de produção: o staging deve manter seu endereço separado.
