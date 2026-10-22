/* Run with a local HTTP server on 8765 and an isolated Chromium CDP endpoint on 9223. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
  const port = process.env.AUDIT_CDP_PORT || '9223';
  const origin = process.env.AUDIT_ORIGIN || 'http://127.0.0.1:8765';
  const tab = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, {method:'PUT'}).then(r=>r.json());
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  let id=0; const pending=new Map(); const errors=[];
  ws.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.id){pending.get(m.id)?.(m);pending.delete(m.id);}
    if(m.method==='Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.text);
  };
  const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id:n,method,params}));});
  const evalJS=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;};
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  const visit=async path=>{await call('Page.navigate',{url:origin+path});await wait(650);};
  const click=selector=>evalJS(`document.querySelector(${JSON.stringify(selector)}).click()`);
  const resize=width=>call('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width<500});
  await call('Page.enable');await call('Runtime.enable');
  await call('Network.enable');
  await call('Network.setBlockedURLs', {urls:['*googletagmanager.com*','*google-analytics.com*']});
const root=require('node:path').resolve(__dirname,'..');
const articles=JSON.parse(fs.readFileSync(root+'/data/articles.json','utf8'));
articles.push(...Array.from({length:Math.ceil(articles.length/12)},(_,i)=>({url:i?'/blog/page-'+(i+1)+'.html':'/blog.html'})));
const report=[];
for(const entry of articles){
 const row={path:entry.url,issues:[]};
 await resize(1440);await visit(entry.url);
 await evalJS('Array.from(document.images).forEach(i=>i.loading="eager")');
 await evalJS('Promise.race([Promise.all(Array.from(document.images).map(i=>i.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,8000))])');
 for(const width of [320,390,1440]){
  await resize(width);await wait(50);
  const data=await evalJS(`({overflow:document.documentElement.scrollWidth>innerWidth,h1:document.querySelectorAll('h1').length, brokenImages:Array.from(document.images).filter(i=>!i.naturalWidth).map(i=>i.src),emptyHeadings:Array.from(document.querySelectorAll('h1,h2,h3,h4')).filter(h=>!h.textContent.trim()).length,rawMarkdown:Array.from(document.querySelectorAll('.article-content p')).filter(p=>/^(#{1,6} |\\x60{3})/.test(p.textContent)).map(p=>p.textContent.slice(0,100)),badCode:Array.from(document.querySelectorAll('pre')).filter(p=>p.scrollWidth>p.clientWidth&&getComputedStyle(p).overflowX==='visible').length})`);
  if(data.overflow||data.h1!==1||data.brokenImages.length||data.emptyHeadings||data.rawMarkdown.length||data.badCode)row.issues.push({width,...data});
 }
 await resize(320);await evalJS('document.documentElement.style.fontSize="200%"');
 if(await evalJS('document.documentElement.scrollWidth>innerWidth'))row.issues.push({width:320,textScale:'200%',overflow:true});
 report.push(row);
 console.log(entry.url, row.issues.length?'ISSUES':'OK');
}
fs.writeFileSync('/tmp/blog-audit.json',JSON.stringify(report,null,2));
console.log('Audited',report.length,'article/archive pages');
assert.equal(report.filter(r=>r.issues.length).length,0,'See /tmp/blog-audit.json');
ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`);
})().catch(e=>{console.error(e);process.exit(1)});
