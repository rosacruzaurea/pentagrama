# Continuidade do projeto

Leia README.md, ESTADO.md e CHANGELOG.md antes de alterar.

- Preserve identidade visual, fontes editoriais, datas reais e créditos. Não invente capas, sinopses ou downloads.
- Edite as fontes em `content/`, `tools/` e `site/assets/`; gere o HTML com `python3 tools/build.py` e valide com `python3 tools/check.py`.
- Não reintroduza o acervo de artigos antigos nem snapshots/importadores de recuperação. Livros e revistas antigos continuam fazendo parte do catálogo.
- `site/` é o único artefato. Produção usa Actions/main; staging usa repositório separado com base própria, noindex e sem CNAME.
- Toda mudança passa por PR e revisão antes de main. Não confunda validação local, staging e produção.
- Verifique os fluxos alterados em desktop/mobile. Preserve conteúdos e arquivos fora do escopo.
- Mantenha documentação curta e impessoal, com changelog e contexto técnico. Relatórios, capturas e registros de conversas ficam fora da árvore versionada.
- Nunca inclua segredos, SQL, backups brutos, dados pessoais ou arquivos de servidor no repositório.
