/* Cache only the public guide. Reference-source files and external documents are excluded. */
const CACHE='daikin-guide-8013cec93f8a3986';
const ROOT=new URL('./',self.location.href);
const ASSETS=['./index.html','./manifest.webmanifest','./icons/guide-192.png','./icons/guide-512.png'].map(path=>new URL(path,ROOT).href);
const GUIDE_PATHS=new Set([ROOT.pathname,new URL('./index.html',ROOT).pathname]);
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS.map(url=>new Request(url,{cache:'reload'})))));
});
self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    for(const key of await caches.keys())if(key.startsWith('daikin-guide-')&&key!==CACHE)await caches.delete(key);
    await self.clients.claim();
  })());
});
self.addEventListener('message',event=>{if(event.data?.type==='ACTIVATE_UPDATE')self.skipWaiting();});
self.addEventListener('fetch',event=>{
  const request=event.request,url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==ROOT.origin)return;
  if(request.mode==='navigate'&&GUIDE_PATHS.has(url.pathname)){
    event.respondWith((async()=>{
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),4000);
      try{
        const response=await fetch(request,{signal:controller.signal,cache:'no-cache'});
        if(!response.ok)throw new Error('Guide unavailable');
        // Each saved release remains atomic until its new worker activates.
        return response;
      }catch(error){
        const saved=await caches.match(ASSETS[0],{cacheName:CACHE});if(saved)return saved;
        return new Response('The guide has not been saved yet. Connect to the internet and reload.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
      }finally{clearTimeout(timer);}
    })());
  }else if(ASSETS.includes(url.href)){
    event.respondWith(caches.open(CACHE).then(async cache=>(await cache.match(request))||fetch(request)));
  }
});
