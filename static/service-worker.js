const CACHE_NAME = "mi-app-cache-v1";
const urlsToCache = [
  "/",
  "/static/index.css",
  "/static/login.css",
  "/static/usuarios.css",
  "/static/app.js",
  "/static/icons/BruCRM.ico",
  "/static/icons/icon-512x512.png"
];

// Instalar el Service Worker y cachear archivos
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Interceptar solicitudes para servir desde la caché
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

// Actualizar el Service Worker
self.addEventListener("activate", event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      )
    )
  );
});
