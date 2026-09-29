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
  await resize(390);await visit('/');
  await evalJS('localStorage.removeItem("analytics_consent")');await visit('/');
  assert.equal(await evalJS('!!document.querySelector("script[src*=googletagmanager]")'),false,'Analytics must not load before consent');
  assert.equal(await evalJS('document.querySelector(".analytics-consent-banner").hidden'),false);
  await click('[data-analytics-consent=decline]');
  assert.equal(await evalJS('document.querySelector(".analytics-consent-banner").hidden'),true);
  await visit('/');assert.equal(await evalJS('document.querySelector(".analytics-consent-banner").hidden'),true,'Consent decision persists');
  assert.equal(await evalJS('document.querySelector("#analytics-consent-manage").closest("footer") !== null'),true);
  await click('.menu-toggle');assert.equal(await evalJS('document.querySelector(".menu-toggle").getAttribute("aria-expanded")'),'true');
  assert.equal(await evalJS('getComputedStyle(document.querySelector(".site-links")).display'),'flex');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
  assert.equal(await evalJS('document.querySelector(".menu-toggle").getAttribute("aria-expanded")'),'false');
  assert.equal(await evalJS('document.activeElement.className'),'menu-toggle');
  await click('.menu-toggle');await click('.site-links a[href="/#services"]');await wait(100);
  assert.equal(await evalJS('document.querySelector(".menu-toggle").getAttribute("aria-expanded")'),'false');
  await resize(1440);assert.equal(await evalJS('getComputedStyle(document.querySelector(".site-links")).display'),'flex');
  await resize(390);await visit('/');
  await evalJS('document.querySelector(".technology-details summary").focus()');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
  assert.equal(await evalJS('document.querySelector(".technology-details").open'),true,'Technology disclosure works with keyboard');
  assert.equal(await evalJS('document.querySelectorAll(".technology-skills > .skill-tags .tag").length'),12,'All original tags restored');
  assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,'Expanded technologies do not overflow');
  await resize(390);await visit('/blog.html');await wait(500);
  assert.equal(await evalJS('document.querySelectorAll(".blog-card").length'),12);
  assert.equal(await evalJS('document.querySelector(".blog-tools").hidden'),false);
  await evalJS('document.querySelector("#blog-search").value="security";document.querySelector("#blog-search").dispatchEvent(new Event("input"))');
  assert.match(await evalJS('document.querySelector("#blog-status").textContent'),/matching article/);
  assert.equal(await evalJS('document.querySelector(".pagination").hidden'),true);
  await evalJS('document.querySelector("#blog-search").value="notarealarticlexyz";document.querySelector("#blog-search").dispatchEvent(new Event("input"))');
  assert.equal(await evalJS('document.querySelectorAll(".blog-card").length'),0);
  assert.match(await evalJS('document.querySelector("#blog-status").textContent'),/No articles/);
  await evalJS('document.querySelector("#blog-search").value="";document.querySelector("#blog-search").dispatchEvent(new Event("input"));document.querySelector("#blog-topic").value="Compose";document.querySelector("#blog-topic").dispatchEvent(new Event("change"))');
  assert.ok(await evalJS('document.querySelectorAll(".blog-card").length')>0);
  await evalJS('document.querySelector("#blog-topic").value="";document.querySelector("#blog-topic").dispatchEvent(new Event("change"));document.querySelector("#blog-search").value="android";document.querySelector("#blog-search").dispatchEvent(new Event("input"))');
  assert.equal(await evalJS('document.querySelector("#more-results").hidden'),false);
  await click('#more-results');assert.equal(await evalJS('document.querySelectorAll(".blog-card").length'),24);
  await evalJS('document.querySelector("#blog-search").value="";document.querySelector("#blog-search").dispatchEvent(new Event("input"))');
  assert.equal(await evalJS('document.querySelectorAll(".blog-card").length'),12);
  assert.equal(await evalJS('document.querySelector(".pagination").hidden'),false);
  await visit('/blog/page-6.html');assert.equal(await evalJS('document.querySelectorAll(".blog-card").length'),4);
  await visit('/projects.html');assert.equal(await evalJS('document.querySelectorAll(".project-card").length'),projectCount);
  const urls=await evalJS('[...document.querySelectorAll(".project-card h3 a")].map(a=>a.pathname)');
  await resize(320);
  for(const url of urls){await visit(url);assert.equal(await evalJS('document.querySelectorAll("h1").length'),1);assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,`No overflow: ${url}`);}
  await visit('/');
  await evalJS('document.documentElement.style.fontSize="200%"');
  assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,'200% root text size');
  await visit('/');
  assert.equal(await evalJS('document.querySelectorAll(".testimonial-card").length'),6);
  assert.equal(await evalJS('document.querySelectorAll(".hero-tags .tag").length'),0);
  assert.equal(await evalJS('document.querySelectorAll(".hero-summary-list li").length'),5);
  assert.equal(await evalJS('getComputedStyle(document.querySelector(".hero-summary-card")).display'),'none');
  await evalJS('document.documentElement.style.scrollBehavior="auto";document.querySelector(".testimonial-dots").scrollIntoView({block:"center",behavior:"instant"})');
  const quoteScroll = await evalJS('scrollY');
  for(let i=1;i<=6;i++) {
    await click(`.testimonial-dots .dot-${i}`);
    assert.equal(await evalJS('document.querySelectorAll(".testimonial-card:not([hidden])").length'),1);
    assert.equal(await evalJS(`document.querySelector("#t${i}").hidden`),false);
    assert.equal(await evalJS('scrollY'),quoteScroll,'Testimonial navigation preserves scroll position');
  }
  await evalJS('document.querySelector(".testimonial-dots .dot-1").focus()');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
  assert.equal(await evalJS('document.querySelector("#t1").hidden'),false,'Keyboard activates testimonial');
  await call('Emulation.setScriptExecutionDisabled',{value:true});
  await visit('/');assert.equal(await evalJS('getComputedStyle(document.querySelector(".site-links")).display'),'flex','Navigation remains usable without JS');
  assert.equal(await evalJS('[...document.querySelectorAll(".testimonial-card")].every(e=>getComputedStyle(e).display==="grid")'),true,'All testimonials readable without JS');
  assert.equal(await evalJS('[...document.querySelectorAll(".fade-section, .fade-section > .section-inner")].every(e=>getComputedStyle(e).opacity==="1")'),true,'Content visible without JS');
  await click('.technology-details summary');
  assert.equal(await evalJS('document.querySelector(".technology-details").open'),true,'Technology disclosure works without JS');
  await visit('/blog.html');assert.equal(await evalJS('document.querySelectorAll(".blog-card").length'),12,'Static archive works without JS');
  await call('Emulation.setScriptExecutionDisabled',{value:false});
  await visit('/talks.html');
  assert.equal(await evalJS('location.pathname'),'/courses.html','Legacy talks URL redirects');
  assert.equal(await evalJS('document.querySelectorAll("a[href*=mastering-retrofit]").length'),1,'Retrofit course available');
  assert.equal(await evalJS('document.querySelector("link[rel=canonical]").href'),'https://jamescullimore.dev/courses.html');
  const representative = ['/','/projects.html','/projects/starjar.html','/blog.html','/courses.html','/articles/how-i-cut-my-gradle-build-time-by-50.html','/impressum.html'];
  for(const width of [320,390,768,1024,1440]){
    await resize(width);
    for(const url of representative){
      await visit(url);
      assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,`No overflow at ${width}: ${url}`);
      assert.equal(await evalJS('getComputedStyle(document.querySelector(".site-brand strong")).display !== "none"'),true,'Business name remains visible');
      if(url==='/') {
        const nav = await evalJS('document.querySelector(".site-header").getBoundingClientRect().height');
        assert.ok(nav <= 90, 'Compact header');
        if(width<500) assert.ok(await evalJS('document.querySelector(".hero").getBoundingClientRect().height') < 600,'Compact mobile hero');
        const screenshot = await call('Page.captureScreenshot',{format:'png'});
        fs.writeFileSync(`/tmp/website-${width}-home.png`,Buffer.from(screenshot.data,'base64'));
      }
    }
  }
  await call('Emulation.setDeviceMetricsOverride',{width:667,height:375,deviceScaleFactor:1,mobile:true});
  await visit('/');await click('.menu-toggle');
  assert.equal(await evalJS('document.querySelector(".site-header").getBoundingClientRect().height <= innerHeight'),true,'Landscape menu stays within viewport');
  await click('.site-links a[href="/#services"]');
  assert.equal(await evalJS('document.activeElement.id'),'services','Anchor navigation transfers focus');
  await resize(320);await visit('/');
  // Simulate text-only enlargement, including the original design's pixel-based typography.
  await evalJS('document.querySelectorAll("body *").forEach(e=>e.dataset.auditFont=getComputedStyle(e).fontSize);document.querySelectorAll("body *").forEach(e=>e.style.fontSize=(parseFloat(e.dataset.auditFont)*2)+"px")');
  assert.equal(await evalJS('document.documentElement.scrollWidth <= innerWidth'),true,'200% text-only enlargement without overflow');
  await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  await visit('/');
  assert.equal(await evalJS('getComputedStyle(document.documentElement).scrollBehavior'),'auto','Reduced motion disables smooth scrolling');
  assert.equal(await evalJS('document.getAnimations().length'),0,'Reduced motion has no entrance animation');
  await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'no-preference'}]});
  await visit('/');
  await evalJS('document.querySelector(".industries .section-inner").scrollIntoView({behavior:"instant",block:"center"})');
  await wait(80);
  assert.equal(await evalJS('document.querySelector(".industries .section-inner").getAnimations().some(a=>a.effect.getTiming().duration===550)'),true,'Visible content receives a subtle upward entrance');
  await wait(1000);
  assert.equal(await evalJS('getComputedStyle(document.querySelector(".industries .section-inner")).opacity'),'1','Content stays fully visible after entrance');
  await resize(390);await visit('/');
  await evalJS('document.querySelector(".own-product-icon[src*=elchem]").scrollIntoView({behavior:"instant",block:"center"})');
  assert.equal(await evalJS('(()=>{const r=document.querySelector(".own-product-icon[src*=elchem]").getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2).closest("a").pathname})()'),'/projects/elchem.html','Project icon is a link to its detail page');
  assert.deepEqual(errors,[],'No JavaScript exceptions');
  console.log('PASS: five responsive widths, landscape, manual testimonials, keyboard activation, text enlargement, reduced motion, mobile menu, Escape, resizing, consent, search, topics, pagination, all project pages, 200% root text size, JS-disabled fallback and console errors.');
  ws.close();
  await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`);
})().catch(e=>{console.error(e);process.exit(1)});
