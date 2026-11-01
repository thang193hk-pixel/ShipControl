// Emerald Ship: giữ trang mở app trong bộ nhớ máy, để icon trên điện thoại luôn mở được (kể cả khi mạng yếu)
const CACHE = "emerald-ship-v1";
const FILES = ["/ShipControl/", "/ShipControl/app/", "/ShipControl/manifest.webmanifest",
               "/ShipControl/icon-192.png", "/ShipControl/icon-512.png", "/ShipControl/favicon.svg"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => {
    const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r;
  }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
