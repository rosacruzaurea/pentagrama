# Pentagrama Publicações

Site estático de livros, revistas e leituras LOGON.

- Produção: https://pentagrama.org.br/
- Staging: https://rosacruzaurea.github.io/pentagrama-staging/
- [Contexto técnico](ESTADO.md) · [Changelog](CHANGELOG.md) · [Pendências do acervo](docs/FALTANTES.md)

## Desenvolvimento

Python 3.12+ e biblioteca padrão, sem framework ou backend:

```sh
python3 tools/build.py
python3 tools/check.py
```

- `content/site.json`: catálogo e páginas institucionais.
- `content/blog-logon.json`: seleção estática do Blog, com fontes, datas e créditos. Textos completos na LOGON; não há atualização automática.
- `tools/build.py`, `tools/blog.py`: geração do HTML.
- `site/assets/`: estilos, scripts e arquivos públicos.
- `site/`: único diretório publicável. HTML gerado não deve ser editado diretamente.

## Publicação

Alterações passam por PR. O merge em `main` aciona GitHub Actions, que gera, valida e publica somente `site/`.

`PAGES_BASE_PATH` define o caminho-base: `/pentagrama` por padrão, vazio no domínio próprio, `/pentagrama-staging` na prévia. O workflow de produção obtém a base das configurações do Pages.

O staging recebe somente o artefato de um commit revisável, com `SITE_NOINDEX=1` e sem `CNAME`. A publicação é manual e independente da produção. `noindex` não restringe acesso.

## Validação e direitos

O verificador confere rotas, links locais, arquivos permitidos, política de indexação e tamanho do artefato. Relatórios e capturas são gerados localmente e não versionados. Os testes de navegador usam Playwright e um Chrome/CDP já disponíveis, informados por `PLAYWRIGHT_MODULE` e `CDP_URL`.

Não incluir credenciais, dados pessoais, bancos, backups ou transcrições no repositório. O site não possui formulários próprios nem analytics.

Textos, marcas, capas e publicações conservam seus direitos editoriais; não são automaticamente licenciados como código aberto. A licença da fonte Glegoo está em `site/assets/fonts/OFL.txt`.
