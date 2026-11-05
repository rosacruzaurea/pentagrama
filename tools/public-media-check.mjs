import fs from 'node:fs';import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE));const browser=await chromium.connectOverCDP(process.env.CDP_URL);
const context=await browser.newContext({viewport:{width:390,height:780}});const page=await context.newPage();const result={};
try{
 await page.goto('https://rosacruzaurea.github.io/pentagrama/imagens-do-mundo-14/',{waitUntil:'domcontentloaded',timeout:30000});
 const audio=page.locator('audio').first();await audio.scrollIntoViewIfNeeded();await audio.evaluate(e=>{e.preload='metadata';e.load();});
 await page.waitForFunction(()=>{const e=document.querySelector('audio');return e?.readyState>=1||e?.error;},{},{timeout:25000});
 Object.assign(result,await audio.evaluate(e=>({metadata_loaded:e.readyState>=1,duration:e.duration,error_code:e.error?.code??null,controls:e.controls,paused:e.paused})));
}catch(e){result.error=e.message;}finally{await context.close();await browser.close();}
fs.writeFileSync('docs/public-audio-browser.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));process.exitCode=result.metadata_loaded&&!result.error_code?0:1;
