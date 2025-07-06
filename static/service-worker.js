const CACHE_NAME = 'futrivals-cache-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/FutRivals.png',
  // aggiungi altre risorse statiche se necessario
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        return response || fetch(event.request);
      })
  );
}); 