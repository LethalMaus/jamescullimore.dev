const query=new URLSearchParams(location.search), code=query.get('code')||'';
if(/^[A-Fa-f0-9]{12}$/.test(code)){document.querySelector('#code').textContent=code.toUpperCase();document.querySelector('#code').hidden=false;document.querySelector('#empty').hidden=true;}
// Keep only supported invitation fields when changing language; never insert HTML.
const safe=new URLSearchParams();if(/^[A-Fa-f0-9]{12}$/.test(code))safe.set('code',code);
const token=query.get('token')||'';if(/^[a-f0-9]{64}$/.test(token))safe.set('token',token);
document.querySelectorAll('nav a[hreflang]').forEach(a=>{a.search=safe.toString()});
fetch('/scrumscore/config.json').then(r=>r.json()).then(c=>{for(const [id,url,host] of [['apple',c.appStoreUrl,'apps.apple.com'],['google',c.playStoreUrl,'play.google.com']]){if(url){const u=new URL(url);if(u.protocol==='https:'&&u.hostname===host){const a=document.getElementById(id);a.href=u.href;a.hidden=false;}}}}).catch(()=>{});
