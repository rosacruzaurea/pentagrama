# Pentagrama: instruções de continuidade

Leia README.md, ESTADO.md e docs/VERIFICACAO.md antes de alterar.

- Fonte principal: site arquivado em 2026. Preservar logo, branco, dourado #B18400, Glegoo, faixa superior rosa/azul e estrutura editorial.
- Backup2018 e biblioteca local apenas complementam lacunas. Não confundir data da captura com publicação da obra.
- Editar conteúdo em content/site.json e layout em tools/build.py / site/assets. Gerar e conferir com Python.
- Nunca colocar SQL, arquivos privados, PHP, WordPress, credenciais ou backups brutos no Git.
- site/ é o contrato do artefato. Base /pentagrama/. Branch preview-pages somente artefato, main somente após PR/revisão.
- Não inventar capas, downloads, sinopses, funcionalidades de compra ou formulários.
- Após mudanças: conferir links, dados, desktop/mobile e funções alteradas. Não declarar navegadores/integrações não testados como validados.
