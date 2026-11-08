/** Actual Chrome UI + synthetic provider: never evidence of real Google results. */
import fs from 'node:fs';import path from 'node:path';import {execFileSync} from 'node:child_process';import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE));
const browser=await chromium.connectOverCDP(process.env.CDP_URL,{timeout:15000});
const root=path.resolve('site'),results=[],errors=[];
const check=(v,name)=>{results.push({name,passed:!!v});if(!v)throw Error(name);};
const csp=execFileSync('python3',['-c',"import sys;sys.path.insert(0,'tools');from content_search import content_security_policy;print(content_security_policy(True))"],{encoding:'utf8'}).trim();
const fixture=`window.__calls=[];const elements={};window.google={search:{cse:{element:{render(c){elements[c.gname]={execute(q){window.__calls.push({query:q,attributes:c.attributes});c.div.textContent='Resultado ilustrativo: '+q;window.__gcse.searchCallbacks.web.rendered(c.gname,q,[],[]);}}},getElement(n){return elements[n]}}}}};window.__gcse.initializationCallback();`;
try {
 for(const [width,mode] of [[1280,'configured'],[390,'configured'],[390,'error']]){
  const ctx=await browser.newContext({viewport:{width,height:900}});const requests=[];
  try{
   await ctx.route('**/*',async r=>{
    const u=new URL(r.request().url());
    if(u.origin==='https://cse.google.com'){
     requests.push(u.href);if(mode==='error')return r.abort();
     return r.fulfill({contentType:'application/javascript',body:fixture});
    }
    if(u.origin!=='https://pentagrama.test')return r.abort();
    let file=path.resolve(root,u.pathname.replace(/^\/pentagrama\//,''));
    if(!file.startsWith(root+'/'))return r.abort();
    if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
    if(!fs.existsSync(file))return r.fulfill({status:404,body:''});
    let body=fs.readFileSync(file);
    if(file.endsWith('index.html'))body=body.toString().replace('data-engine-id=""','data-engine-id="fixture-engine"').replace(/(<meta http-equiv="Content-Security-Policy" content=")[^"]*/,(_,prefix)=>prefix+csp);
    await r.fulfill({body,contentType:({'.html':'text/html','.css':'text/css','.js':'application/javascript','.ttf':'font/ttf','.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif'})[path.extname(file)]||'application/octet-stream'});
   });
   const p=await ctx.newPage();p.setDefaultTimeout(10000);p.on('pageerror',e=>errors.push(e.message));
   await p.goto('https://pentagrama.test/pentagrama/livros/',{waitUntil:'networkidle'});
   const panel=p.locator('.google-search');
   check(requests.length===0,`${width}/${mode}: no third party on load`);
   await panel.locator('summary').click();await panel.getByRole('searchbox').fill('alma & espírito');
   check(requests.length===0,`${width}/${mode}: opening/typing sends nothing`);
   await panel.locator('select').selectOption('pdf');await panel.getByRole('button').click();
   if(mode==='error'){
    await p.getByText('Não foi possível exibir os resultados.',{exact:false}).waitFor();
    check(await panel.locator('[data-content-fallback]').isVisible(),`${width}: failure fallback`);
   }else{
    await panel.locator('[data-content-status]').filter({hasText:'Busca concluída'}).waitFor();
    const call=await p.evaluate(()=>window.__calls[0]);
    check(call.query==='alma & espírito'&&call.attributes.as_sitesearch==='pentagrama.org.br'&&call.attributes.as_filetype==='pdf',`${width}: scoped PDF submission`);
    check(ctx.pages().length===1&&await panel.locator('[data-content-results]').isVisible(),`${width}: same-page results`);
    await panel.locator('select').selectOption('');await panel.getByRole('searchbox').fill('gnosis');await panel.getByRole('button').click();
    await p.waitForFunction(()=>window.__calls.length===2);
    check(requests.length===1&&await p.evaluate(()=>window.__calls[1].attributes.as_filetype===''),`${width}: reuse loader; switch all files`);
    await panel.getByRole('searchbox').evaluate(el=>{el.value='a'.repeat(8000);el.form.requestSubmit();});
    await p.waitForFunction(()=>window.__calls.length===3);
    check(await p.evaluate(()=>window.__calls[2].query.length===300),`${width}: cap bypassed maxlength`);
   }
   await p.locator('.filters [name=q]').fill('gnosis');check(await p.locator('[data-item]:visible').count()>0,`${width}/${mode}: local search independent`);
   check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${width}/${mode}: no overflow`);
  }finally{await ctx.close();}
 }
}catch(e){errors.push(e.message);}finally{await browser.close();fs.writeFileSync('docs/content-browser-local.json',JSON.stringify({provider:'synthetic; no actual Google query',results,errors},null,2)+'\n');}
console.log(JSON.stringify({checks:results.length,passed:results.filter(r=>r.passed).length,errors}));process.exitCode=errors.length?1:0;
