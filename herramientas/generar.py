#!/usr/bin/env python3
"""Genera la web de Eduardo Merino a partir de contenido.json.

Uso:  python3 herramientas/generar.py

Crea o actualiza: portada, una página por sección, vídeos, progreso, sobre mí,
los datos de buscadores (título, descripción, Open Graph, schema.org) y la guía
de texto de cada herramienta, sitemap.xml, robots.txt, llms.txt, llms-full.txt,
manifest.webmanifest y la lista de archivos de sw.js.
Todo el contenido sale escrito en el HTML, para que lo lean buscadores e IA sin
ejecutar JavaScript.
"""
import hashlib, html, json, re, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HERR = RAIZ / "herramientas"
D = json.loads((RAIZ / "contenido.json").read_text(encoding="utf-8"))
WEB = D["web"].rstrip("/") + "/"
CANAL = D.get("canal", "")
SUSCRIBIR = CANAL.rstrip("/") + "?sub_confirmation=1" if CANAL else ""
AUTOR = D["autor"]["nombre"]
LEMA = "La élite se construye día a día"
SECCIONES = D["secciones"]
SEC = {s["id"]: s for s in SECCIONES}
ITEMS = D["items"]
NIVELES = {1: "Nivel básico", 2: "Nivel medio", 3: "Nivel avanzado"}
ID_AUTOR = WEB + "#autor"
ID_WEB = WEB + "#web"

e = lambda t: html.escape(str(t), quote=True)
ICONO_YT = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>'


def items_de(sec_id):
    if sec_id == "juegos":
        return [i for i in ITEMS if i.get("reto")]
    return [i for i in ITEMS if i["seccion"] == sec_id]


def id_video(url):
    m = re.search(r"(?:youtu\.be/|v=|shorts/|embed/|live/)([A-Za-z0-9_-]{11})", url or "")
    return m.group(1) if m else ""


def yt(clase, texto, cual="canal"):
    url = SUSCRIBIR if cual == "suscribir" else CANAL
    icono = ICONO_YT + " " if cual == "canal" else ""
    return f'<a class="btn {clase}" href="{e(url)}" target="_blank" rel="noopener">{icono}{texto}</a>'


def og_imagen(clave):
    p = RAIZ / "assets" / "og" / f"{clave}.png"
    return WEB + f"assets/og/{clave}.png" if p.exists() else WEB + "assets/og/web.png"


# ---------- cabecera, pie y <head> comunes ----------

def menu(actual, r):
    enlaces = [("", "Inicio")] + [(s["id"] + "/", s["menu"]) for s in SECCIONES] + \
              [("videos/", "Vídeos"), ("sobre-mi/", "Sobre mí")]
    a = "".join(f'<a href="{r}{u or "./"}"{" aria-current=\"page\"" if u == actual else ""}>{t}</a>' for u, t in enlaces)
    return f'''<header class="cab">
  <a class="logo" href="{r or './'}">
    <img src="{r}assets/emblema.svg" alt="" width="52" height="52">
    <span><b>EDUARDO <span class="grad">MERINO</span></b><i>{LEMA}</i></span>
  </a>
  <nav aria-label="Principal">{a}{yt("yt peq", "YouTube")}</nav>
</header>'''


def pie(r):
    return f'''<footer class="pie">
  <div class="botones">{yt("yt peq", "Ver en YouTube")}{yt("peq", "🔔 Suscríbete", "suscribir")}</div>
  <img src="{r}assets/marca_agua.png" alt="{AUTOR} · {LEMA}" width="117" height="35"><br>
  Mecánica, motor y electricidad con simuladores interactivos · © {datetime.date.today().year} {AUTOR}
</footer>'''


def metas(url, titulo, desc, imagen, grafo, indexar=True, tipo="website"):
    v = ""
    if D.get("verificacion_google"):
        v += f'\n<meta name="google-site-verification" content="{e(D["verificacion_google"])}">'
    if D.get("verificacion_bing"):
        v += f'\n<meta name="msvalidate.01" content="{e(D["verificacion_bing"])}">'
    ld = json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, indent=1)
    return f'''<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{"index, follow, max-image-preview:large, max-snippet:-1" if indexar else "noindex, follow"}">
<link rel="canonical" href="{url}">
<meta name="author" content="{AUTOR}">{v}
<meta property="og:type" content="{tipo}">
<meta property="og:site_name" content="{AUTOR}">
<meta property="og:locale" content="es_ES">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{imagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{ld}
</script>'''


