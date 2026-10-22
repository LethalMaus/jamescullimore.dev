/* Run with a local HTTP server on 8765 and an isolated Chromium CDP endpoint on 9223. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
  const port = process.env.AUDIT_CDP_PORT || '9223';
  const origin = process.env.AUDIT_ORIGIN || 'https://jamescullimore.dev';
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
await resize(390);await call('Network.setCacheDisabled',{cacheDisabled:true});
await call('Network.emulateNetworkConditions',{offline:false,latency:150,downloadThroughput:200000,uploadThroughput:93750,connectionType:'cellular4g'});
await call('Emulation.setCPUThrottlingRate',{rate:4});
await call('Page.addScriptToEvaluateOnNewDocument',{source:`window.__perf={lcp:0,cls:0};new PerformanceObserver(l=>{for(const e of l.getEntries())window.__perf.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__perf.cls+=e.value}).observe({type:'layout-shift',buffered:true});`});
const report=[];
for(const path of ['/starjar/','/watchful/','/dontgotobed/']){
 await call('Network.clearBrowserCache');await call('Page.navigate',{url:origin+path});await wait(20000);
 const data=await evalJS(`({url:location.href,...window.__perf,ready:document.readyState,bytes:performance.getEntriesByType('resource').reduce((n,r)=>n+r.transferSize,0),resources:performance.getEntriesByType('resource').sort((a,b)=>b.transferSize-a.transferSize).slice(0,8).map(r=>({url:r.name,bytes:r.transferSize,duration:r.duration})),iframes:document.querySelectorAll('iframe').length})`);
 report.push(data);console.log(JSON.stringify(data));
}
fs.writeFileSync(process.env.PERF_REPORT||'/tmp/website-performance.json',JSON.stringify(report,null,2));
await call('Emulation.setCPUThrottlingRate',{rate:1});ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`);
})().catch(e=>{console.error(e);process.exit(1)});
