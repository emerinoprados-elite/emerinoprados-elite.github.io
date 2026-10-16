/* Web de Eduardo Merino. El contenido ya viene escrito en cada página (lo genera herramientas/generar.py);
   este script solo registra la app instalable para usarla sin conexión. */
(function () {
  const RAIZ = document.documentElement.dataset.raiz || "";
  if ("serviceWorker" in navigator && location.protocol.startsWith("http"))
    navigator.serviceWorker.register(RAIZ + "sw.js").catch(() => {});
})();
