/** Contract tests with an inert DOM/provider. No Google network calls. */
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const code=fs.readFileSync(new URL('../site/assets/content-search.js',import.meta.url),'utf8');
function fixture(engine='fixture-engine') {
 const timers=new Map(),scripts=[],executed=[],rendered=[],handlers={};let counter=0;
 const node=()=>({hidden:true,textContent:'',children:[],attrs:{},setAttribute(k,v){this.attrs[k]=v;},append(...els){this.children.push(...els);},replaceChildren(...els){this.children=els;},remove(){this.removed=true;}});
 const input={value:'alma',addEventListener(){},focus(){this.focused=true;}},filetype={value:''};
 const form={elements:{q:input,as_filetype:filetype},addEventListener(type,fn){(handlers[type]??=[]).push(fn);}};
 const status=node(),fallback=node(),results=node(),note=node();
 const panel={dataset:{engineId:engine},querySelector(s){return ({form,'[data-content-status]':status,'[data-content-fallback]':fallback,'[data-content-results]':results,'[data-search-note]':note})[s];}};
 const context={document:{querySelector:()=>panel,createElement:node,head:{append:el=>scripts.push(el)}},URL,URLSearchParams,Map,Promise,Error,setTimeout(fn,ms){const id=++counter;timers.set(id,{fn,ms});return id;},clearTimeout(id){timers.delete(id);}};
 context.window=context;
 const api={render(config){rendered.push(config);},getElement(name){return {execute(query){executed.push({name,query});}};}};
 vm.runInNewContext(code,context);
 const submit=async()=>{const event={preventDefault(){this.prevented=true;}};const promises=handlers.submit.map(fn=>fn(event));await Promise.resolve();return {event,done:Promise.all(promises)};};
 return {context,input,filetype,status,fallback,results,scripts,executed,rendered,timers,submit,init(){context.google={search:{cse:{element:api}}};context.__gcse.initializationCallback();},expire(ms){for(const [id,t] of [...timers])if(t.ms===ms){timers.delete(id);t.fn();}}};
}
test('missing/invalid ID preserves native form and caps query without third-party load',async()=>{
 for(const id of ['', '<script>','https://example.org']){const f=fixture(id);f.input.value='x'.repeat(8000);const s=await f.submit();await s.done;assert.equal(s.event.prevented,undefined);assert.equal(f.input.value.length,300);assert.equal(f.scripts.length,0);}
});
test('no provider on load; first submit loads once, uses latest bounded query and scopes results',async()=>{
 const f=fixture();assert.equal(f.scripts.length,0);f.input.value='a'.repeat(8000);const first=await f.submit();f.input.value='alma & espírito';f.filetype.value='pdf';const second=await f.submit();
 assert.equal(f.scripts.length,1);f.init();await Promise.all([first.done,second.done]);assert.equal(f.executed.length,1);assert.equal(f.executed[0].query,'alma & espírito');assert.equal(f.rendered[0].attributes.as_filetype,'pdf');assert.equal(f.rendered[0].attributes.as_sitesearch,'pentagrama.org.br');assert.equal(f.rendered[0].attributes.autoSearchOnLoad,false);
 const url=new URL(f.fallback.href);assert.equal(url.searchParams.get('q'),'alma & espírito');assert.equal(url.searchParams.get('as_filetype'),'pdf');
 f.context.__gcse.searchCallbacks.web.rendered('content-pdf');assert.equal(f.results.attrs['aria-busy'],'false');
});
test('switch PDF/all and repeated searches reuse engine but retain separate restrictions',async()=>{
 const f=fixture();const first=await f.submit();f.init();await first.done;f.filetype.value='pdf';await (await f.submit()).done;f.filetype.value='';await (await f.submit()).done;
 assert.equal(f.scripts.length,1);assert.equal(f.rendered.length,2);assert.equal(f.executed.length,3);assert.deepEqual(f.rendered.map(r=>r.attributes.as_filetype),['','pdf']);assert.equal(f.results.children[1].hidden,true);
});
test('script error and retry do not break local page or force external navigation',async()=>{
 const f=fixture();const first=await f.submit();f.scripts[0].onerror();await first.done;assert.match(f.status.textContent,/Não foi possível/);assert.equal(f.fallback.hidden,false);
 const second=await f.submit();assert.equal(f.scripts.length,2);f.init();await second.done;assert.equal(f.executed.length,1);
});
test('load timeout and result timeout end busy state and expose fallback',async()=>{
 const f=fixture();const first=await f.submit();f.expire(12000);await first.done;assert.match(f.status.textContent,/Não foi possível/);assert.equal(f.scripts[0].removed,true);
 const second=await f.submit();f.init();await second.done;f.expire(15000);assert.equal(f.results.attrs['aria-busy'],'false');assert.equal(f.fallback.hidden,false);
});
test('empty query does not load; unsafe-looking query is passed only as text',async()=>{
 const f=fixture();f.input.value='   ';await (await f.submit()).done;assert.equal(f.scripts.length,0);
 f.input.value='<svg onload=alert(1)>';const s=await f.submit();f.init();await s.done;assert.equal(f.executed[0].query,'<svg onload=alert(1)>');assert.equal(f.results.children.length,1);assert.equal(new URL(f.fallback.href).searchParams.get('q'),f.input.value);
});

test('real result renderer inserts text, rejects executable URLs and preserves safe links',async()=>{
 const f=fixture();const s=await f.submit();f.init();await s.done;
 const div=f.context.document.createElement('div');
 const done=f.context.__gcse.searchCallbacks.web.ready('content-all','q',[],[
  {url:'javascript:alert(1)',titleNoFormatting:'bad'},
  {url:'https://pentagrama.org.br/example.pdf',titleNoFormatting:'<img onerror=alert(1)>',contentNoFormatting:'<script>evil</script>'}
 ],div);
 assert.equal(done,true);assert.equal(div.children.length,1);
 const [link,snippet]=div.children[0].children;
 assert.equal(link.textContent,'<img onerror=alert(1)>');assert.equal(link.innerHTML,undefined);
 assert.equal(snippet.textContent,'<script>evil</script>');assert.equal(link.rel,'noopener noreferrer');
 f.context.__gcse.searchCallbacks.web.ready('content-all','q',[],[],div);
 assert.equal(div.children.length,1);assert.match(div.children[0].textContent,/Nenhum resultado/);
});
