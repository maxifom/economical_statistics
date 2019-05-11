importScripts('https://storage.googleapis.com/workbox-cdn/releases/4.3.1/workbox-sw.js');
workbox.routing.registerRoute(
    new RegExp("\\.(js|css|png|jpg|ico)"),
    new workbox.strategies.StaleWhileRevalidate({
        cacheName: "assets-cache",
        plugins: [
            new workbox.expiration.Plugin({
                maxEntries: 50,
                maxAgeSeconds: 60 * 60,
                purgeOnQuotaError: true,
            })
        ]
    })
);
workbox.routing.registerRoute(
    "/",
    new workbox.strategies.StaleWhileRevalidate({
        cacheName: "main-page-cache",
        plugins: [
            new workbox.expiration.Plugin({
                maxEntries: 50,
                maxAgeSeconds: 60 * 60,
                purgeOnQuotaError: true,
            })
        ]
    })
);
workbox.routing.registerRoute(
    new RegExp("/(companies|company|news_single|news|history|visualization|predictions|dict|all_predictions)[\/*[0-9]*]*"),
    new workbox.strategies.StaleWhileRevalidate({
        cacheName: "html-cache",
        plugins: [
            new workbox.expiration.Plugin({
                maxEntries: 20,
                maxAgeSeconds: 60 * 60,
                purgeOnQuotaError: true,
            })
        ]
    })
);
workbox.routing.registerRoute(
    /^https:\/\/fonts\.googleapis\.com/,
    new workbox.strategies.StaleWhileRevalidate({
        cacheName: 'google-fonts-stylesheets',
        purgeOnQuotaError: true,

    }),
);
workbox.routing.registerRoute(
    /^https:\/\/fonts\.gstatic\.com/,
    new workbox.strategies.CacheFirst({
        cacheName: 'google-fonts-webfonts',
        purgeOnQuotaError: true,
        plugins: [
            new workbox.cacheableResponse.Plugin({
                statuses: [0, 200],
            }),
            new workbox.expiration.Plugin({
                maxAgeSeconds: 60 * 60 * 24 * 365,
            }),
        ],
    }),
);
