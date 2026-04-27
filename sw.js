const CACHE = 'field-map-v3';
const STATIC = [
  './',
  './index.html',
  './sw.js',
];

// 高德地图相关域名
const AMap_HOSTS = [
  'webapi.amap.com',
  'restapi.amap.com',
  'webrd0.is.autonavi.com',
  'wprd0.is.autonavi.com',
  'webst0.is.autonavi.com',
  'lbs.amap.com',
  'vdata.amap.com',
  'mdevelop.amap.com',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // 高德地图域名 → 缓存优先
  if (AMap_HOSTS.some(h => url.hostname.includes(h))) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(resp => {
          if (resp.ok) {
            const clone = resp.clone();
            caches.open(CACHE).then(cache => cache.put(e.request, clone));
          }
          return resp;
        }).catch(() => new Response('', { status: 503 }));
      })
    );
    return;
  }

  // 本地请求 → 网络优先，缓存兜底
  if (url.hostname === '192.168.1.209' || url.hostname === 'localhost' || !url.host) {
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          if (resp.ok) {
            const clone = resp.clone();
            caches.open(CACHE).then(cache => cache.put(e.request, clone));
          }
          return resp;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // 其他 → 网络优先
  e.respondWith(fetch(e.request));
});
