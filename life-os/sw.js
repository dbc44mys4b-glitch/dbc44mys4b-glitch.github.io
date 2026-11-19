/* LIFE OS offline PWA: static shell only. Sensitive data is never cached here. */
const CACHE = 'life-os-v6-1-shell-20261119-montblanc';
const ASSETS = ['./','./index.html','./app.js','./config.js','./styles.css','./apple-light.css','./favicon.svg','./manifest.webmanifest','./icon-192.png','./icon-512.png','./apple-touch-icon.png','./pwa.js','./mountain-hero.webp'];
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',e=>{
  e.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('life-os-')&&k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()]));
});
self.addEventListener('fetch',e=>{
  const r=e.request;
  if(r.method!=='GET')return;
  const url=new URL(r.url);
  if(url.origin!==self.location.origin)return;
  const relative=url.pathname.slice(new URL(self.registration.scope).pathname.length);
  if(relative.startsWith('api/')||relative.startsWith('functions/')||relative.includes('auth'))return;
  if(r.mode==='navigate'){
    e.respondWith(fetch(r).catch(async()=>await caches.match('./index.html')||Response.error()));
    return;
  }
  if(!ASSETS.includes('./'+relative))return;
  e.respondWith(fetch(r).then(res=>{
    if(res.ok){const copy=res.clone();e.waitUntil(caches.open(CACHE).then(c=>c.put(r,copy)))}
    return res;
  }).catch(()=>caches.match(r)));
});
