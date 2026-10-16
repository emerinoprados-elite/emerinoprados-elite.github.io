# Web de Eduardo Merino (fases 1 y 2)

Web estática para GitHub Pages: HTML, CSS y JS propios, sin frameworks.

## Huecos por rellenar (solo en estos dos sitios)

1. **`contenido.json`**
   - `"canal"`: URL del canal, por ejemplo `https://www.youtube.com/@TuNombre`. Activa todos los botones de YouTube y "Suscríbete".
   - `"video"` de cada instrumento: URL del vídeo cuando esté publicado. Activa "Ver el vídeo" y lo inserta en el catálogo.
   - `"web"`: dirección final, por ejemplo `https://emerinoprados-elite.github.io/` (informativo).
2. **`const WEB_PERSONAL = ""`** en cada archivo de `instrumentos/`: la misma dirección de la web. Hace que el instrumento, descargado como archivo suelto, siga enlazando con la web y su vídeo. Dentro de la web ya funciona aunque esté vacía.

## Estructura

```
index.html                 Portada
instrumentos/index.html    Catálogo (se genera desde contenido.json)
instrumentos/*.html        Los tres instrumentos (cada uno funciona offline como archivo suelto)
sobre-mi/index.html        Sobre mí, contacto y privacidad
videos/index.html          Vídeos por tema (desde contenido.json)
progreso/index.html        Modo juego: nivel, insignias, racha diaria, copia de seguridad
manifest.webmanifest       App instalable (PWA)
sw.js                      Funcionamiento sin conexión
assets/                    Estilos, script común, logo (SVG y PNG) y marca de agua
contenido.json             Fuente única de instrumentos, vídeos y canal
404.html, .nojekyll        Para GitHub Pages
```

Para añadir un instrumento: copiar el HTML a `instrumentos/` y añadir su entrada en `contenido.json`.

## Modo juego

`assets/juego.js` guarda en `localStorage` (clave `em-progreso-v1`) los aciertos de los retos. Puntos por acierto: calibre 10, centesimal 15, milesimal 20, más premio cada 5 seguidos. Niveles: Aprendiz 0, Oficial 300, Maestro 1000, Élite 2500. Las insignias se definen en ese mismo archivo. Solo cuenta dentro de la web; el instrumento suelto funciona igual pero no guarda progreso.

## Al cambiar archivos

Sube `VERSION` en `sw.js` (em-v1 → em-v2…) para que los móviles con la app instalada descarguen lo nuevo. Si añades una página, añádela también a `ARCHIVOS` en `sw.js`.
