import fs from 'node:fs';import path from 'node:path';
import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE));
const browser=await chromium.connectOverCDP(process.env.CDP_URL);
const base=process.env.PUBLIC_BASE||'https://pentagrama.test/pentagrama';
const root=path.resolve('site');const results=[];const errors=[];
fs.mkdirSync('docs/screenshots',{recursive:true});
const check=(v,name)=>{results.push({name,passed:!!v});if(!v)throw Error(name);};
try{for(const width of [1280,390]){
 const ctx=await browser.newContext({viewport:{width,height:900}});
 try{
 if(!process.env.PUBLIC_BASE)await ctx.route('**/*',async r=>{
 const u=new URL(r.request().url());if(u.origin!=='https://pentagrama.test')return r.abort();
 let f=path.resolve(root,u.pathname.replace(/^\/pentagrama\//,''));if(!f.startsWith(root+'/'))return r.abort();
 if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
 if(!fs.existsSync(f))return r.fulfill({status:404,body:''});
 await r.fulfill({body:fs.readFileSync(f),contentType:({'.html':'text/html','.css':'text/css','.js':'application/javascript','.ttf':'font/ttf','.png':'image/png','.jpg':'image/jpeg'})[path.extname(f)]||'application/octet-stream'});
 });
 const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));page.setDefaultTimeout(10000);
 await page.goto(base+'/blog/',{waitUntil:'networkidle'});
 check(await page.locator('h1').innerText()==='Artigos Logon',width+' reference heading');
 check(await page.locator('.logon-card').count()===8,width+' eight current articles');
 check(await page.locator('.logon-card time').evaluateAll(es=>es.every(e=>e.dateTime.startsWith('2026-'))),width+' all dates2026');
 check(await page.locator('.logon-read').evaluateAll(es=>es.every(e=>e.href.startsWith('https://logon.media/pt-br/logon_article/'))),width+' original destinations');
 await page.locator('.logon-card').first().scrollIntoViewIfNeeded();await page.waitForFunction(()=>[...document.querySelectorAll('.logon-card img')].slice(0,2).every(i=>i.complete&&i.naturalWidth>0));
 check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),width+' no overflow');
 await page.getByRole('searchbox').fill('Torii');check(await page.locator('.logon-card:visible').count()===1,width+' search');
 await page.getByRole('searchbox').fill('zzzzSemResultado');check(await page.locator('[data-empty]').isVisible(),width+' empty');
 await page.getByRole('button',{name:'Limpar busca'}).click();check(await page.locator('.logon-card:visible').count()===8,width+' reset');
 await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';scrollTo(0,0);});await page.screenshot({path:`docs/screenshots/blog-${process.env.PUBLIC_BASE?'public':'local'}-${width}.png`});
 check(await page.locator('.blog-archive, a[href*="/artigos/"]').count()===0,width+' retired archive absent');
 }finally{await ctx.close();}
}
const ctx=await browser.newContext({javaScriptEnabled:false});try{
 const p=await ctx.newPage();
 if(process.env.PUBLIC_BASE){await p.goto(base+'/blog/');check(await p.locator('.logon-card').count()===8,'noJS all current articles');check(await p.locator('.logon-read').first().isVisible(),'noJS read link');}
}finally{await ctx.close();}
}finally{await browser.close();fs.writeFileSync('docs/blog-browser-'+(process.env.PUBLIC_BASE?'public':'local')+'.json',JSON.stringify({results,errors},null,2));}
console.log(JSON.stringify({checks:results.length,passed:results.filter(e=>e.passed).length,errors}));if(errors.length)process.exitCode=1;
