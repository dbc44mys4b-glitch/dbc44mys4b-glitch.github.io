/* MONTBLANC 7.0 — offline app shell only; never cache private records or API calls. */
const CACHE = 'montblanc-v14.0.1-visible-20261121';
const ASSETS = ['./','./index.html','./app.js','./github-sync.js','./config.js','./styles.css','./mission60.css','./mission60.js','./challenge60.css','./challenge60.js','./apple-light.css','./favicon.svg','./manifest.webmanifest','./icon-192.png','./icon-512.png','./apple-touch-icon.png','./pwa.js','./mountain-hero.webp'];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
  event.waitUntil(Promise.all([
    caches.keys().then(keys=>Promise.all(keys.filter(key=>(key.startsWith('life-os-')||key.startsWith('montblanc-'))&&key!==CACHE).map(key=>caches.delete(key)))),
    self.clients.claim()
  ]));
});
self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET')return;
  const url=new URL(request.url);
  if(url.origin!==self.location.origin)return; // Do not touch github.com, Supabase, or any remote API
  const scopePath=new URL(self.registration.scope).pathname;
  if(!url.pathname.startsWith(scopePath))return;
  const relative=url.pathname.slice(scopePath.length);
  if(relative.startsWith('api/')||relative.startsWith('functions/')||relative.includes('auth'))return;
  if(request.mode==='navigate'){
    event.respondWith(fetch(request).catch(()=>caches.match('./index.html').then(response=>response||Response.error())));
    return;
  }
  const canonical='./'+relative;
  if(!ASSETS.includes(canonical))return;
  // Ignore ?v=... on requests while keeping a stable offline cache key.
  const canonicalUrl=new URL(canonical,self.registration.scope).href;
  event.respondWith(fetch(request).then(response=>{
    if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(cache=>cache.put(canonicalUrl,copy)))}
    return response;
  }).catch(()=>caches.match(canonicalUrl).then(response=>response||Response.error())));
});
