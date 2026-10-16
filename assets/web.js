/* Web de Eduardo Merino: lee contenido.json y rellena enlaces, catálogo y vídeos.
   La raíz de la web se indica con data-raiz en <html> ("" en la portada, "../" en subcarpetas). */
(function () {
  const RAIZ = document.documentElement.dataset.raiz || "";
  const ICONO_YT = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>';
  const NIVELES = { 1: "Nivel básico", 2: "Nivel medio", 3: "Nivel avanzado" };
  const TEMAS = { metrologia: "Metrología", mecanica: "Mecánica", electricidad: "Electricidad" };

  // Saca el identificador de un enlace de YouTube (watch, youtu.be, shorts, embed)
  function idVideo(url) {
    if (!url) return "";
    const m = url.match(/(?:youtu\.be\/|v=|shorts\/|embed\/|live\/)([A-Za-z0-9_-]{11})/);
    return m ? m[1] : "";
  }
  const canalSuscribir = c => c ? c.replace(/\/+$/, "") + "?sub_confirmation=1" : "";

  // Enlaces marcados con data-yt="canal" o data-yt="suscribir"
  function enlazarCanal(canal) {
    document.querySelectorAll("[data-yt]").forEach(a => {
      const url = a.dataset.yt === "suscribir" ? canalSuscribir(canal) : canal;
      if (url) {
        a.href = url; a.target = "_blank"; a.rel = "noopener";
        a.removeAttribute("aria-disabled"); a.removeAttribute("title");
      } else {
        a.removeAttribute("href");
        a.setAttribute("aria-disabled", "true");
        a.title = "El canal se enlazará muy pronto";
      }
    });
  }

  function tarjeta(item, conVideo) {
    const div = document.createElement("article");
    div.className = "tarjeta";
    const vid = idVideo(item.video);
    div.innerHTML =
      `<h3><span class="em" aria-hidden="true">${item.icono || "🔧"}</span>${item.titulo}</h3>
       <div class="etiquetas"><span>${TEMAS[item.tema] || item.tema}</span><span>${NIVELES[item.nivel] || ""}</span></div>
       <p>${item.descripcion || ""}</p>
       ${conVideo && vid ? `<div class="video"><iframe loading="lazy" title="Vídeo: ${item.titulo}" src="https://www.youtube-nocookie.com/embed/${vid}" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>` : ""}
       <div class="botones">
         <a class="btn prim" href="${RAIZ + item.archivo}">Abrir instrumento</a>
         ${item.video ? `<a class="btn yt" href="${item.video}" target="_blank" rel="noopener">${ICONO_YT} Ver el vídeo</a>`
                      : `<span class="btn" aria-disabled="true" title="El vídeo de este instrumento aún no está publicado">${ICONO_YT} Vídeo próximamente</span>`}
       </div>`;
    return div;
  }

  // Página de vídeos: una sección por tema
  function pintarTemas(datos) {
    document.querySelectorAll("[data-temas]").forEach(cont => {
      cont.innerHTML = "";
      [...new Set(datos.items.map(i => i.tema))].forEach(t => {
        const sec = document.createElement("section");
        sec.className = "seccion";
        sec.innerHTML = `<h2>${TEMAS[t] || t}</h2><div class="rejilla" data-lista="${t}" data-videos></div>`;
        cont.appendChild(sec);
      });
    });
  }

  function pintarListas(datos) {
    document.querySelectorAll("[data-lista]").forEach(cont => {
      const tema = cont.dataset.lista;
      const items = datos.items.filter(i => tema === "todos" || i.tema === tema);
      cont.innerHTML = "";
      items.forEach(i => cont.appendChild(tarjeta(i, cont.hasAttribute("data-videos"))));
    });
  }

  fetch(RAIZ + "contenido.json", { cache: "no-cache" })
    .then(r => r.json())
    .then(datos => { enlazarCanal(datos.canal || ""); pintarTemas(datos); pintarListas(datos); })
    .catch(() => {
      enlazarCanal("");
      document.querySelectorAll("[data-lista]").forEach(c =>
        c.innerHTML = '<p class="aviso">No se ha podido cargar la lista. Abre la web desde su dirección en internet.</p>');
    });

  // App instalable: guarda la web para usarla sin conexión
  if ("serviceWorker" in navigator && location.protocol.startsWith("http"))
    navigator.serviceWorker.register(RAIZ + "sw.js").catch(() => {});
})();