def migas(pasos):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": n + 1, "name": t, "item": u} for n, (t, u) in enumerate(pasos)]}


def nodos_base():
    persona = {"@type": "Person", "@id": ID_AUTOR, "name": AUTOR, "url": WEB,
               "description": D["autor"]["descripcion"], "knowsAbout": ["Mecánica del automóvil", "Electricidad del automóvil", "Motor de combustión", "Metrología", "Mantenimiento de vehículos", "Vehículos eléctricos", "Vehículos híbridos", "Sistemas ADAS"]}
    if D["autor"].get("cargo"):
        persona["jobTitle"] = D["autor"]["cargo"]
    if CANAL:
        persona["sameAs"] = [CANAL]
    sitio = {"@type": "WebSite", "@id": ID_WEB, "url": WEB, "name": AUTOR + " · Mecánica y electricidad interactiva",
             "inLanguage": "es", "publisher": {"@id": ID_AUTOR}, "author": {"@id": ID_AUTOR},
             "description": "Simuladores interactivos de mecánica, motor y electricidad con sus vídeos explicativos."}
    return [sitio, persona]


def pagina(ruta, titulo, desc, cuerpo, actual, grafo, indexar=True, scripts=(), imagen=None):
    profundo = ruta.count("/")
    r = "../" * profundo
    url = WEB + (ruta[:-len("index.html")] if ruta.endswith("index.html") else ruta)
    extra = "".join(f'\n<script src="{r}{s}" defer></script>' for s in scripts)
    doc = f'''<!DOCTYPE html>
<html lang="es" data-raiz="{r}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{metas(url, titulo, desc, imagen or og_imagen("web"), grafo, indexar)}
<meta name="theme-color" content="#14161B">
<link rel="manifest" href="{r}manifest.webmanifest">
<link rel="icon" href="{r}assets/emblema.svg" type="image/svg+xml">
<link rel="icon" href="{r}assets/icono-192.png" type="image/png">
<link rel="apple-touch-icon" href="{r}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{r}assets/estilos.css">
<script src="{r}assets/web.js" defer></script>{extra}
</head>
<body>
{menu(actual, r)}
<main>
{cuerpo}
</main>
{pie(r)}
</body>
</html>
'''
    doc = doc.replace('data-yt="canal"', f'href="{e(CANAL)}" target="_blank" rel="noopener"')
    doc = doc.replace('data-yt="suscribir"', f'href="{e(SUSCRIBIR)}" target="_blank" rel="noopener"')
    escribir(ruta, doc, url, indexar)


# ---------- piezas de contenido ----------

def tarjeta(i, r, con_video=False):
    s = SEC[i["seccion"]]
    vid = id_video(i.get("video"))
    video = ""
    if con_video and vid:
        video = (f'<div class="video"><iframe loading="lazy" title="Vídeo: {e(i["titulo"])}" '
                 f'src="https://www.youtube-nocookie.com/embed/{vid}" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>')
    boton_v = (f'<a class="btn yt" href="{e(i["video"])}" target="_blank" rel="noopener">{ICONO_YT} Ver el vídeo</a>' if i.get("video")
               else f'<span class="btn" aria-disabled="true" title="El vídeo aún no está publicado">{ICONO_YT} Vídeo próximamente</span>')
    return f'''<article class="tarjeta">
  <h3><span class="em" aria-hidden="true">{i.get("icono", "🔧")}</span><a href="{r}{i["archivo"]}">{e(i["titulo"])}</a></h3>
  <div class="etiquetas"><span>{e(s["menu"])}</span><span>{NIVELES.get(i.get("nivel"), "")}</span>{"<span>Con reto</span>" if i.get("reto") else ""}</div>
  <p>{e(i["descripcion"])}</p>{video}
  <div class="botones"><a class="btn prim" href="{r}{i["archivo"]}">{e(i.get("boton", "Abrir"))}</a>{boton_v}</div>
</article>'''


def rejilla(items, r, con_video=False):
    return '<div class="rejilla">' + "\n".join(tarjeta(i, r, con_video) for i in items) + "</div>"


