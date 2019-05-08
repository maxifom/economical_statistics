const cacheName = 'cache-and-update-v1';
const cacheFiles = [
    "/icons/favicon.ico",
    "/js/index.js",
    "/js/jquery.js",
    "/js/d3.js",
    "/js/chart.js",
    "/js/d3.cloud.js",
    "/js/bootstrap.min.js",
    "/css/bootstrap.min.css",
    "/icons/ds.png",
    "/news",
    "/history",
    "/companies",
    "/visualization",
    "/predictions",
    "/dict",
    "/all_predictions",
    "/sw.js",
];

self.addEventListener('install', function (e) {
    console.log('[Service Worker] Install');
    e.waitUntil(
        caches.open(cacheName).then(function (cache) {
            console.log('[Service Worker] Caching all');
            return cache.addAll(cacheFiles);
        })
    );
});

self.addEventListener('fetch', function (event) {
    event.respondWith(caches.match(event.request).then(cachedResponse => {
        return cachedResponse || fetch(event.request)
    }));
    event.waitUntil(update(event.request));
});

function update(request) {
    return caches.open(cacheName).then((cache) =>
        fetch(request).then((response) =>
            cache.put(request, response)
        )
    );
}