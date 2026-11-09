/** SEO and opt-in Google form checks in a real Chrome, using existing CDP tooling. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE));
const browser=await chromium.connectOverCDP(process.env.CDP_URL,{timeout:15000});
const published=process.env.PUBLIC_BASE;
const base=published||'https://pentagrama.test/pentagrama';
const root=path.resolve('site');
const results=[],errors=[];
const check=(v,name)=>{results.push({name,passed:!!v});if(!v)throw Error(name);};
fs.mkdirSync('docs/screenshots',{recursive:true});
try {
 for(const [width,js] of [[1280,true],[390,true],[320,true],[390,false]]) {
  const label=`${width}-${js?'js':'nojs'}`;
  const ctx=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:js});
  const googleRequests=[];
  await ctx.route('https://www.google.com/search?**',async r=>{
   googleRequests.push(r.request().url());
   // Inspect the native form submission, without making queries or claiming indexed results.
   await r.fulfill({contentType:'text/html',body:'<!doctype html><title>Google submission fixture</title>'});
  });
  if(!published) await ctx.route('https://pentagrama.test/**',async r=>{
   const u=new URL(r.request().url());let f=path.resolve(root,u.pathname.replace(/^\/pentagrama\//,''));
   if(!f.startsWith(root+'/')&&f!==root)return r.abort();
   if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
   if(!fs.existsSync(f))return r.fulfill({status:404,body:''});
   await r.fulfill({body:fs.readFileSync(f),contentType:({'.html':'text/html','.css':'text/css','.js':'application/javascript','.ttf':'font/ttf','.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif','.xml':'application/xml'})[path.extname(f)]||'application/octet-stream'});
  });
  try {
   const page=await ctx.newPage();page.setDefaultTimeout(12000);
   page.on('pageerror',e=>errors.push(label+': '+e.message));
   page.on('console',m=>{if(m.type()==='error'&&/content security|refused to|violat/i.test(m.text()))errors.push(label+': '+m.text());});
   for(const route of ['/livros/','/revistas/','/buscar/']) {
    await page.goto(base+route,{waitUntil:'networkidle'});
    check(await page.locator('link[rel=canonical]').getAttribute('href')==='https://pentagrama.org.br'+route,label+route+' canonical production');
    check(js ? await page.locator('.filters').isVisible() : await page.locator('[data-item][hidden]').count()===0,label+route+' existing local filters or noJS full catalog');
    const google=page.locator('.google-search');
    check(!await google.getAttribute('open'),label+route+' Google opt-in closed');
    await google.locator('summary').click();
    check(await google.getByRole('searchbox').isVisible(),label+route+' opens with native details');
    check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),label+route+' no overflow');
    if(route==='/livros/') {
     check(googleRequests.length===0,label+' no request before submission');
     if(js){
      await page.locator('.filters [name=autor]').selectOption({label:'Jan van Rijckenborgh'});
      check(await page.locator('[data-item]:visible').evaluateAll(es=>es.length>0&&es.every(e=>JSON.parse(e.dataset.autor).includes('Jan van Rijckenborgh'))),label+' author filter preserved');
      await page.locator('.filters [name=q]').fill('gnosis');
      check(await page.locator('[data-item]:visible').count()>0,label+' local search preserved');
      await page.getByRole('button',{name:'Limpar filtros'}).click();
      check(await page.locator('[data-item]:visible').count()===24,label+' reset preserved');
     }
     await google.getByRole('searchbox').fill('alma & espírito');
     await google.locator('select').selectOption('pdf');
     const popupEvent=ctx.waitForEvent('page');
     await google.getByRole('button').click();
     const popup=await popupEvent;await popup.waitForLoadState('domcontentloaded');
     const submitted=new URL(googleRequests.at(-1));
     check(submitted.origin==='https://www.google.com'&&submitted.pathname==='/search'&&submitted.searchParams.get('as_sitesearch')==='pentagrama.org.br'&&submitted.searchParams.get('as_filetype')==='pdf'&&submitted.searchParams.get('q')==='alma & espírito',label+' scoped PDF query encoding');
     check(await popup.evaluate(()=>window.opener===null),label+' safe new tab');await popup.close();
     await google.locator('select').selectOption('');
     const popupAll=ctx.waitForEvent('page');await google.getByRole('button').click();const all=await popupAll;await all.waitForLoadState('domcontentloaded');
     check(new URL(googleRequests.at(-1)).searchParams.get('as_filetype')==='',label+' all pages and documents query');await all.close();
     await page.screenshot({path:`docs/screenshots/seo-${published?'public':'local'}-${label}.png`});
    }
   }
   await page.goto(base+'/produto/do-castigo-da-alma/',{waitUntil:'domcontentloaded'});
   check(await page.locator('link[rel=canonical]').getAttribute('href')==='https://pentagrama.org.br/livros/do-castigo-da-alma/',label+' alias canonical');
   const graph=JSON.parse(await page.locator('script[type="application/ld+json"]').textContent())['@graph'];
   check(graph.some(x=>x['@type']==='Book'&&x.name==='Do castigo da alma'),label+' valid publication schema');
  }finally{await ctx.close();}
 }
}catch(e){errors.push(e.message);}finally{
 await browser.close();
 fs.writeFileSync(`docs/seo-browser-${published?'public':'local'}.json`,JSON.stringify({results,errors},null,2)+'\n');
}
console.log(JSON.stringify({checks:results.length,passed:results.filter(x=>x.passed).length,errors}));process.exitCode=errors.length?1:0;
