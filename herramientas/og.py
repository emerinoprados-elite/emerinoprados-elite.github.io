#!/usr/bin/env python3
"""Crea las imágenes para compartir (Open Graph, 1200×630) en assets/og/.
Uso: python3 herramientas/og.py   (necesita Pillow). Ejecutar antes de generar.py."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
D = json.loads((RAIZ / "contenido.json").read_text(encoding="utf-8"))
FUENTES = Path("/usr/share/fonts/opentype/inter")
W, H = 1200, 630


def fuente(nombre, t):
    try:
        return ImageFont.truetype(str(FUENTES / nombre), t)
    except OSError:
        return ImageFont.load_default(t)


def ajustar(d, texto, f, ancho):
    lineas, l = [], ""
    for p in texto.split():
        prueba = (l + " " + p).strip()
        if d.textlength(prueba, font=f) <= ancho:
            l = prueba
        else:
            lineas.append(l); l = p
    return lineas + [l]


def imagen(titulo, sub, salida, icono=""):
    im = Image.new("RGB", (W, H), "#14161B")
    halo = Image.new("RGB", (W, H), "#14161B")
    dh = ImageDraw.Draw(halo)
    dh.ellipse((-300, -400, 700, 400), fill="#4a2410")
    dh.ellipse((800, -200, 1600, 500), fill="#4a1630")
    im = Image.blend(im, halo.filter(ImageFilter.GaussianBlur(160)), 1)
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 14, W, H), fill="#FF6A2A")
    logo = Image.open(RAIZ / "assets" / "icono-512.png").convert("RGBA").resize((300, 300), Image.LANCZOS)
    im.paste(logo, (W - 360, 150), logo)
    d.text((70, 70), "EDUARDO MERINO", font=fuente("Inter-ExtraBold.otf", 34), fill="#FF7A1A")
    ft = fuente("Inter-Black.otf", 64)
    y = 140
    for l in ajustar(d, titulo, ft, 720)[:4]:
        d.text((70, y), l, font=ft, fill="#F4F5F7"); y += 76
    fs = fuente("Inter-Medium.otf", 30)
    y += 14
    for l in ajustar(d, sub, fs, 720)[:3]:
        d.text((70, y), l, font=fs, fill="#AEB4C2"); y += 40
    d.text((70, H - 80), "«La élite se construye día a día»", font=fuente("Inter-SemiBoldItalic.otf", 28), fill="#FFC23D")
    salida.parent.mkdir(parents=True, exist_ok=True)
    im.save(salida, optimize=True)


if __name__ == "__main__":
    og = RAIZ / "assets" / "og"
    imagen("Simuladores de mecánica, motor y electricidad", "Practica con los vídeos del canal", og / "web.png")
    for i in D["items"]:
        imagen(i["titulo"], "Simulador interactivo · Aprende paso a paso", og / f"{i['id']}.png")
    print("Imágenes creadas en assets/og/")
