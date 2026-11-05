"""Recover editorial PDFs present on disk but unlinked/mislinked in WordPress.

Titles and volumes checked against PDF front matter. Never classify a valid-PDF
placeholder saying 'Temporariamente indisponível' as an available publication.
Run after merge_2026.py with the extracted backup root as argument.
"""
from pathlib import Path
import hashlib,html,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[1];backup=Path(sys.argv[1])
data=json.loads((ROOT/'content/site.json').read_text())
mapping={
 'A Fraternidade Mundial da Rosa-Cruz':'livros/fraternidade-mundial-rosa-cruz.pdf',
 'A Fraternidade de Shamballa':'livros/fraternidade-shamballa.pdf',
 'A Gnosis original egípcia, tomo 1':'livros/gnosis-original-egipcia-tomo-1.pdf',
 'A Gnosis original egípcia, tomo 2':'livros/gnosis-original-egipcia-tomo-2.pdf',
 'A Gnosis original egípcia, tomo 4':'livros/gnosis-original-egipcia-tomo-4.pdf',
 'A Gnosis universal':'livros/gnosis-universal.pdf',
 'A senda libertadora da Rosa-Cruz':'livros/senda-libertadora-rosa-cruz.pdf',
 'Agenda 2016':'livros/agenda2016.pdf',
 'Christianopolis':'livros/christianopolis.pdf',
 'Histórias do roseiral':'livros/historias-roseiral.pdf',
 'Iniciação. Iluminação. Libertação.':'wp-content/uploads/2016/09/iniciacao_iluminacao_libertacao.pdf',
 'João Ultimonascido':'livros/joao_ultimonascido.pdf',
 'Não há espaço vazio':'livros/nao-ha-espaco-vazio.pdf',
 'O Evangelho da Verdade e O Evangelho de Maria - O conhecimento que ilumina':'livros/conhecimento-ilumina-evangelho-verdade-evangelho-maria.pdf',
 'O Nuctemeron de Apolônio de Tiana':'livros/nuctemeron-apolonio-tiana.pdf',
 'O caminho da Rosa-Cruz nos dias atuais':'wp-content/uploads/2017/01/caminho.pdf',
 'O evangelho dos doze santos':'livros/evangelho-doze-santos.pdf',
 'O mistério da vida e da morte':'livros/misterio-vida-morte.pdf',
 'O mistério das bem-aventuranças':'livros/misterio-bem-aventurancas.pdf',
 'O novo caduceu de Mercúrio':'livros/novo-caduceu-mercurio.pdf',
 'O novo sinal':'livros/novo-sinal.pdf',
 'O remédio universal':'livros/remedio-universal.pdf',
 'O selo da renovação':'livros/selo-renovacao_0.pdf',
 'Os sinais poderosos do conselho de Deus':'livros/sinais-poderosos-conselho-deus.pdf',
 'Transfiguração e Transmutação':'wp-content/uploads/2017/02/transfiguracao.pdf',
 'Revista Ano 20 Número 1':'pentagramas/revista-ano-20-numero-1.pdf',
 'Revista Ano 24 Número 6':'pentagramas/revista-ano-24-numero-6.pdf',
}
evidence=[]
for title,relative in mapping.items():
    e=next(e for e in data['entries'] if e['title']==title)
    p=backup/relative;digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    name=digest[:12]+'-'+p.name;target=ROOT/'site/assets/media'/name
    if not target.exists():shutil.copyfile(p,target)
    target.chmod(0o644);url='/assets/media/'+name
    if url not in e['html']:
        e['html']=e['html'].replace('Arquivo não localizado no backup.','')
        note=''
        if title.endswith('egípcia, tomo 2'):note=' Edição anterior intitulada A Arquignosis Egípcia, tomo II (1986).'
        if title.endswith('egípcia, tomo 4'):note=' Edição anterior intitulada A Arquignosis Egípcia, tomo IV (1991).'
        e['html']+=f'<p><a href="{url}">Baixar publicação (PDF)</a>{html.escape(note)}</p>'
        e['backup_file_relinked']=True
    e['html']='\n'.join(line.rstrip() for line in e['html'].splitlines())
    evidence.append({'title':title,'source':relative,'url':url,'sha256':digest,'bytes':p.stat().st_size})
for e in data['entries']:
    if e['type']=='livro':e['ebook']=bool(re.search(r'href="/assets/[^\"]+\.(?:pdf|epub|mobi)"',e['html']))
(ROOT/'content/site.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(ROOT/'content/recovered-unlinked.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'relinked':len(evidence),'books':25,'magazines':2,'bytes':sum(e['bytes'] for e in evidence)}))
