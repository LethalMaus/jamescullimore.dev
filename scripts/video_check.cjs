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

for(const path of ['/starjar/','/watchful/','/dontgotobed/']){
 await resize(390);await visit(path);
 assert.equal(await evalJS('document.querySelectorAll("iframe").length'),0,'No player before activation');
 const selector='button.video-preview';await evalJS(`document.querySelector('${selector}').scrollIntoView({block:'center',behavior:'instant'});document.querySelector('${selector}').focus()`);
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
 await call('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
 await wait(300);
 assert.equal(await evalJS('document.querySelectorAll("iframe").length'),1,'Keyboard loads player');
 assert.equal(await evalJS('document.activeElement.tagName'),'IFRAME');
 await call('Emulation.setScriptExecutionDisabled',{value:true});await visit(path);
 assert.equal(await evalJS('document.querySelector("a.video-preview").hostname'),'www.youtube.com','No-JS fallback');
 await call('Emulation.setScriptExecutionDisabled',{value:false});
}
for(const path of ['/services/android-kotlin-multiplatform/','/services/android-app-rescue/','/services/android-testing-build-optimisation/','/de/leistungen/android-kotlin-multiplatform/','/de/leistungen/android-app-modernisierung/','/de/leistungen/android-testautomatisierung-gradle/']){
 for(const width of [320,390,1440]){
  await resize(width);await visit(path);assert.equal(await evalJS('document.documentElement.scrollWidth<=innerWidth'),true,path);
  assert.equal(await evalJS('document.querySelectorAll(".service-evidence blockquote").length'),1);
 }
 await resize(320);await evalJS('document.documentElement.style.fontSize="200%"');assert.equal(await evalJS('document.documentElement.scrollWidth<=innerWidth'),true,path+' large text');
}
console.log('PASS: lazy players, keyboard activation, no-JS links, six service evidence sections and enlarged text.');
ws.close();await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`);
})().catch(e=>{console.error(e);process.exit(1)});