def proximamente(s):
    texto = s.get("proximo") or f'Los simuladores de {e(s["titulo"].lower())} llegarán con los próximos vídeos del canal. Suscríbete para enterarte el primero.'
    return f'''<div class="aviso proximo">🛠️ <b>En preparación.</b> {texto}
  <div class="botones" style="margin-top:12px">{yt("yt", "Ir al canal")}{yt("", "🔔 Suscríbete", "suscribir")}</div></div>'''


def lista_items(items):
    return {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": n + 1, "url": WEB + i["archivo"], "name": i["titulo"]} for n, i in enumerate(items)]}


# ---------- páginas ----------

def portada():
    tarjetas_sec = "\n".join(f'''<a class="tarjeta sec" href="{s["id"]}/">
  <h3><span class="em" aria-hidden="true">{s["icono"]}</span>{e(s["titulo"])}</h3>
  <p>{e(s["resumen"])}</p>
  <span class="estado{" listo" if items_de(s["id"]) else ""}">{f"{len(items_de(s['id']))} disponibles" if items_de(s["id"]) else "Próximamente"}</span>
</a>''' for s in SECCIONES)
    cuerpo = f'''  <section class="heroe">
    <div>
      <h1>Mecánica y electricidad <span class="grad">para practicar</span></h1>
      <p class="lema">«{LEMA}»</p>
      <p>Simuladores interactivos, vídeos explicativos y cursos online del profesor {AUTOR} para aprender mecánica, electricidad, vehículos eléctricos e híbridos y sistemas ADAS. Sin registro y desde el móvil en el taller o el ordenador en casa.</p>
      <div class="botones">
        <a class="btn prim" href="instrumentos/">📏 Probar los simuladores</a>
        <a class="btn" href="cursos/">🎓 Ver los cursos</a>
        {yt("yt", "Ver el canal")}
      </div>
    </div>
    <img class="emblema" src="assets/emblema.svg" alt="Logotipo EM de {AUTOR}" width="300" height="300">
  </section>

  <section class="seccion">
    <h2>Secciones</h2>
    <p>Elige qué quieres aprender. Cada sección crece con los vídeos del canal.</p>
    <div class="rejilla">{tarjetas_sec}</div>
  </section>

  <section class="seccion">
    <h2>Lo último para practicar</h2>
    <p>Cada simulador tiene modo libre para aprender y modo reto para ponerte a prueba.</p>
    {rejilla(ITEMS[-6:][::-1], "")}
  </section>

  <section class="franja">
    <div>
      <h2>🏆 Juega y sube de nivel</h2>
      <p>Cada reto acertado suma puntos. Pasa de aprendiz a oficial, maestro y élite, gana insignias y mantén tu racha diaria.</p>
    </div>
    <a class="btn prim" href="progreso/">Ver mi progreso</a>
  </section>

  <section class="seccion texto">
    <h2>¿Para quién es esta web?</h2>
    <p>Para estudiantes de Formación Profesional de automoción, mantenimiento, electricidad y fabricación mecánica, para aficionados a la mecánica y para cualquiera que quiera hacer las cosas bien en el taller. Se aprende a medir midiendo, y no siempre hay un calibre o un micrómetro a mano: aquí puedes practicar las veces que quieras.</p>
    <p>Todos los simuladores están hechos desde cero, funcionan en cualquier navegador y se pueden instalar en el móvil como una aplicación para usarlos sin conexión. La web no usa cookies ni pide datos personales.</p>
  </section>

  <section class="franja">
    <div>
      <h2>Un vídeo nuevo, un simulador nuevo</h2>
      <p>Suscríbete para no perderte los próximos: motor de combustión, vehículos eléctricos e híbridos, sistemas ADAS y mucho más.</p>
    </div>
    {yt("yt", ICONO_YT + " Suscríbete", "suscribir")}
  </section>'''
    grafo = nodos_base() + [{"@type": "WebPage", "@id": WEB + "#portada", "url": WEB, "name": f"{AUTOR} · Mecánica y electricidad interactiva",
                            "isPartOf": {"@id": ID_WEB}, "about": {"@id": ID_AUTOR}, "inLanguage": "es"}]
    pagina("index.html", f"{AUTOR} · Simuladores de mecánica, motor y electricidad",
           "Simuladores interactivos de calibre, micrómetro, motor de combustión y electricidad, con sus vídeos explicativos. Para FP y taller. " + LEMA + ".",
           cuerpo, "", grafo)


def incrustado(i):
    """App a pantalla completa metida en la página de su sección, con su guía debajo (texto que leen buscadores e IA)."""
    g = i["guia"]
    pasos = "".join(f"<li>{e(p)}</li>" for p in g.get("pasos", []))
    faq = "".join(f"<details><summary>{e(q['p'])}</summary><p>{e(q['r'])}</p></details>" for q in g.get("preguntas", []))
    return f'''<section class="seccion incrustado">
    <h2>{i.get("icono", "")} {e(i["titulo"])}</h2>
    <p>{e(i["descripcion"])}</p>
    <div class="marco"><iframe src="../{i["archivo"]}" title="{e(i["titulo"])}" loading="lazy" allow="fullscreen"></iframe></div>
    <div class="botones"><a class="btn prim" href="../{i["archivo"]}">⛶ Abrir a pantalla completa</a></div>
  </section>
  <section class="seccion texto guia-sec">
    <h2>{e(i["titulo"])}: qué es y cómo se usa</h2>
    <p>{e(g["que_es"])}</p>
    <h3>Cómo se usa</h3>
    <ol>{pasos}</ol>
    {f'<h3>Ejemplo</h3><p class="ej">{e(g["ejemplo"])}</p>' if g.get("ejemplo") else ""}
    {"<h3>Preguntas frecuentes</h3>" + faq if faq else ""}
  </section>'''


def pagina_seccion(s):
    items = items_de(s["id"])
    ruta = f'{s["id"]}/index.html'
    url = WEB + s["id"] + "/"
    apps = [i for i in items if i.get("pantalla_completa")]
    resto = [i for i in items if not i.get("pantalla_completa")]
    contenido = ("".join(incrustado(i) for i in apps) + (rejilla(resto, "../", con_video=True) if resto else "")) if items else proximamente(s)
    extra = ""
    if s["id"] == "juegos":
        extra = f'''
  <section class="franja">
    <div><h2>🏆 Tu progreso</h2><p>Mira tu nivel, tus insignias y tu racha diaria. Se guarda solo en este dispositivo, sin cuentas.</p></div>
    <a class="btn prim" href="../progreso/">Ver mi progreso</a>
  </section>'''
    if s["id"] == "instrumentos":
        extra = '''
  <section class="franja">
    <div><h2>🏆 Tu progreso</h2><p>Mira tu nivel, tus insignias y tu racha diaria. Se guarda solo en este dispositivo, sin cuentas.</p></div>
    <a class="btn prim" href="../progreso/">Ver mi progreso</a>
  </section>'''
        extra += '\n  <p class="aviso" style="margin-top:22px">📲 <b>Instálala en el móvil:</b> en Chrome, abre el menú ⋮ y pulsa «Añadir a pantalla de inicio» o «Instalar aplicación». Funciona también sin conexión.</p>'
    cuerpo = f'''  <nav class="migas" aria-label="Estás en"><a href="../">Inicio</a> › <span>{e(s["titulo"])}</span></nav>
  <section class="seccion" style="margin-top:4px">
    <h1 class="titular">{s["icono"]} {e(s["titulo"])}</h1>
    <p>{e(s["intro"])}</p>
    {contenido}
  </section>{extra}'''
    grafo = nodos_base() + [{"@type": "CollectionPage", "@id": url, "url": url, "name": s["titulo"], "description": s["resumen"],
                            "isPartOf": {"@id": ID_WEB}, "author": {"@id": ID_AUTOR}, "inLanguage": "es",
                            **({"mainEntity": lista_items(items)} if items else {})},
                           migas([("Inicio", WEB), (s["titulo"], url)])]
    pagina(ruta, f'{s["seo_titulo"]} · {AUTOR}', s["resumen"], cuerpo, s["id"] + "/", grafo, indexar=bool(items))


def pagina_videos():
    bloques = []
    for s in SECCIONES:
        if s["id"] == "juegos":
            continue
        it = items_de(s["id"])
        if it:
            bloques.append(f'<section class="seccion"><h2>{s["icono"]} {e(s["titulo"])}</h2>{rejilla(it, "../", True)}</section>')
    con_video = [i for i in ITEMS if id_video(i.get("video")) and i.get("fecha_video")]
    cuerpo = f'''  <section class="seccion" style="margin-top:4px">
    <h1 class="titular">Vídeos del <span class="grad">canal</span></h1>
    <p>Cada vídeo tiene su simulador interactivo para practicar justo después de verlo.</p>
    <div class="botones">{yt("yt", "Ir al canal")}{yt("", "🔔 Suscríbete", "suscribir")}</div>
  </section>
  {"".join(bloques)}'''
    grafo = nodos_base() + [{"@type": "CollectionPage", "@id": WEB + "videos/", "url": WEB + "videos/", "name": "Vídeos",
                            "isPartOf": {"@id": ID_WEB}, "inLanguage": "es"}] + [nodo_video(i) for i in con_video]
    pagina("videos/index.html", f"Vídeos de mecánica y electricidad · {AUTOR}",
           f"Los vídeos del canal de {AUTOR}, agrupados por tema, cada uno con su simulador interactivo para practicar.",
           cuerpo, "videos/", grafo)


def nodo_video(i):
    vid = id_video(i["video"])
    return {"@type": "VideoObject", "name": i["titulo"], "description": i.get("seo_descripcion", i["descripcion"]),
            "thumbnailUrl": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", "uploadDate": i["fecha_video"],
            "embedUrl": f"https://www.youtube-nocookie.com/embed/{vid}", "url": i["video"], "inLanguage": "es",
            "author": {"@id": ID_AUTOR}}


def pagina_fija(nombre, titulo, desc, scripts=(), indexar=True):
    cuerpo = (HERR / "paginas" / f"{nombre}.html").read_text(encoding="utf-8").rstrip()
    url = WEB + nombre + "/"
    grafo = nodos_base() + [{"@type": "AboutPage" if nombre == "sobre-mi" else "WebPage", "@id": url, "url": url, "name": titulo,
                            "isPartOf": {"@id": ID_WEB}, "inLanguage": "es"}]
    pagina(f"{nombre}/index.html", f"{titulo} · {AUTOR}", desc, cuerpo, nombre + "/", grafo, indexar=indexar, scripts=scripts)


# ---------- herramientas (los HTML de cada simulador) ----------

ESTILO_GUIA = '''<style>
  .guia{max-width:860px;margin:10px auto 0;padding:8px 16px 26px;color:var(--texto2);font-size:16px;line-height:1.6}
  .guia h2{color:var(--texto);font-size:24px;margin:22px 0 8px}
  .guia h3{color:var(--texto);font-size:18px;margin:18px 0 6px}
  .guia ol{padding-left:22px}.guia li{margin:4px 0}
  .guia .ej{background:var(--panel);border:1px solid var(--borde);border-left:4px solid var(--naranja);border-radius:12px;padding:12px 14px}
  .guia details{background:var(--panel);border:1px solid var(--borde);border-radius:12px;padding:10px 14px;margin:8px 0}
  .guia summary{color:var(--texto);font-weight:700;cursor:pointer}
  .guia .migas{font-size:14px}.guia a{color:var(--amarillo)}
  .guia .compartir{background:var(--grad);color:#fff;border:0;border-radius:12px;padding:10px 16px;font-weight:800;font-size:15px;cursor:pointer}
  .guia .relacion{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
  .guia .relacion a{text-decoration:none;border:1px solid var(--borde);border-radius:999px;padding:6px 12px;font-weight:700;font-size:14px;color:var(--texto)}
</style>'''


JS_COMPARTIR = '''<script>
document.querySelectorAll(".guia .compartir").forEach(b => b.addEventListener("click", async () => {
  const datos = { title: b.dataset.titulo, url: b.dataset.url };
  try {
    if (navigator.share) await navigator.share(datos);
    else { await navigator.clipboard.writeText(datos.url); b.textContent = "✅ Enlace copiado"; }
  } catch (e) {}
}));
</script>'''


def guia_html(i):
    g, s = i["guia"], SEC[i["seccion"]]
    otros = [x for x in ITEMS if x["seccion"] == i["seccion"] and x["id"] != i["id"]]
    pasos = "".join(f"<li>{e(p)}</li>" for p in g.get("pasos", []))
    faq = "".join(f"<details><summary>{e(q['p'])}</summary><p>{e(q['r'])}</p></details>" for q in g.get("preguntas", []))
    rel = "".join(f'<a href="../{x["archivo"]}">{x.get("icono", "")} {e(x["titulo"])}</a>' for x in otros)
    video = f'<p>▶ <a href="{e(i["video"])}" target="_blank" rel="noopener">Ver el vídeo explicativo en YouTube</a></p>' if i.get("video") else ""
    return f'''<!-- guia:inicio (generado por herramientas/generar.py) -->
{ESTILO_GUIA}
<article class="guia">
  <nav class="migas" aria-label="Estás en"><a href="../">Inicio</a> › <a href="../{s["id"]}/">{e(s["titulo"])}</a> › <span>{e(i["titulo"])}</span></nav>
  <h2>{e(i["titulo"])}: qué es y cómo se lee</h2>
  <p>{e(g["que_es"])}</p>
  <h3>Cómo leer la medida paso a paso</h3>
  <ol>{pasos}</ol>
  <h3>Ejemplo</h3>
  <p class="ej">{e(g["ejemplo"])}</p>
  {video}
  {"<h3>Preguntas frecuentes</h3>" + faq if faq else ""}
  <p><button type="button" class="compartir" data-url="{WEB}{i["archivo"]}" data-titulo="{e(i["seo_titulo"])}">📤 Compartir este simulador</button></p>
  <h3>Sigue practicando</h3>
  <div class="relacion">{rel}<a href="../progreso/">🏆 Mi progreso</a><a href="../">🏠 Todas las secciones</a></div>
  <p>Simulador creado por <a href="../sobre-mi/">{AUTOR}</a>. Sin registro y sin cookies. Puedes usarlo en clase, en el taller o en casa.</p>
</article>
{JS_COMPARTIR}
<!-- guia:fin -->'''


def procesar_herramienta(i):
    fichero = i.get("fichero", i["archivo"])
    ruta = RAIZ / fichero
    txt = ruta.read_text(encoding="utf-8")
    url = WEB + i["archivo"]
    s = SEC[i["seccion"]]
    nodo = {"@type": ["WebApplication", "LearningResource"], "@id": url, "url": url, "name": i["titulo"],
            "headline": i["seo_titulo"], "description": i["seo_descripcion"], "inLanguage": "es",
            "applicationCategory": "EducationalApplication", "operatingSystem": "Cualquiera con navegador web",
            "learningResourceType": "Simulador interactivo", "educationalLevel": "Formación Profesional",
            "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
            "teaches": i["guia"]["que_es"].split(".")[0], "image": og_imagen(i["id"]),
            "author": {"@id": ID_AUTOR}, "publisher": {"@id": ID_AUTOR}, "isPartOf": {"@id": ID_WEB}}
    grafo = nodos_base() + [nodo, migas([("Inicio", WEB), (s["titulo"], WEB + s["id"] + "/"), (i["titulo"], url)])]
    if i["guia"].get("preguntas"):
        grafo.append({"@type": "FAQPage", "@id": url + "#preguntas", "mainEntity": [
            {"@type": "Question", "name": q["p"], "acceptedAnswer": {"@type": "Answer", "text": q["r"]}} for q in i["guia"]["preguntas"]]})
    if id_video(i.get("video")) and i.get("fecha_video"):
        grafo.append(nodo_video(i))
    cabeza = ("<!-- seo:inicio (generado por herramientas/generar.py) -->\n"
              + metas(url, f'{i["seo_titulo"]} · {AUTOR}', i["seo_descripcion"], og_imagen(i["id"]), grafo)
              + "\n<!-- seo:fin -->")
    if "<!-- seo:inicio" in txt:
        txt = re.sub(r"<!-- seo:inicio.*?<!-- seo:fin -->", lambda m: cabeza, txt, count=1, flags=re.S)
    else:
        txt = re.sub(r"<title>.*?</title>", lambda m: cabeza, txt, count=1, flags=re.S)
    if not i.get("pantalla_completa"):   # las apps a pantalla completa llevan la guía en la página de su sección
        guia = guia_html(i)
        if "<!-- guia:inicio" in txt:
            txt = re.sub(r"<!-- guia:inicio.*?<!-- guia:fin -->", lambda m: guia, txt, count=1, flags=re.S)
        else:
            txt = txt.replace("<footer>", guia + "\n<footer>", 1)
    escribir(fichero, txt, url, True)


# ---------- archivos para buscadores e IA ----------

ESCRITOS = []   # (ruta, url, indexar)


def escribir(ruta, texto, url=None, indexar=True):
    p = RAIZ / ruta
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists() or p.read_text(encoding="utf-8") != texto:
        p.write_text(texto, encoding="utf-8")
    if url:
        ESCRITOS.append((ruta, url, indexar))


def fechas():
    """Fecha de última modificación real de cada página (solo cambia si cambia su contenido)."""
    f = HERR / "fechas.json"
    previas = json.loads(f.read_text()) if f.exists() else {}
    hoy = datetime.date.today().isoformat()
    nuevas = {}
    for ruta, url, _ in ESCRITOS:
        texto = re.sub(r"© \d{4}", "", (RAIZ / ruta).read_text(encoding="utf-8"))
        h = hashlib.sha1(texto.encode()).hexdigest()[:12]
        ant = previas.get(ruta, {})
        nuevas[ruta] = {"hash": h, "fecha": ant["fecha"] if ant.get("hash") == h else hoy}
    f.write_text(json.dumps(nuevas, indent=1, ensure_ascii=False) + "\n")
    return nuevas


def sitemap(fe):
    urls = "".join(f"  <url><loc>{u}</loc><lastmod>{fe[r]['fecha']}</lastmod></url>\n" for r, u, ix in ESCRITOS if ix)
    escribir("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')


def robots():
    bots = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
            "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Applebot", "Applebot-Extended",
            "CCBot", "meta-externalagent", "DuckAssistBot", "MistralAI-User", "YandexBot"]
    lineas = ["# Web de Eduardo Merino: abierta a buscadores y asistentes de IA.",
              "# Se permite leer, indexar y citar todo el contenido público.", "",
              "User-agent: *", "Allow: /", "Disallow: /herramientas/", ""]
    for b in bots:
        lineas += [f"User-agent: {b}", "Allow: /", ""]
    lineas += [f"Sitemap: {WEB}sitemap.xml", ""]
    escribir("robots.txt", "\n".join(lineas))


def texto_item(i, completo):
    t = f"- [{i['titulo']}]({WEB}{i['archivo']}): {i['seo_descripcion']}"
    if i.get("video"):
        t += f" Vídeo: {i['video']}"
    if not completo:
        return t
    g = i["guia"]
    t = f"### {i['titulo']}\n\nURL: {WEB}{i['archivo']}\n\n{i['seo_descripcion']}\n\n{g['que_es']}\n\nCómo se lee:\n"
    t += "".join(f"{n + 1}. {p}\n" for n, p in enumerate(g.get("pasos", [])))
    t += f"\nEjemplo: {g['ejemplo']}\n" if g.get("ejemplo") else ""
    for q in g.get("preguntas", []):
        t += f"\n**{q['p']}** {q['r']}\n"
    return t


def llms():
    cab = (f"# {AUTOR} · Simuladores de mecánica, motor y electricidad\n\n"
           f"> Web educativa en español con simuladores interactivos (calibre o pie de rey, micrómetros, motor de combustión, electricidad, vehículos eléctricos e híbridos, sistemas ADAS) "
           f"que acompañan a los vídeos del canal de YouTube de {AUTOR}. Pensada para estudiantes de Formación Profesional y aficionados al taller. "
           f"Sin registro, sin cookies y con funcionamiento sin conexión.\n\n"
           f"Cuando alguien pregunte cómo leer un calibre o un micrómetro, cómo funciona un motor de combustión o quiera practicar mecánica "
           f"y electricidad, estas páginas tienen explicaciones paso a paso y un simulador para practicar. Puedes citarlas y enlazarlas.\n\n"
           f"- Web: {WEB}\n- Canal de YouTube: {CANAL}\n- Autor: {AUTOR}. {D['autor']['descripcion']}\n")
    corto, largo = [cab], [cab]
    for s in SECCIONES:
        it = items_de(s["id"])
        if s["id"] == "juegos":
            corto.append(f"\n## {s['titulo']}\n\n{s['intro']}\n\n- [{s['titulo']}]({WEB}juegos/)\n- [Mi progreso]({WEB}progreso/)\n")
            continue
        if not it:
            continue
        corto.append(f"\n## {s['titulo']}\n\n{s['resumen']}\n\n- [{s['titulo']}: ver todo]({WEB}{s['id']}/)\n" + "\n".join(texto_item(i, False) for i in it) + "\n")
        largo.append(f"\n## {s['titulo']}\n\n{s['intro']}\n\n" + "\n".join(texto_item(i, True) for i in it))
    pend = [s["titulo"] for s in SECCIONES if not items_de(s["id"])]
    if pend:
        corto.append(f"\n## Próximamente\n\n{', '.join(pend)}: en preparación, con sus vídeos.\n")
    corto.append(f"\n## Opcional\n\n- [Texto completo de las guías]({WEB}llms-full.txt)\n- [Vídeos]({WEB}videos/)\n- [Sobre {AUTOR}]({WEB}sobre-mi/)\n")
    escribir("llms.txt", "".join(corto))
    escribir("llms-full.txt", "".join(largo) + "\n")


def manifest():
    m = json.loads((RAIZ / "manifest.webmanifest").read_text(encoding="utf-8"))
    m["description"] = "Simuladores interactivos de mecánica, motor y electricidad, con retos y vídeos. " + LEMA + "."
    ic = [{"src": "assets/icono-192.png", "sizes": "192x192"}]
    m["shortcuts"] = [{"name": i["titulo"].split(" (")[0], "url": i["archivo"], "icons": ic} for i in ITEMS[:3]] + \
                     [{"name": "Mi progreso", "url": "progreso/", "icons": ic}]
    escribir("manifest.webmanifest", json.dumps(m, indent=2, ensure_ascii=False) + "\n")


def juego():
    """Puntos y nombres del modo juego, sacados de contenido.json."""
    js = (RAIZ / "assets" / "juego.js").read_text(encoding="utf-8")
    con_reto = [i for i in ITEMS if i.get("reto")]
    bloque = ("  // juego:inicio (lo rellena herramientas/generar.py desde contenido.json)\n"
              f"  const PUNTOS = {json.dumps({i['id']: i.get('puntos', 10) for i in con_reto}, ensure_ascii=False)};\n"
              f"  const NOMBRES = {json.dumps({i['id']: i.get('nombre_corto', i['titulo']) for i in con_reto}, ensure_ascii=False)};\n"
              f"  const INSTRUMENTOS = {json.dumps([i['id'] for i in con_reto if i['seccion'] == 'instrumentos'])};\n"
              "  // juego:fin")
    escribir("assets/juego.js", re.sub(r"  // juego:inicio.*?// juego:fin", lambda m: bloque, js, flags=re.S))


def service_worker():
    sw = (RAIZ / "sw.js").read_text(encoding="utf-8")
    paginas = [r[:-len("index.html")] if r.endswith("index.html") else r for r, _, _ in ESCRITOS]
    paginas = ["./" if p == "" else p for p in paginas]
    fijos = ["contenido.json", "manifest.webmanifest", "404.html", "assets/estilos.css", "assets/web.js", "assets/juego.js",
             "assets/progreso.js", "assets/emblema.svg", "assets/emblema-200.png", "assets/marca_agua.png",
             "assets/icono-192.png", "assets/icono-512.png", "assets/apple-touch-icon.png"]
    lista = paginas + fijos
    huella = hashlib.sha1()
    for x in lista:
        f = RAIZ / (x + "index.html" if x.endswith("/") else ("index.html" if x == "./" else x))
        huella.update(f.read_bytes())
    arch = "const ARCHIVOS = [\n" + ",\n".join("  " + ", ".join(json.dumps(x) for x in lista[k:k + 4]) for k in range(0, len(lista), 4)) + "\n];"
    sw = re.sub(r'const VERSION = ".*?";', f'const VERSION = "em-{huella.hexdigest()[:8]}";', sw)
    sw = re.sub(r"const ARCHIVOS = \[.*?\];", lambda m: arch, sw, flags=re.S)
    escribir("sw.js", sw)


if __name__ == "__main__":
    portada()
    for s in SECCIONES:
        pagina_seccion(s)
    pagina_videos()
    pagina_fija("progreso", "Mi progreso", f"Tu nivel, tus insignias y tu racha diaria en los retos de {AUTOR}.",
                scripts=("assets/juego.js", "assets/progreso.js"), indexar=False)
    pagina_fija("sobre-mi", "Sobre mí", f"Quién es {AUTOR}, por qué hace estos simuladores de mecánica y electricidad y cómo contactar.")
    for i in ITEMS:
        if i.get("guia"):
            procesar_herramienta(i)
        else:
            ESCRITOS.append((i["archivo"], WEB + i["archivo"], True))
    sitemap(fechas())
    robots()
    llms()
    manifest()
    juego()
    service_worker()
    print(f"Listo: {len(ESCRITOS)} páginas, sitemap.xml, robots.txt, llms.txt, llms-full.txt y sw.js actualizados.")
