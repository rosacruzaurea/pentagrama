/** Bounded browser batches using an existing authorized CDP browser. No installation. */
import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
fs.mkdirSync('docs/screenshots',{recursive:true});
const root=process.cwd();const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE));
const browser=await chromium.connectOverCDP(process.env.CDP_URL,{timeout:15000});
const width=Number(process.env.WIDTH||390);const published=process.env.PUBLIC_BASE;const base=published||'https://pentagrama.test/pentagrama';
const noJS=process.env.NOJS==='1';const runKey=noJS?'nojs':width;
const context=await browser.newContext({viewport:{width,height:780},javaScriptEnabled:!noJS});const page=await context.newPage();page.setDefaultTimeout(15000);
const results=[],errors=[];const mode=published?'public':'local';
const save=()=>fs.writeFileSync(`docs/browser-${mode}-${runKey}.json`,JSON.stringify({results,errors},null,2));
const check=(v,name)=>{results.push({name,passed:!!v});if(!v)errors.push(name);console.log(name+': '+!!v);save();};
if(!published)await context.route('**/*',async route=>{const u=new URL(route.request().url());if(u.origin!=='https://pentagrama.test')return route.abort();let f=path.resolve(root,'site',u.pathname.replace(/^\/pentagrama\//,''));if(!f.startsWith(path.join(root,'site')+'/')&&f!==path.join(root,'site'))return route.abort();if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');if(!fs.existsSync(f))return route.fulfill({status:404,body:''});const ext=path.extname(f);await route.fulfill({body:fs.readFileSync(f),contentType:({'.html':'text/html','.css':'text/css','.js':'application/javascript','.ttf':'font/ttf','.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif'})[ext]||'application/octet-stream'});});
page.on('pageerror',e=>errors.push(e.message));
async function visit(route){await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:20000});await page.waitForFunction(()=>document.documentElement.classList.contains('js'));const s=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length}));check(!s.overflow,route+' fits '+width);check(s.h1===1,route+' h1');}
try{
 if(noJS){
  await page.goto(base+'/livros/',{waitUntil:'domcontentloaded',timeout:20000});check(await page.locator('[data-item]').count()===70,'70 books without JS');check(await page.getByRole('navigation').isVisible(),'navigation without JS');check(await page.locator('[data-item][hidden]').count()===0,'all books exposed without JS');
 }else if(width===1280||width===320){
  await visit('/');await page.evaluate(()=>Promise.all([...document.images].filter(i=>i.getBoundingClientRect().top<innerHeight).map(i=>i.decode().catch(()=>{}))));await page.screenshot({path:`docs/screenshots/${mode}-home-${width}.png`,timeout:8000});
  await visit('/livros/');await visit('/livros/rosacruz-aurea-uma-escola-iniciatica-para-o-seculo-xxi/');
 }else{
  await visit('/');await page.evaluate(()=>Promise.all([...document.images].filter(i=>i.getBoundingClientRect().top<innerHeight).map(i=>i.decode().catch(()=>{}))));await page.screenshot({path:`docs/screenshots/${mode}-home-${width}.png`,timeout:8000});
  const menu=page.getByRole('button',{name:/Menu/});await menu.click();check(await menu.getAttribute('aria-expanded')==='true','menu opens');await page.keyboard.press('Escape');check(await menu.getAttribute('aria-expanded')==='false','Escape closes menu');await menu.click();await page.goto(base+'/livros/',{waitUntil:'domcontentloaded',timeout:30000});await page.waitForSelector('[data-catalog]');
  await page.getByRole('searchbox').fill('gnosis');check(await page.locator('[data-item]:visible').count()>0&&await page.locator('[data-item]:visible').count()<24,'catalog search');
  await page.getByRole('searchbox').fill('<img src=x onerror=alert(1)>');check(await page.locator('[data-empty]').isVisible(),'empty state');check(await page.locator('img[src="x"]').count()===0,'search is plain text');
  await page.getByRole('button',{name:'Limpar filtros'}).click();check(await page.locator('[data-item]:visible').count()===24,'reset');await page.getByRole('button',{name:'Mostrar mais publicações'}).click();check(await page.locator('[data-item]:visible').count()===48,'show more');
  await visit('/revistas/?ano=2025');check(await page.locator('[data-item]:visible').count()===2,'2025 magazine filter');
  await visit('/livros/?tipo=ebook');check(await page.locator('[data-item]:visible').evaluateAll(a=>a.length>0&&a.every(e=>e.dataset.tipo==='ebook')),'ebook filter');const expectedBooks=JSON.parse(fs.readFileSync('content/site.json')).entries.filter(e=>e.type==='livro'&&e.ebook).length;check((await page.locator('[data-count]').innerText()).includes(String(expectedBooks)),'ebook total matches available files');
  await visit('/livros/iniciacao-e-libertacao/');check(await page.locator('.prose a[href$=".epub"]').count()===1,'recovered EPUB link');
  await page.evaluate(()=>Promise.all([...document.images].filter(i=>i.getBoundingClientRect().top<innerHeight).map(i=>i.decode().catch(()=>{}))));await page.screenshot({path:`docs/screenshots/${mode}-book-${width}.png`,timeout:8000});
 }
}catch(e){errors.push(e.message);save();}finally{await context.close();await browser.close();save();}
console.log(JSON.stringify({checks:results.length,passed:results.filter(r=>r.passed).length,errors}));process.exitCode=errors.length?1:0;
