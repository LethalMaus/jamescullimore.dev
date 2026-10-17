/* Run with a local HTTP server on 8765 and an isolated Chromium CDP endpoint on 9223. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const projectCount = JSON.parse(fs.readFileSync(require('node:path').join(__dirname, '../data/projects.json'), 'utf8')).length;
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
  for (const path of ['/starjar/', '/watchful/', '/dontgotobed/']) {
    for (const width of [320,390,768,1440]) {
      await resize(width); await visit(path);
      assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,`${path} at ${width}`);
      assert.equal(await evalJS('document.querySelectorAll("main").length'),1);
    }
    await evalJS('localStorage.removeItem("analytics_consent")'); await visit(path);
    await evalJS(`document.addEventListener('click', e => { if(e.target.closest('a')) e.preventDefault(); });`);
    const badge='a[href*="play.google.com"] img';
    const count=()=>evalJS('dataLayer.filter(x=>x[0]==="event" && x[1]==="app_store_click").length');
    await click(badge); assert.equal(await count(),0,'No tracking before consent');
    await evalJS('setAnalyticsConsent(false)'); await click(badge); assert.equal(await count(),0,'No tracking after decline');
    await evalJS('setAnalyticsConsent(true)'); await click(badge); assert.equal(await count(),1,'Track nested badge click after consent');
    assert.equal(await evalJS('dataLayer.filter(x=>x[1]==="app_store_click")[0][2].app_id'),path.split('/')[1]);
    await evalJS('setAnalyticsConsent(false)'); await click(badge); assert.equal(await count(),1,'Revocation stops tracking');
  }
  await visit('/');
  assert.equal(await evalJS(`(()=>{const a=document.querySelector('.app-download-link');a.scrollIntoView({block:'center',behavior:'instant'});const r=a.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2).closest('a').pathname===a.pathname;})()`),true,'App link is not covered by case-study link');
  for (const path of ['/services/android-kotlin-multiplatform/', '/services/android-app-rescue/', '/services/android-testing-build-optimisation/']) {
    for (const width of [320, 390, 1440]) {
      await resize(width); await visit(path);
      assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,`Service overflow: ${path} at ${width}`);
      assert.equal(await evalJS('document.querySelectorAll("main").length'),1);
      assert.equal(await evalJS('document.querySelectorAll("h1").length'),1);
      assert.equal(await evalJS('new URL(document.querySelector("link[rel=canonical]").href).pathname'),path);
      assert.equal(await evalJS('document.querySelectorAll(".project-card").length'),3);
    }
    await evalJS('document.querySelector("summary").focus()');
    await call('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
    await call('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
    assert.equal(await evalJS('document.querySelector("details").open'),true,'Service FAQ keyboard access');
    await resize(320);
    await evalJS('document.documentElement.style.fontSize="200%"');
    assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,'Service text enlargement');
  }
  for (const [path, name] of [['/services/android-kotlin-multiplatform/','service'],['/starjar/','starjar'],['/watchful/','watchful']]) {
    await resize(1440); await visit(path);
    await evalJS('document.fonts.ready');
    const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    fs.mkdirSync('/tmp/website-review',{recursive:true});
    fs.writeFileSync(`/tmp/website-review/${name}.png`,Buffer.from(shot.data,'base64'));
  }
  await visit('/starjar/');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
  assert.equal(await evalJS('document.activeElement.className'),'skip-link');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  assert.equal(await evalJS('document.activeElement.id'),'main');
  assert.equal(await evalJS('document.querySelectorAll(".hero-media .starry").length'),2,'Animated StarJar characters restored');
  assert.ok(await evalJS('document.getAnimations().length')>0,'StarJar animation runs with normal motion preferences');
  await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  assert.equal(await evalJS('document.getAnimations().length'),0);
  assert.deepEqual(errors,[]);
  console.log('PASS: app mobile layouts, landmarks, consent/decline/revocation, nested store clicks, homepage app CTA, StarJar skip link, reduced motion, service pages, FAQs and text enlargement.');
  await resize(1440); await visit('/starjar/');
  await evalJS('document.querySelector("#inside-starjar").scrollIntoView({block:"start",behavior:"instant"})');
  let screenshot=await call('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync('/tmp/website-review/starjar-gallery.png',Buffer.from(screenshot.data,'base64'));
  await resize(390); await visit('/starjar/');
  screenshot=await call('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync('/tmp/website-review/starjar-mobile.png',Buffer.from(screenshot.data,'base64'));
  ws.close(); await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`);
})().catch(e=>{console.error(e);process.exit(1)});
