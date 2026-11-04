# Verificação da reconstrução

## Referência

A home de referência é https://web.archive.org/web/20260710195647/https://pentagrama.org.br/ . Os catálogos foram preservados em capturas de julho de 2026. Há 20 cards de livros e 20 de revistas extraídos dessas páginas; isso não comprova recuperação integral do catálogo2026.

Confirmados no HTML e na renderização da referência: logo, branco, dourado #B18400, Glegoo, faixa rosa/azul, navegação Home/Livros/Revistas/Quem somos/Contato/Blog e as seções da home. Os dois banners de 2019 referidos pela página têm correspondentes visuais no backup2016/05; foi usado o banner Fênix. Não se afirma identidade byte a byte com o recurso remoto indisponível. Carrosséis foram simplificados em seções estáticas responsivas. Não há newsletter, checkout ou envio de formulário simulado.

## Conteúdo

A prioridade é2026. O backup fornece os textos e arquivos ausentes, mantendo as rotas históricas. Registros duplicados de impresso/e-book foram reunidos por título, preservando aliases. As datas dos artigos são as originais. Livros não recebem uma data fictícia baseada na captura.

Os arquivos locais de22livros complementam o acervo:20PDFs e2EPUBs. O volume Entre o silêncio e a luz está identificado como miolo sem capa; a divergência entre o ano do rosto e da CIP não foi corrigida por inferência. Capas de novos livros foram extraídas dos próprios EPUBs ou renderizadas do PDF. A capa da Revista2025nº2 foi renderizada apenas da frente da prancha, sem recriar a arte.

O inventário vigente de faltantes está em FALTANTES.md. A primeira varredura de links não bastou: a conferência posterior dos235PDFs do backup localizou25publicações do catálogo de livros e2revistas que não estavam corretamente vinculadas no banco. A restauração não promete que todo item do catálogo tenha download.

## Controles efetivos

- Sanitização: sem PHP, SQL, scripts do WordPress, iframes, formulários antigos ou eventos HTML inline.
- CSP via meta: scripts/estilos locais; objetos bloqueados; mídia externa limitada à entrega de áudios GitHub. Não se afirma que isso configure headers HTTP do Pages.
- Sem instalação de pacotes na VPS. Build estático sem dependências externas. Ferramentas já existentes utilizadas na recuperação/teste.
- A dependência de CI checkout está fixada por SHA. O teste de browser usa o Playwright já disponível; não houve upgrade de tooling do host neste escopo.
- Artefato permitido por extensão e verificado abaixo do limite1GB do GitHub Pages.
- PDFs inspecionados por pdfinfo, com resultados por arquivo em pdf-check.json. Isso é verificação de estrutura/JavaScript declarado, não análise antivírus completa.

## Evidências

- artifact-manifest.json: arquivos, hashes, tamanho, referências locais e falhas.
- browser-local-*.json / browser-public-*.json: lotes efetivamente executados.
- screenshots/: capturas de avaliação. As imagens com1280/390 correspondem ao candidato atual; relatórios de tentativas anteriores são históricos.

A primeira rotina extensa de browser foi interrompida por pressão de recursos. Os lotes menores substituem essa tentativa; não tratar um lote interrompido como aprovado. A verificação pública será registrada após o deploy. Não foram testados Safari/iOS, entrega de e-mail, pedidos de compra ou disponibilidade contínua.

## Resultado local do candidato

-358páginas/aliases;12.112referências locais verificadas;852arquivos;684.590.775bytes de artefato; zero erros no verificador.
-33verificações de browser aprovadas em lotes:1280px(6),390px(18),320px(6),sem JavaScript(3). Capturas desktop/mobile inspecionadas.
- Busca sem acentos, estado vazio, entrada tratada como texto, reset, mostrar mais, filtro de ano, filtro de e-books, menu/Escape e link EPUB testados.
-186PDFs abriram; nenhum declarou JavaScript ou criptografia. O PDF Caos Exterior, Despertar Interior emitiu aviso de campos de formulário, mas a renderização da capa e a leitura da estrutura funcionaram; não foi modificado para ocultar o aviso.

## Verificação da primeira publicação e ajuste final

Pages41829622129 concluiu com sucesso. A primeira prévia pública passou em15conferênciasHTTP com hash idêntico ao candidato,24checks de browser em desktop/mobile e carregamento dos metadados de um áudio real, sem autoplay.52/52áudios tiveram tamanho eSHA256 conferidos pelaAPI do release.

A conferência semântica posterior encontrou flags de e-book herdadas do WordPress que não correspondiam à presença de arquivo. O filtro foi corrigido para representar os40livros comPDF/EPUB/MOBI recuperado, sem apresentar disponibilidade fictícia. O verificador agora bloqueia divergência entre rótulo e arquivo. Esta alteração afeta apenas home e listagens, não os PDFs, EPUBs ou áudios. Os relatórios públicos são atualizados após a nova publicação.

O workflow gerado pelo próprio Pages emitiu aviso sobre upload-artifact@v4 usandoNode20 com execução forçada emNode24 e migração de ubuntu-latest. É infraestrutura gerenciada pelo GitHub, não dependência de runtime do site ou atualização executada na VPS.

## Conferência final por arquivo, solicitada por Dani

A lista completa de faltantes exigiu cruzar o catálogo com os arquivos brutos, não apenas os links exportados. Foram inspecionadas as páginas iniciais dos235PDFs do backup. Os3arquivos contendo somente o aviso Temporariamente indisponível não foram apresentados como livros. Um nome de arquivo diferente recuperou O conhecimento que ilumina, antes classificado como ausente pela URL antiga.

A reconstituição adicional vinculou25publicações do catálogo de livros (incluindo Agenda2016) e2revistas. Inventário vigente:5livros do catálogo semPDF/EPUB,9revistas semPDF,2livros somente emEPUB;3arquivos extras do backup são apenas avisos. Entre o silêncio e a luz permanece como miolo sem capa. A biblioteca local e cópias de recuperação do servidor foram comparadas; nenhum título adicional útil apareceu fora das fontes já examinadas.

Os65registros com download na categoria de livros incluem a Agenda2016. O artefato contém213PDFs no total, incluindo artigos, revistas e livros. A prova atualizada de integridade está em artifact-manifest.json; as contagens da primeira publicação acima são históricas.

## Resultado publicado vigente

Código do artefato: `4d6bf3d6bea41ecb4c1743b6d9568e9dc9228265`. Pages: `f6555e973a152215ebafd6b9e74a51f0fd28f64c`, build 41832471136 aprovado. A atualização não modifica o domínio institucional nem main.

O verificador local aprovou 358 páginas, 12.167 referências locais e 879 arquivos, com 825.490.608 bytes. Todos os 213 PDFs abriram na verificação estrutural. No endereço público, 42 recursos responderam 200 com hashes iguais aos locais, incluindo os 27 PDFs recuperados após a reconciliação. O navegador mobile passou em 19 verificações, incluindo o total real de 65 registros com download no catálogo de livros. Os relatórios JSON e capturas correspondentes estão neste diretório.

As contagens anteriores nesta nota são o histórico da reconstrução, não o inventário vigente. FALTANTES.md e content/missing-publications.json são a referência atual para lacunas.
