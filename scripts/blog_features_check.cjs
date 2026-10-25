/* Requires the local preview and isolated Chrome CDP endpoint described in README.md. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const origin = process.env.AUDIT_ORIGIN || 'http://127.0.0.1:8765';
  const cdp = `http://127.0.0.1:${process.env.AUDIT_CDP_PORT || 9223}`;
  const articles = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/articles.json')));
  const tab = await fetch(`${cdp}/json/new?about:blank`, {method:'PUT'}).then(r=>r.json());
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise(r=>ws.onopen=r);
  let id=0; const pending=new Map(); const errors=[];
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id);}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);};
  const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id:n,method,params}));});
  const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;};
  const visit=async url=>{await call('Page.navigate',{url:origin+url});await new Promise(r=>setTimeout(r,250));};
  const resize=width=>call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<500});
  const expected=article=>(article.featured_in||[]).map(f=>({url:f.url,text:`${f.name}${f.edition||''}`}));
  const readPills=selector=>evaluate(`Array.from(document.querySelectorAll(${JSON.stringify(selector)})).map(a=>({url:a.href,text:a.querySelector('.feature-copy').textContent}))`);
  async function layout(label) {
    for(const width of [320,390,1440]) {
      await resize(width);
      assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,`${label}: overflow at ${width}`);
      assert.equal(await evaluate(`Array.from(document.querySelectorAll('.feature-pill')).some(a=>a.getBoundingClientRect().right>innerWidth)`),false,`${label}: pill overflow`);
    }
    await resize(320);
    await evaluate('document.documentElement.style.fontSize="200%"');
    assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,`${label}: enlarged text overflow`);
    await evaluate('document.documentElement.style.fontSize=""');
  }
  try {
    await call('Page.enable');await call('Runtime.enable');await call('Network.enable');
    await call('Network.setBlockedURLs',{urls:['*googletagmanager.com*','*google-analytics.com*']});
    // Verify every static archive card, including the no-JavaScript fallback.
    await call('Emulation.setScriptExecutionDisabled',{value:true});
    for(let p=0;p<Math.ceil(articles.length/12);p++) {
      await visit(p?`/blog/page-${p+1}.html`:'/blog.html');
      for(let j=0;j<articles.slice(p*12,p*12+12).length;j++)
        assert.deepEqual(await readPills(`.blog-card:nth-child(${j+1}) .feature-pill`),expected(articles[p*12+j]));
      await evaluate(`document.querySelectorAll('.feature-more').forEach(d=>d.open=true)`);
      await layout(`archive ${p+1} expanded`);
      await evaluate(`document.querySelectorAll('.feature-more').forEach(d=>d.open=false)`);
    }
    const featuredArticles = articles.filter(a=>a.featured_in?.length);
    await visit('/blog/featured.html');
    assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('.blog-title a')).map(a=>new URL(a.href).pathname)`),featuredArticles.map(a=>a.url));
    await layout('featured collection without JavaScript');
    await call('Emulation.setScriptExecutionDisabled',{value:false});
    for(const article of articles.filter(a=>a.featured_in?.length)) {
      await visit(article.url);
      assert.deepEqual(await readPills('.article-header .feature-pill'),expected(article));
      await layout(article.url);
    }
    // Search rebuilds cards in JavaScript; test each article's features independently.
    await visit('/blog.html');
    await evaluate(`new Promise((resolve,reject)=>{let tries=0;const timer=setInterval(()=>{if(!document.querySelector('.blog-tools').hidden){clearInterval(timer);resolve();}else if(++tries>100){clearInterval(timer);reject(Error('Search did not load'));}},50);})`);
    for(const article of articles) {
      await evaluate(`{const s=document.querySelector('#blog-search');s.value=${JSON.stringify(article.title)};s.dispatchEvent(new Event('input'));}`);
      const selector = `.blog-card:has(.blog-title a[href="${article.url}"])`;
      assert.equal(await evaluate(`document.querySelectorAll(${JSON.stringify(selector)}).length`),1,article.title);
      assert.deepEqual(await readPills(selector+' .feature-pill'),expected(article));
    }
    await evaluate(`{const s=document.querySelector('#blog-search');s.value='Android';s.dispatchEvent(new Event('input'));document.querySelector('#more-results').click();}`);
    assert.equal(await evaluate('document.querySelectorAll(".blog-card").length'),24);
    const disclosure = await evaluate(`{const d=document.querySelector('.feature-more');d.querySelector('summary').click();const opened=d.open;d.querySelector('summary').click();({opened,closed:!d.open})}`);
    assert.deepEqual(disclosure,{opened:true,closed:true});
    await layout('filtered results');
    await evaluate(`{document.querySelector('#blog-search').value='';const t=document.querySelector('#blog-topic');t.value='Testing';t.dispatchEvent(new Event('change'));}`);
    const filtered=await evaluate(`Array.from(document.querySelectorAll('.blog-card')).map(c=>({url:new URL(c.querySelector('.blog-title a').href).pathname,features:Array.from(c.querySelectorAll('.feature-pill')).map(a=>({url:a.href,text:a.querySelector('.feature-copy').textContent}))}))`);
    for(const card of filtered)assert.deepEqual(card.features,expected(articles.find(a=>a.url===card.url)));
    await evaluate(`{const t=document.querySelector('#blog-topic');t.value='';const f=document.querySelector('#blog-featured');f.value='featured';f.dispatchEvent(new Event('change'));}`);
    assert.equal(await evaluate(`document.querySelector('#blog-status').textContent.startsWith('${featuredArticles.length} matching articles')`),true);
    await evaluate(`document.querySelector('#more-results').click();document.querySelector('#more-results').click()`);
    assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('.blog-title a')).map(a=>new URL(a.href).pathname)`),featuredArticles.map(a=>a.url));
    await evaluate(`{const t=document.querySelector('#blog-topic');t.value='Testing';t.dispatchEvent(new Event('change'));}`);
    const featuredTesting=await evaluate(`Array.from(document.querySelectorAll('.blog-title a')).map(a=>new URL(a.href).pathname)`);
    assert.ok(featuredTesting.length>0);
    assert.ok(featuredTesting.every(url=>featuredArticles.some(a=>a.url===url)));
    await layout('featured testing filter');
    await visit('/blog/featured.html');
    await evaluate(`new Promise((resolve,reject)=>{let n=0;const t=setInterval(()=>{if(!document.querySelector('.blog-tools').hidden){clearInterval(t);resolve();}else if(++n>100){clearInterval(t);reject(Error('Featured search did not load'));}},50);})`);
    assert.equal(await evaluate(`document.querySelector('#blog-featured').value`),'featured');
    await evaluate(`{const f=document.querySelector('#blog-featured');f.value='';f.dispatchEvent(new Event('change'));}`);
    assert.equal(await evaluate(`document.querySelector('#blog-status').textContent.startsWith('${articles.length} matching articles')`),true);
    await visit('/');
    assert.equal(await evaluate(`document.querySelector('.home-publications a').getAttribute('href')`),'/blog/featured.html');
    assert.equal(await evaluate(`document.querySelector('.home-publications').closest('main') !== null`),true);
    await layout('homepage publication strip');
    await evaluate(`document.querySelector('[data-analytics-consent="decline"]')?.click()`);
    for (const width of [390,1440]) {
      await resize(width);
      await evaluate(`document.querySelector('.home-publications').scrollIntoView({block:'center',behavior:'instant'})`);
      const screenshot=await call('Page.captureScreenshot',{format:'png'});
      fs.writeFileSync(`/tmp/home-publications-${width}.png`,Buffer.from(screenshot.data,'base64'));
    }
    // New imports must contain readable code and load their hero images.
    for(const article of articles.slice(0,2)) {
      await visit(article.url);
      await evaluate('Promise.all(Array.from(document.images).map(i=>i.decode().catch(()=>{})))');
      assert.equal(await evaluate('Array.from(document.images).some(i=>!i.naturalWidth)'),false,article.url);
      assert.ok(await evaluate('document.querySelectorAll(".article-content pre code").length')>=2);
      assert.equal(await evaluate(`Array.from(document.querySelectorAll('iframe')).some(f=>!f.getAttribute('src'))`),false);
      await layout(article.url);
    }
    assert.deepEqual(errors,[]);
    await visit('/blog.html');
    await evaluate(`document.querySelector('[data-analytics-consent="decline"]')?.click()`);
    for (const width of [390,1440]) {
      await resize(width);
      await evaluate(`window.scrollTo(0, document.querySelector('.blog-card').getBoundingClientRect().top + scrollY - 100)`);
      const screenshot = await call('Page.captureScreenshot', {format:'png'});
      fs.writeFileSync(`/tmp/blog-features-${width}.png`, Buffer.from(screenshot.data, 'base64'));
    }
    console.log(`Passed: ${articles.length} article searches, all archives, article feature links, filters, load more, new imports and responsive layouts.`);
  } finally {ws.close();await fetch(`${cdp}/json/close/${tab.id}`);}
})().catch(e=>{console.error(e);process.exit(1);});
