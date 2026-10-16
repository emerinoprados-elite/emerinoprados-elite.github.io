# Web de Eduardo Merino

Web estática para GitHub Pages: HTML, CSS y JS propios, sin frameworks.

## Huecos por rellenar (solo en estos dos sitios)

1. **`contenido.json`**
   - `"canal"`: URL del canal, por ejemplo `https://www.youtube.com/@TuNombre`. Activa todos los botones de YouTube y "Suscríbete".
   - `"video"` de cada instrumento: URL del vídeo cuando esté publicado. Activa "Ver el vídeo" y lo inserta en el catálogo.
   - `"web"`: dirección final, por ejemplo `https://emerinoprados-elite.github.io/` (informativo).
2. **`const WEB_PERSONAL = ""`** en cada archivo de `instrumentos/`: la misma dirección de la web. Hace que el instrumento, descargado como archivo suelto, siga enlazando con la web y su vídeo. Dentro de la web ya funciona aunque esté vacía.

## Cómo se actualiza

Todo el texto de la web sale de **`contenido.json`** (secciones, herramientas, guías, vídeos). Tras cambiarlo:

```
python3 herramientas/og.py        # imágenes para compartir (solo si hay herramientas nuevas; necesita Pillow)
python3 herramientas/generar.py   # regenera páginas, SEO, sitemap, robots, llms.txt y sw.js
```

El generador escribe el contenido directamente en el HTML (no depende de JavaScript), así lo leen Google, Bing y los asistentes de IA.

- **Secciones**: instrumentos, motor, mecánica, electricidad y juegos. Una sección sin herramientas sale como «En preparación» con `noindex` y no entra en el sitemap hasta que tenga contenido.
- **Herramienta nueva**: copiar su HTML a la carpeta de su sección (por ejemplo `motor/ciclo-4-tiempos.html`), añadir su entrada en `items` con `seccion`, `seo_titulo`, `seo_descripcion` y `guia`, y ejecutar el generador. En el HTML de la herramienta se insertan dos bloques entre marcadores (`seo:inicio/fin` en la cabecera y `guia:inicio/fin` antes del `<footer>`); no editarlos a mano.
- **Vídeo publicado**: rellenar `video` (URL) y `fecha_video` (AAAA-MM-DD) del item. Con ambos se añaden los datos estructurados del vídeo.
- **Google Search Console / Bing**: pegar el código de verificación en `verificacion_google` / `verificacion_bing`.
- Para que cuente en el modo juego, añadir el id y sus puntos en `assets/juego.js`.

## Archivos para buscadores e IA (generados)

`sitemap.xml`, `robots.txt` (abierto a buscadores y crawlers de IA), `llms.txt` (resumen para IA), `llms-full.txt` (texto completo de las guías), `assets/og/` (imágenes 1200×630) y datos schema.org en cada página. `herramientas/fechas.json` guarda la fecha real de cambio de cada página para el sitemap.
