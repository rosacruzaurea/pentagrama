# Changelog

## 2026.11.09 · Em revisão

- Mecanismo de busca no conteúdo configurado; renderização de títulos/trechos como texto pelo callback oficial, sem liberar eval ou HTML externo.
- Resultados dentro do fluxo da página; política de segurança mantida. Configuração de idioma e anúncios no provedor ainda requer revisão.
- Removida a demonstração, seus geradores e a opção de publicação; testes de regressão preservados.

## 2026.11.08.2 · Em revisão

- “Buscar no conteúdo” com preparação do Programmable Search, configuração pública vazia e carregamento somente ao pesquisar.
- Resultados na página, filtro PDF, limites, tratamento de falha e alternativa externa; busca local preservada.
- Demonstração interativa somente em staging, com exemplos reais do catálogo claramente identificados como simulação.
- Testes de contrato, CSP e UI com provedor simulado; ativação real depende do ID e de homologação.

## 2026.11.08 · Em revisão

- Busca local limitada a 300 caracteres na interface, na URL e no processamento, incluindo o Blog.
- Índice normalizado reutilizado e termos repetidos eliminados, evitando trabalho proporcional a consultas repetitivas.
- Testes de regressão para limites, navegação por URL, acentos, filtros, reset e reutilização do índice.

## 2026.11.07 · Em revisão

- URLs canônicas, descrições, metadados sociais e dados estruturados derivados do catálogo.
- Sitemaps separados para páginas primárias e todos os PDFs vinculados, com descoberta em robots.txt.
- Pesquisa Google opcional nas listagens, limitada ao domínio e com seleção de PDFs, preservando filtros locais.
- Verificações automáticas de SEO e testes de formulário em desktop/mobile e sem JavaScript.
- Seção específica em `docs/FALTANTES.md` com seis livros e nove revistas disponíveis sem texto extraível.
- Procedimento para comprovar indexação pelo Search Console; sem alteração dos arquivos do acervo.

## 2026.11.06.2

- Removido o acervo de 77 artigos de 2017–2018, suas páginas e mídias exclusivas.
- Blog mantido com a seleção LOGON de 2026; navegação ajustada ao catálogo vigente.
- Retirados snapshots, importadores antigos, relatórios e capturas transitórios.
- Documentação reduzida ao contexto técnico e às pendências editoriais.
- Livros, revistas, páginas institucionais e arquivos compartilhados preservados.

## 2026.11.06.1

- Blog reorganizado conforme a estrutura editorial arquivada de 2026.
- Seleção de oito artigos LOGON de 2026, com imagens locais, créditos e links para os textos originais.
- Busca no Blog e layout responsivo.

## 2026.11.05

- Apresentação oficial sem seção de backup ou avisos de prévia.
- Deploy via Actions restrito a `site/`, com geração e validação.
- Caminho-base configurável e staging separado.

## 2026.11.04

- Primeira versão estática: identidade visual, catálogo, busca, filtros e downloads.
