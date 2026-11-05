# Desenvolvimento e produção no GitHub Pages

Proposta de 05/11/2026, em resposta à Dani. Não cria repositórios, domínios, secrets ou environments.

## Recomendação

O GitHub permite um site Pages por repositório. Branches e environments do Actions não criam destinos Pages independentes.

- **Produção:** repositório `rosacruzaurea/pentagrama`, código na `main`, Pages por Actions. Domínio pretendido: `pentagrama.org.br`, ainda não configurado. Merge revisado dispara o build e o deploy de `site/`.
- **Desenvolvimento:** criar `rosacruzaurea/pentagrama-dev` como destino apenas dos arquivos gerados. Endereço a provisionar: `https://rosacruzaurea.github.io/pentagrama-dev/`; opcionalmente `dev.pentagrama.org.br`, também a configurar. Não duplicar a manutenção do código-fonte.
- **Fonte única:** branches de trabalho e PRs permanecem em `pentagrama`. Publicar em dev o commit escolhido para revisão; após aprovação, integrar na main para produção. Registrar o SHA de origem em cada publicação.

Para automação entre repositórios, preferir GitHub App com escrita somente no repositório de dev; alternativa, credencial fine-grained restrita a esse destino. O GITHUB_TOKEN do repositório de origem não deve ser presumido como capaz de escrever em outro repositório. A implantação deve confirmar a capacidade real.

Não disponibilizar credenciais de deploy a código de PRs externos. Publicação de revisão deve usar branch interna confiável ou aprovação explícita, com concorrência separada da produção. Recomenda-se limitar o environment de produção à main e proteger a main com revisão/CI obrigatórias; confirmar recursos disponíveis antes de configurar.

Dev recebe `SITE_NOINDEX=1`. Se houver domínio próprio, ambos os ambientes podem usar base vazia; sem domínio próprio, dev usa `/pentagrama-dev`. Noindex/robots não tornam um Pages privado. Uma prévia compartilhada mostra o último candidato publicado; para prévias simultâneas por PR, considerar uma hospedagem com suporte nativo a esse fluxo.

## Estado atual e correção incluída no PR

Pages mudou de publicação por branch para Actions. O workflow recebido publica a raiz inteira (`path: '.'`), embora o HTML de entrada e seus recursos estejam em `site/`. O candidato corrige para publicar somente `site/`, após gerar e validar o artefato. Não modifica as configurações remotas do Pages.

A base dos links passa a vir de `actions/configure-pages.outputs.base_path`: `/pentagrama` no projeto atual, vazia após a configuração do domínio próprio. Configurar DNS/domínio/HTTPS continua sendo uma etapa separada. Produção permite indexação; desenvolvimento pode bloqueá-la por variável do build.

## Fontes consultadas

- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://github.com/actions/configure-pages/blob/v6.0.0/action.yml

Documentação do GitHub e configuração real do projeto consultadas em 05/11/2026. Proposta, não comprovação de um segundo ambiente implantado.
