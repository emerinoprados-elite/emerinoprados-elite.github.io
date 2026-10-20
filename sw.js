/* Service worker: guarda la web para usarla sin conexión.
   VERSION y ARCHIVOS los actualiza herramientas/generar.py: así los móviles descargan lo nuevo. */
const VERSION = "em-4455b2d5";
const ARCHIVOS = [
  "./", "cursos/", "instrumentos/", "averias/",
  "mecanica/", "electricidad/", "electricos/", "hibridos/",
  "adas/", "videos/", "progreso/", "sobre-mi/",
  "instrumentos/calibre.html", "instrumentos/micrometro-centesimal.html", "instrumentos/micrometro-milesimal.html", "taller-motor/",
  "contenido.json", "manifest.webmanifest", "404.html", "assets/estilos.css",
  "assets/web.js", "assets/juego.js", "assets/progreso.js", "assets/emblema.svg",
  "assets/emblema-200.png", "assets/marca_agua.png", "assets/icono-192.png", "assets/icono-512.png",
  "assets/apple-touch-icon.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Primero la red (para ver siempre lo último) y, si no hay conexión, lo guardado.
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok) { const copia = res.clone(); caches.open(VERSION).then(c => c.put(req, copia)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true })
      .then(r => r || (req.mode === "navigate" ? caches.match("./") : undefined)))
  );
});
