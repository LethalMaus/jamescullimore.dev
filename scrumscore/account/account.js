'use strict';
(async()=>{
 const copy={
 en:['Set your password','Choose at least 12 characters. Then sign into ScrumScore with your email and this password.','Checking your invitation…','Password','Repeat password','Save password','Your password is saved. Open ScrumScore and choose “Sign in / restore household”. Use this account on both Android and iOS.','This link is missing, expired or already used. Ask for a new private setup link.','Passwords must match and contain at least 12 characters.','Could not save your password. Please try again.','Back to ScrumScore'],
 de:['Passwort festlegen','Wähle mindestens 12 Zeichen. Melde dich danach mit deiner E-Mail-Adresse und diesem Passwort in ScrumScore an.','Deine Einladung wird geprüft…','Passwort','Passwort wiederholen','Passwort speichern','Dein Passwort ist gespeichert. Öffne ScrumScore und wähle „Anmelden / Haushalt wiederherstellen“. Nutze dieses Konto auf Android und iOS.','Dieser Link fehlt, ist abgelaufen oder wurde bereits verwendet. Bitte um einen neuen privaten Einrichtungslink.','Die Passwörter müssen übereinstimmen und mindestens 12 Zeichen enthalten.','Das Passwort konnte nicht gespeichert werden. Bitte erneut versuchen.','Zurück zu ScrumScore'],
 fr:['Choisir un mot de passe','Choisis au moins 12 caractères. Connecte-toi ensuite à ScrumScore avec ton adresse e-mail et ce mot de passe.','Vérification de ton invitation…','Mot de passe','Répéter le mot de passe','Enregistrer','Ton mot de passe est enregistré. Ouvre ScrumScore et choisis « Se connecter / retrouver le foyer ». Utilise ce compte sur Android et iOS.','Ce lien est absent, expiré ou déjà utilisé. Demande un nouveau lien privé.','Les mots de passe doivent être identiques et contenir au moins 12 caractères.','Impossible d’enregistrer le mot de passe. Réessaie.','Retour à ScrumScore'],
 it:['Imposta la password','Scegli almeno 12 caratteri. Poi accedi a ScrumScore con la tua e-mail e questa password.','Verifica dell’invito…','Password','Ripeti password','Salva password','Password salvata. Apri ScrumScore e scegli “Accedi / ripristina famiglia”. Usa questo account su Android e iOS.','Il link è assente, scaduto o già usato. Richiedi un nuovo link privato.','Le password devono coincidere e avere almeno 12 caratteri.','Impossibile salvare la password. Riprova.','Torna a ScrumScore']
 };
 const language=(navigator.language||'en').split('-')[0];const t=copy[language]||copy.en;document.documentElement.lang=copy[language]?language:'en';
 const el=id=>document.getElementById(id);for(const[id,n]of Object.entries({title:0,intro:1,status:2,passwordLabel:3,repeatLabel:4,save:5,home:10}))el(id).textContent=t[n];
 const params=new URLSearchParams(location.hash.slice(1));const hash=params.get('token_hash');const type=params.get('type');history.replaceState(null,'',location.pathname);
 let access=null;
 const config=window.SCRUMSCORE_ACCOUNT;
 if(!config || config.url!=='https://biinfkpwuwwbgrvkhcin.supabase.co' || !hash || !/^[a-f0-9]{32,128}$/.test(hash) || !['invite','recovery'].includes(type)){el('status').textContent=t[7];return;}
 async function call(path,body,method='POST'){
  const response=await fetch(config.url+'/auth/v1/'+path,{method,headers:{apikey:config.key,'Content-Type':'application/json',...(access?{Authorization:'Bearer '+access}:{})},body:body===null?undefined:JSON.stringify(body),referrerPolicy:'no-referrer',cache:'no-store'});
  if(!response.ok)throw new Error('Request failed');return response.status===204?null:response.json();
 }
 try {const session=await call('verify',{token_hash:hash,type});access=session.access_token;if(!access)throw new Error('Missing session');el('status').textContent='';el('setup').hidden=false;el('password').focus();}catch{el('status').textContent=t[7];return;}
 el('setup').addEventListener('submit',async event=>{
  event.preventDefault();const password=el('password').value;
  if(password.length<12 || password!==el('repeat').value){el('status').textContent=t[8];return;}
  el('save').disabled=true;
  try {await call('user',{password},'PUT');el('setup').reset();el('setup').hidden=true;el('status').textContent=t[6];try{await call('logout?scope=local',null);}catch{}access=null;}
  catch {el('status').textContent=t[9];el('save').disabled=false;}
 });
})();
