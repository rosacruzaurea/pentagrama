/** Run the shipped script against a small DOM contract; no packages or network. */
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../site/assets/app.js',import.meta.url),'utf8');
function setup(query='',records=[
 {search:'Alma e Rosacruz Áurea',autor:'["Jan"]',ano:'2025',tipo:'ebook'},
 {search:'Gnosis e consciência',autor:'["Catharose"]',ano:'2024',tipo:'livro'},
 {search:'Alma e consciência',autor:'["Jan"]',ano:'2024',tipo:'livro'},
]){
 let reads=0;const events={},windowEvents={};
 const controls=Object.fromEntries(['q','autor','ano','tipo'].map(name=>[name,{name,value:'',focus(){}}]));
 const items=records.map(row=>({hidden:false,dataset:{...row,get search(){reads++;return row.search;}}}));
 const count={textContent:''},empty={hidden:true},more={hidden:true,addEventListener(k,f){events['more:'+k]=f;}};
 const form={elements:controls,querySelectorAll(){return Object.values(controls);},addEventListener(k,f){events[k]=f;}};
 const catalog={querySelector(s){return ({form,'[data-count]':count,'[data-empty]':empty,'[data-more]':more})[s];},querySelectorAll(){return items;}};
 const location=new URL('https://catalog.test/buscar/'+query);
 const context={URL,URLSearchParams,location,history:{replaceState(a,b,url){location.href=String(url);}},window:{addEventListener(k,f){windowEvents[k]=f;}},document:{documentElement:{classList:{add(){}}},querySelector(s){return s==='[data-catalog]'?catalog:null;},addEventListener(){}}};
 vm.runInNewContext(source,context,{timeout:1000});
 return {controls,items,count,empty,more,location,reads:()=>reads,emit:(name)=>events[name]({preventDefault(){}}),pop:(query)=>{location.search=query;windowEvents.popstate();},visible:()=>items.filter(x=>!x.hidden)};
}
test('URL query is capped before first filter, including popstate',()=>{
 const s=setup('?q='+encodeURIComponent('a '.repeat(1000)));
 assert.equal(s.controls.q.value.length,300);
 s.pop('?q='+encodeURIComponent('b'.repeat(900)));assert.equal(s.controls.q.value.length,300);
});
test('programmatic input bypassing HTML maxlength is capped and URL reflects bounded value',()=>{
 const s=setup();s.controls.q.value='a '.repeat(4000);s.emit('input');
 assert.equal(s.controls.q.value.length,300);assert.equal(s.location.searchParams.get('q').length,300);
});
test('index is read once and reused across input, filters and reset',()=>{
 const s=setup();assert.equal(s.reads(),3);
 for(const term of ['alma','gnosis','alma alma ALMA','não encontrado']){s.controls.q.value=term;s.emit('input');}
 s.controls.autor.value='Jan';s.emit('change');s.emit('reset');assert.equal(s.reads(),3);
});
test('accents/case and repeated terms retain the same results',()=>{
 const s=setup();s.controls.q.value='ÁUREA';s.emit('input');assert.equal(s.visible().length,1);
 s.controls.q.value='alma';s.emit('input');const hits=s.visible();
 s.controls.q.value='ALMA álma alma';s.emit('input');assert.deepEqual(s.visible(),hits);
});
test('author/year/format combine with search and reset restores all fields',()=>{
 const s=setup('?q=alma&autor=Jan&ano=2025&tipo=ebook');assert.equal(s.visible().length,1);
 s.controls.ano.value='1990';s.emit('change');assert.equal(s.visible().length,0);assert.equal(s.empty.hidden,false);
 s.emit('reset');assert.equal(s.visible().length,3);assert.equal(s.location.search,'');
 assert.ok(Object.values(s.controls).every(c=>c.value===''));
});
test('show more and reset keep pagination semantics',()=>{
 const s=setup('',Array.from({length:60},()=>({search:'Alma',autor:'[]'})));
 assert.equal(s.visible().length,24);s.emit('more:click');assert.equal(s.visible().length,48);
 s.emit('reset');assert.equal(s.visible().length,24);assert.match(s.count.textContent,/60/);
});
test('empty and nonmatching queries remain well-defined',()=>{
 const s=setup();s.controls.q.value='  ';s.emit('input');assert.equal(s.visible().length,3);
 s.controls.q.value='<svg onload=alert(1)>';s.emit('submit');assert.equal(s.visible().length,0);
 assert.equal(s.count.textContent,'0 publicações encontradas');
});
