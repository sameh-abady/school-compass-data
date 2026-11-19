#!/usr/bin/env python3
"""Build a password-protected (AES-GCM encrypted) static copy of the School Compass page for Netlify.
Usage: python3 build.py <source index.html> <password> <out dir>"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src, pw, out = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(src, encoding='utf-8').read()

# Stand-in for the Claude runtime: only file downloads work outside Claude.
POLY = """<script>
window.claude = { use: async function(name){
  if (name === 'downloads') return { save: async function(o){
    var a=document.createElement('a'); a.href=URL.createObjectURL(o.data); a.download=o.filename;
    document.body.appendChild(a); a.click(); setTimeout(function(){URL.revokeObjectURL(a.href); a.remove();},1500); } };
  return null; } };
</script><script>
(function(){
  var VAPID='BPYp0p67_FDOf6Nja8SUaM9jWtHTvxK3NhMxCvfVr4FWyXTo_GOpZl-fbitQuLo0sVcLPBuAmm_9yZZhCpOZMco';
  function b64u(s){ s=s.replace(/-/g,'+').replace(/_/g,'/'); while(s.length%4) s+='='; var r=atob(s), a=new Uint8Array(r.length); for(var i=0;i<r.length;i++) a[i]=r.charCodeAt(i); return a; }
  function tok(){ try{ return window.__scTok || sessionStorage.getItem('sc-tok') || localStorage.getItem('sc-tok'); }catch(e){ return window.__scTok; } }
  var ios=/iP(hone|ad|od)/.test(navigator.userAgent), standalone=(window.matchMedia&&matchMedia('(display-mode: standalone)').matches)||navigator.standalone;
  var css='#pushBtn{position:fixed;bottom:16px;inset-inline-end:16px;z-index:50;background:#2f5f55;color:#fff;border:0;border-radius:999px;padding:12px 18px;font:inherit;font-size:15px;box-shadow:0 6px 18px rgba(0,0,0,.18);cursor:pointer}#pushBtn.on{background:#fff;color:#2f5f55;border:1px solid #cfe0da;padding:9px 13px;font-size:13px}#pushTip{position:fixed;bottom:70px;inset-inline-end:16px;z-index:50;max-width:290px;background:#fff;border:1px solid #e4e9e8;border-radius:14px;padding:12px 14px;font-size:14px;line-height:1.6;box-shadow:0 6px 18px rgba(0,0,0,.12)}';
  function tip(t){ var o=document.getElementById('pushTip'); if(o) o.remove(); if(!t) return; o=document.createElement('div'); o.id='pushTip'; o.innerHTML=t; document.body.appendChild(o); setTimeout(function(){ o.remove(); }, 12000); }
  function btn(txt,on){ var b=document.getElementById('pushBtn'); if(!b){ b=document.createElement('button'); b.id='pushBtn'; b.onclick=click; document.body.appendChild(b); } b.textContent=txt; b.className=on?'on':''; }
  async function api(action, sub){ var r=await fetch('/api/subscribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({token:tok(),action:action,sub:sub})}); if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); }
  var reg=null;
  async function refresh(){
    if(!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)){
      if(ios && !standalone){ btn('🔔 الإشعارات', false); return; } return; }
    reg = await navigator.serviceWorker.register('/sw.js');
    var sub = await reg.pushManager.getSubscription();
    if(sub && Notification.permission==='granted') btn('🔔 ✓', true); else btn('🔔 فعّل الإشعارات', false);
  }
  async function click(){
    if(ios && !standalone){ tip('على الآيفون: من Safari اضغط زرار المشاركة <b>⬆︎</b> ← <b>Add to Home Screen</b>، وافتح الموقع من الأيقونة الجديدة، وبعدين دوس هنا تاني.'); return; }
    if(!reg) return;
    try{
      var sub=await reg.pushManager.getSubscription();
      if(sub && Notification.permission==='granted'){ await api('test', sub.toJSON()); tip('بعتنا إشعار تجربة للتليفون ده ✅'); return; }
      var perm=await Notification.requestPermission(); if(perm!=='granted'){ tip('الإشعارات مقفولة. افتحها من إعدادات التليفون للموقع ده.'); return; }
      sub = await reg.pushManager.subscribe({userVisibleOnly:true, applicationServerKey:b64u(VAPID)});
      await api('add', sub.toJSON()); btn('🔔 ✓', true); tip('تمام! الإشعارات اشتغلت على التليفون ده ✅');
    }catch(e){ tip('حصلت مشكلة: '+e.message); }
  }
  function boot(){ if(!document.body){ return setTimeout(boot,200); } var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st); refresh().catch(function(){}); }
  if(document.readyState==='complete') boot(); else window.addEventListener('load', boot);
})();
</script>"""
i = html.find('<head>')
html = html[:i+6] + POLY + html[i+6:] if i >= 0 else POLY + html

ITER = 250000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, html.encode('utf-8'), None)
payload = {k: base64.b64encode(v).decode() for k, v in (('s', salt), ('i', iv), ('c', ct))}
payload['n'] = ITER

shell = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cut">
<meta name="robots" content="noindex,nofollow">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="بوصلة المدرسة">
<meta name="theme-color" content="#2f5f55">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>بوصلة المدرسة — Sandra &amp; Natalie</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;background:#f4f1ea;color:#1f2a37}
.box{background:#fff;border-radius:18px;padding:28px 24px;width:min(340px,88vw);box-shadow:0 10px 30px rgba(0,0,0,.08);text-align:center}
h1{font-size:22px;margin:0 0 4px} p{color:#6b7280;margin:0 0 18px;font-size:14px}
input{width:100%;box-sizing:border-box;font-size:18px;padding:12px 14px;border:1px solid #d1d5db;border-radius:12px;text-align:center}
button{margin-top:12px;width:100%;font-size:17px;padding:12px;border:0;border-radius:12px;background:#1f3b63;color:#fff}
.err{color:#b91c1c;font-size:14px;min-height:20px;margin-top:10px}
label{display:flex;gap:8px;align-items:center;justify-content:center;margin-top:12px;font-size:14px;color:#374151}
label input{width:auto}
</style></head><body>
<form class="box" id="f" autocomplete="on">
<h1>🧭 بوصلة المدرسة</h1><p>Sandra &amp; Natalie — اكتب الباسورد</p>
<input id="pw" type="password" autocomplete="current-password" placeholder="الباسورد / Password" required>
<label><input id="rem" type="checkbox" checked> افتكرني على الجهاز ده</label>
<button type="submit">دخول</button><div class="err" id="err"></div>
</form>
<script id="enc" type="application/json">__PAYLOAD__</script>
<script>
var P0=JSON.parse(document.getElementById('enc').textContent), P=P0;
var DATA_URL='https://raw.githubusercontent.com/sameh-abady/school-compass-data/main/payload.json';
var fresh=(async function(){ try{ var c=new AbortController(); setTimeout(function(){c.abort()},5000); var r=await fetch(DATA_URL+'?t='+Math.floor(Date.now()/60000),{cache:'no-store',signal:c.signal}); if(r.ok){ var j=await r.json(); if(j&&j.c&&j.i&&j.s) P=j; } }catch(e){} })();
function b(s){return Uint8Array.from(atob(s),function(c){return c.charCodeAt(0)});}
async function open_(pw){
  var base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
  var key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b(P.s),iterations:P.n,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['decrypt']);
  var pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:b(P.i)},key,b(P.c));
  return new TextDecoder().decode(pt);
}
async function go(pw,remember){
  await fresh;
  try{ var html; try{ html=await open_(pw); }catch(e1){ if(P===P0) throw e1; P=P0; html=await open_(pw); }
    try{ var hb=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('sc-push:'+pw)); window.__scTok=[].map.call(new Uint8Array(hb),function(x){return ('0'+x.toString(16)).slice(-2)}).join(''); sessionStorage.setItem('sc-tok',window.__scTok); if(remember) localStorage.setItem('sc-tok',window.__scTok); }catch(_){}
    try{ if(remember) localStorage.setItem('sc-pw',pw); }catch(e){}
    document.open(); document.write(html); document.close(); return true;
  }catch(e){ try{localStorage.removeItem('sc-pw');}catch(_){} return false; }
}
(async function(){ var s=null; try{s=localStorage.getItem('sc-pw');}catch(e){} if(s) await go(s,true); })();
document.getElementById('f').addEventListener('submit',async function(e){ e.preventDefault();
  var ok=await go(document.getElementById('pw').value,document.getElementById('rem').checked);
  if(!ok) document.getElementById('err').textContent='الباسورد غلط — Wrong password'; });
</script></body></html>"""
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'payload.json'), 'w').write(json.dumps(payload))
open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(shell.replace('__PAYLOAD__', json.dumps(payload)))
open(os.path.join(out, '_headers'), 'w').write("/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-cache\n")
print('built', os.path.getsize(os.path.join(out, 'index.html')))

# server-only push feed (netlify/data/feed.json) for the notification functions
import subprocess
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_feed.py'), src, pw, os.path.dirname(os.path.abspath(out))], check=True)
