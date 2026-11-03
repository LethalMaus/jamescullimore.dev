import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const startedAt=new Date().toISOString();
const browser=await chromium.launch({headless:true,channel:process.env.TESTLENS_BROWSER_CHANNEL || undefined});
const context=await browser.newContext({viewport:{width:1440,height:1000}});
await context.route('**/*',route=>new URL(route.request().url()).origin==='http://127.0.0.1:8765'?route.continue():route.abort());
const page=await context.newPage();
const checks=[];
const assets=[];
const xml=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
page.on('response',async r=>{if(r.url().startsWith('http://127.0.0.1:8765/') && /blog\.html|assets\/blog\.js|data\/articles\.json/.test(r.url())){try{assets.push({url:r.url(),status:r.status(),sha256:createHash('sha256').update(await r.body()).digest('hex')});}catch{}}});
async function check(name,fn){const start=Date.now();try{await fn();checks.push({name,time:(Date.now()-start)/1000,status:'passed'});console.log('PASS '+name);}catch(e){checks.push({name,time:(Date.now()-start)/1000,status:'failed',message:e.message});console.log('FAIL '+name+': '+e.message);}}
try{
await page.goto('http://127.0.0.1:8765/blog.html');
await check('search_finds_network_layer_article',async()=>{
 await page.locator('#blog-search').fill('Retrofit');
 await page.locator('.blog-title a').filter({hasText:/Retrofit/i}).first().waitFor();
 assert.ok((await page.locator('#blog-grid .blog-card').count())>0);
 assert.match(await page.locator('#blog-grid').innerText(),/Retrofit/i);
});
await check('unmatched_search_has_no_cards',async()=>{
 await page.locator('#blog-search').fill('testlens-no-such-article-7419');
 await page.waitForFunction(()=>document.querySelectorAll('#blog-grid .blog-card').length===0);
 assert.match(await page.locator('#blog-status').innerText(),/0|no /i);
});
await check('clearing_search_restores_browse',async()=>{
 await page.locator('#blog-search').fill('');
 await page.locator('#blog-grid .blog-card').first().waitFor();
 assert.ok(await page.locator('.pagination').isVisible());
});
await check('featured_filter_shows_featured_articles',async()=>{
 const select=page.locator('#blog-featured');console.log('Featured choices:',await select.locator('option').allTextContents());
 await select.selectOption('featured');
 await page.waitForFunction(()=>{const cards=[...document.querySelectorAll('#blog-grid .blog-card')];return cards.length>0 && cards.every(c=>c.querySelector('.article-features'));});
 const cards=page.locator('#blog-grid .blog-card');assert.ok(await cards.count()>0);
 for(const card of await cards.all()) assert.equal(await card.locator('.article-features').count(),1);
});
await check('keyboard_loads_more_featured_articles',async()=>{
 await page.locator('#blog-search').fill('');
 const select=page.locator('#blog-featured');
 await select.focus();
 await page.keyboard.press('End');
 await page.keyboard.press('Tab');
 assert.equal(await select.inputValue(),'featured');
 const featuredArticles=JSON.parse(await readFile('data/articles.json','utf8')).filter(a=>a.featured_in?.length);
 assert.ok(featuredArticles.length>12,'The real article index must exercise a further page');
 await page.waitForFunction(()=>document.querySelectorAll('#blog-grid .blog-card').length===12);
 const links=page.locator('#blog-grid .blog-title a');
 const initial=await links.evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')));
 assert.deepEqual(initial,featuredArticles.slice(0,12).map(a=>a.url));
 const more=page.locator('#more-results');
 for(let tabs=0;tabs<150 && !(await more.evaluate(el=>el===document.activeElement));tabs++)await page.keyboard.press('Tab');
 assert.equal(await more.evaluate(el=>el===document.activeElement),true,'Load more must be reachable with Tab');
 await page.keyboard.press('Enter');
 const expected=Math.min(24,featuredArticles.length);
 await page.waitForFunction(n=>document.querySelectorAll('#blog-grid .blog-card').length===n,expected);
 assert.equal(await select.inputValue(),'featured','Keyboard pagination must preserve the selected filter');
 const urls=await links.evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')));
 assert.deepEqual(urls,featuredArticles.slice(0,expected).map(a=>a.url),'Every loaded card must match the real filtered article index');
 assert.equal(new Set(urls).size,urls.length,'Pagination must not duplicate cards');
 assert.equal(await links.nth(12).evaluate(el=>el===document.activeElement),true,'Focus must move to the first newly loaded article');
});
await check('mobile_search_has_no_horizontal_overflow',async()=>{
 await page.locator('#blog-featured').selectOption('');
 await page.setViewportSize({width:390,height:844});
 await page.locator('#blog-search').fill('Retrofit');
 await page.locator('.blog-title a').filter({hasText:/Retrofit/i}).first().waitFor();
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
});
}finally{await context.close();await browser.close();}
const endedAt=new Date().toISOString();
await writeFile('tools/testlens/output/results.xml',`<testsuite name="Website browser journeys" timestamp="${startedAt}" tests="${checks.length}" failures="${checks.filter(c=>c.status==='failed').length}">${checks.map(c=>`<testcase classname="WebsiteJourney" name="${c.name}" time="${c.time}">${c.status==='failed'?`<failure message="${xml(c.message)}"/>`:''}</testcase>`).join('')}</testsuite>`);
await writeFile('tools/testlens/output/run.json',JSON.stringify({startedAt,endedAt,target:'http://127.0.0.1:8765/blog.html',browser:'Playwright Chromium',checks,assets},null,2));
if(checks.some(c=>c.status==='failed'))process.exitCode=1;
