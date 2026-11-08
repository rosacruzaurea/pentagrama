/** Bounded UI regression tests; no load test and no third-party queries. */
import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE));
const browser=await chromium.connectOverCDP(process.env.CDP_URL,{timeout:15000});
const published=process.env.PUBLIC_BASE,base=published||'https://pentagrama.test/pentagrama',root=path.resolve('site');
const results=[],errors=[],timings=[];
const check=(value,name)=>{results.push({name,passed:!!value});if(!value)throw Error(name);};
try{for(const width of [1280,390]){
 const ctx=await browser.newContext({viewport:{width,height:900}});
 try{
 if(!published)await ctx.route('**/*',async r=>{
  const u=new URL(r.request().url());if(u.origin!=='https://pentagrama.test')return r.abort();
  let f=path.resolve(root,u.pathname.replace(/^\/pentagrama\//,''));if(!f.startsWith(root+'/'))return r.abort();
  if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
  if(!fs.existsSync(f))return r.fulfill({status:404,body:''});
  await r.fulfill({body:fs.readFileSync(f),contentType:({'.html':'text/html','.css':'text/css','.js':'application/javascript','.ttf':'font/ttf','.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif'})[path.extname(f)]||'application/octet-stream'});
 });
 const page=await ctx.newPage();page.setDefaultTimeout(12000);page.on('pageerror',e=>errors.push(e.message));
 for(const route of ['/buscar/','/livros/','/revistas/','/blog/']){
  const label=width+route;
  await page.goto(base+route+'?q='+encodeURIComponent('a '.repeat(1000)),{waitUntil:'networkidle'});
  const input=page.locator('.filters input[name=q]');
  check(await input.getAttribute('maxlength')==='300',label+' HTML input limit');
  check((await input.inputValue()).length===300,label+' initial URL limit');
  const observation=await input.evaluate(el=>{
   el.value='a '.repeat(4000);const start=performance.now();el.dispatchEvent(new Event('input',{bubbles:true}));
   return {ms:performance.now()-start,length:el.value.length,urlLength:new URL(location.href).searchParams.get('q').length};
  });
  timings.push({width,route,requested_chars:8000,...observation});
  check(observation.length===300&&observation.urlLength===300,label+' bypassed maxlength still capped');
  await page.evaluate(()=>{const url=new URL(location.href);url.searchParams.set('q','b'.repeat(2000));history.pushState(null,'',url);dispatchEvent(new PopStateEvent('popstate'));});
  check((await input.inputValue()).length===300,label+' history navigation limit');
  await input.fill('<svg onload="window.__searchAudit=1">');
  check(await page.evaluate(()=>window.__searchAudit===undefined&&!document.querySelector('svg[onload]')),label+' input remains text');
  check(await page.locator('[data-empty]').isVisible(),label+' empty state');
  await page.locator('.filters button[type=reset]').click();
  check(await input.inputValue()===''&&await page.locator('[data-item]:visible').count()===(route==='/blog/'?8:24),label+' reset restores catalog');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),label+' no overflow');
 }
 }finally{await ctx.close();}
}}catch(e){errors.push(e.message);}finally{
 await browser.close();fs.writeFileSync(`docs/search-browser-${published?'public':'local'}.json`,JSON.stringify({results,errors,timings},null,2)+'\n');
}
console.log(JSON.stringify({checks:results.length,passed:results.filter(x=>x.passed).length,errors,timings}));process.exitCode=errors.length?1:0;
