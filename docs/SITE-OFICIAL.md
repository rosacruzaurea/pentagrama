# Site oficial: candidato de 05/11/2026

## Mudanças

- Retirada a seção do rodapé sobre a reconstrução e a página `/sobre-o-acervo/`. O build também remove esse HTML obsoleto de artefatos anteriores.
- Removidos avisos de prévia e notas automáticas de recuperação. Página institucional Quem somos preservada.
- Oito revistas mantêm seus avisos de indisponibilidade, agora sem referência ao backup. Nenhum arquivo de mídia, rota de publicação, alias ou dado bibliográfico foi substituído.
- Indexação permitida no modo oficial. `SITE_NOINDEX=1` serve o modo de desenvolvimento; não é autenticação.
- Base dos links compartilhada entre gerador e verificador, configurável por `PAGES_BASE_PATH`.
- Corrigido o workflow recém-adicionado: publica apenas `site/`, gera e valida antes do upload, recebe o base_path do Pages e impede execução manual de deploy a partir de branches de trabalho.
- Actions atualizadas para versões consultadas nos releases oficiais em 05/11/2026 e fixadas por SHA: checkout7.0.1, configure-pages6.0.0, upload-pages-artifact5.0.0, deploy-pages5.0.1. Sem instalação ou atualização de pacotes no host; build usa biblioteca padrão Python3.12.3.

## Evidências locais

- Três builds verificados: `/pentagrama`, raiz vazia e `/pentagrama-dev` com noindex. Em cada um:357páginas,11.794referências locais,878arquivos e zero erros. Arquivo:site-oficial-checks.json.
-278registros de conteúdo preservados; comparação com a base restringe a mudança editorial aos avisos de indisponibilidade; nenhum diff em site/assets.
- Chrome via perfil gerenciado, sandbox preservado:18/18conferências em1280px e390px. Rodapé sem backup/prévia, contato, largura, indexação, navegação para Quem somos, filtro com65livros disponíveis e aviso de arquivo indisponível. Evidência:site-oficial-browser.json.
- Capturas do rodapé desktop/mobile inspecionadas em screenshots/site-oficial-footer-1280.png e screenshots/site-oficial-footer-390.png.
- Navegador testou uma fixture local interceptada, não um deploy público. A primeira tentativa teve erro no roteador da fixture para a raiz; corrigido o teste, sem alteração do produto para contorná-lo.
- YAMLs conferidos por parser; diff de espaços considera CRLF já existente nos textos importados.

## Limites

Sem merge, deploy, configuração de domínio, criação de repositório dev ou alteração de environments. O workflow de produção precisa ser comprovado em execução após a integração autorizada; a CI de PR valida o candidato sem publicar.

As limitações editoriais documentadas em04/11não foram corrigidas neste PR. Remover notas técnicas do site não torna PDFs parciais em integrais. As fontes e o histórico ficam na documentação técnica, fora de site/.
