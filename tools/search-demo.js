'use strict';
// This file is copied only into the explicit noindex demonstration artifact.
const panel = document.querySelector('.google-search');
const form = panel.querySelector('form');
const input = form.elements.q;
const results = panel.querySelector('[data-content-results]');
const status = panel.querySelector('[data-content-status]');
panel.open = true;
form.querySelector('button').disabled = false;
panel.querySelector('[data-search-note]').textContent = 'Demonstração: a busca e os exemplos abaixo são locais. Nenhum serviço externo é carregado.';
const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
const index = demoEntries.map(entry => ({...entry, text: normalize([entry.title, entry.summary, entry.authors].join(' '))}));
function render(event) {
  event?.preventDefault();
  input.value = input.value.slice(0, 300);
  const words = [...new Set(normalize(input.value).trim().split(/\s+/).filter(Boolean))];
  const matches = index.filter(entry => words.every(word => entry.text.includes(word)) && (form.elements.as_filetype.value !== 'pdf' || entry.pdf));
  results.replaceChildren();
  results.hidden = false;
  status.textContent = `${matches.length} exemplos no catálogo. Resultados ilustrativos, não uma consulta real ao conteúdo.`;
  if (!matches.length) {
    const empty = document.createElement('p');
    empty.textContent = 'Nenhum exemplo encontrado. Tente “alma”, “gnosis” ou “consciência”.';
    results.append(empty);
  }
  for (const entry of matches.slice(0, 10)) {
    const article = document.createElement('article'); article.className = 'demo-result';
    const label = document.createElement('p'); label.className = 'demo-result-path'; label.textContent = entry.pdf ? 'Publicação com PDF disponível' : 'Página do acervo';
    const h = document.createElement('h2'), link = document.createElement('a');
    link.textContent = entry.title; link.href = entry.url; h.append(link);
    const summary = document.createElement('p'); summary.textContent = entry.summary || entry.authors || 'Consulte a publicação no acervo.';
    article.append(label, h, summary); results.append(article);
  }
  if (matches.length > 10) {
    const note = document.createElement('p'); note.textContent = 'Esta demonstração mostra até dez exemplos por busca.'; results.append(note);
  }
}
form.addEventListener('submit', render);
input.value = 'alma';
render();
