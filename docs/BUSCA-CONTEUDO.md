# Busca no conteúdo

## Configuração

`content/search.json` contém um único parâmetro público: `programmableSearchId`.

- Vazio: formulário externo funcional, sem carregar o SDK nem habilitar origens adicionais na CSP.
- Preenchido com o ID (`cx`) válido: resultados na própria página, carregados somente após a submissão. Não colocar URL, HTML de incorporação, senha ou chave de API nesse campo.
- Rótulo público: **Buscar no conteúdo**, separado dos filtros locais do acervo.

O ID é incorporado ao HTML pelo build; não é lido da URL nem baixado de configuração remota. Livros, revistas e busca geral recebem o componente. O Blog mantém a busca local.

## Ativação com o mecanismo real

1. Criar/configurar o mecanismo na conta vinculada ao Google for Nonprofits. Restringir aos endereços de `pentagrama.org.br`; desabilitar pesquisa na web inteira e pesquisa de imagens.
2. Confirmar a modalidade Nonprofit e desligar anúncios no painel. O código não concede a isenção nem remove publicidade por CSS. A atribuição exigida pelo provedor é preservada.
3. Preencher `programmableSearchId` e gerar/validar o site, primeiro em staging.
4. Testar consultas reais em desktop/mobile, somente PDFs, ausência de anúncios, navegação e ausência de violações CSP. Examinar os hosts efetivamente usados pelo SDK: a lista preparada ainda precisa de homologação com o mecanismo real. Não liberar scripts genéricos, execução inline ou eval para contornar falhas.
5. Confirmar que não há chamadas ao provedor antes de pesquisar, que os resultados estão restritos ao domínio e que filtros locais, erro/rede bloqueada e alternativa externa continuam funcionais.
6. Submeter a revisão e só então publicar conforme o fluxo do projeto. Para desativar, esvaziar o ID, gerar novamente e publicar a revisão aprovada.

Sem ID real, testes com provedor simulado comprovam o comportamento da integração, não a compatibilidade final do serviço, a isenção de anúncios ou a indexação.

## Comportamento e privacidade

- Limite de 300 unidades UTF-16, também no processamento. Nenhuma pesquisa ao abrir a página, expandir o painel, digitar ou ler `q` da URL.
- Um carregamento de `cse.js` por página. Blocos de resultados separados para páginas/documentos e PDFs, ambos restritos a `pentagrama.org.br`.
- Inicialização manual via API oficial, sem busca automática nem alteração do histórico pelo provedor.
- Mensagem de carregamento e de falha; timeout de 12 s para inicialização e 15 s para resultados. A alternativa “Abrir resultados em outra aba” preserva consulta, domínio e tipo. Falhas nunca redirecionam automaticamente.
- Sem JavaScript, o formulário externo continua disponível. Não confundir esse fallback com resultados internos.
- Ao enviar a busca, o serviço externo recebe os termos e dados de conexão e pode usar cookies. Há aviso junto ao formulário. Não se faz proxy de consultas nem armazenamento próprio.
- CSP adicional somente nas três páginas de busca e somente com ID configurado: scripts/conexões em hosts Google enumerados, estilos inline necessários ao componente, imagens enumeradas e frame em `www.google.com`. Sem `unsafe-inline`/`unsafe-eval` para scripts, sem curingas de script ou origens de redes de anúncios. Nas demais páginas, preserva-se a política original.

## Demonstração interativa, exclusivamente em staging

Gerar em um checkout isolado:

```sh
PAGES_BASE_PATH=/pentagrama-staging SITE_NOINDEX=1 SEARCH_DEMO=1 python3 tools/build.py
PAGES_BASE_PATH=/pentagrama-staging SITE_NOINDEX=1 SEARCH_DEMO=1 python3 tools/check.py
```

Abrir `/demo-busca/`. A página apresenta resultados na própria tela, incluindo consulta, filtro PDF e estado vazio. Os exemplos vêm dos títulos/descrições reais do catálogo, não do texto integral dos PDFs. O aviso de simulação é permanente; o layout é ilustrativo, não reprodução garantida da interface final do provedor. Não usa ID nem rede externa.

`SEARCH_DEMO=1` sem `SITE_NOINDEX=1` falha. A demonstração não entra em sitemap; o verificador rejeita seus arquivos no artefato normal/de produção. Não copiar o staging para produção. Builds são realizados em checkouts isolados para não deixar arquivos da demonstração na árvore de origem.

## Verificações

- `node --test tools/*.test.mjs`: busca local e integração com DOM/provedor inertes, sem rede.
- `python3 -m unittest discover -s tools -p 'test_*.py'`: validação do ID, CSP e bloqueio da demonstração em produção.
- `tools/content-search-browser-check.mjs`: UI no Chrome com provedor sintético, resultados internos, PDF, limites, reutilização e falha.
- `tools/seo-browser-check.mjs`: fallback sem ID, submissão externa interceptada, desktop/mobile/sem JS.
- `tools/search-browser-check.mjs`: regressões da busca local.

Referências: [Search Element API](https://developers.google.com/custom-search/docs/element) · [Nonprofits](https://support.google.com/programmable-search/answer/12423873).
