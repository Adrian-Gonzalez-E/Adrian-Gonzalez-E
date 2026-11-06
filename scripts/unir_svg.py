#!/usr/bin/env python3
"""Mete Galaga dentro de la ventana del header terminal, bajo la barra de título.

Uso: unir_svg.py galaga.svg terminal.svg salida.svg
Falla sin escribir la salida si el formato de entrada cambia: se conserva la última imagen buena.
La estructura esperada es la de readme-atelier v1.0.0, fijada en el workflow.
"""
import re
import sys
import xml.etree.ElementTree as ET

ANCHO = 840
ALTO_TERMINAL = 300
ALTO_BARRA = 30
SELECTOR_LIBRE = re.compile(r"(?<![\w.-])(text|\*)(?=\s*[,{])")
TITULO = re.compile(r'<text x="420"[^>]*>.*?</text>', re.S)
CAPAS_CRT = '<rect width="840" height="300" fill="url(#ra-scan)"'
BORDE = '<rect x=".5" y=".5" width="839" height="299"'


def trocear(svg):
    """Devuelve (ancho, alto, contenido interior) del SVG raíz."""
    raiz = re.search(r"<svg\b[^>]*>", svg)
    fin = svg.rfind("</svg>")
    if not raiz or fin < 0:
        raise ValueError("no es un SVG")
    medidas = [re.search(rf'\b{a}="(\d+(?:\.\d+)?)"', raiz.group(0)) for a in ("width", "height")]
    if not all(medidas):
        raise ValueError("el SVG raíz no declara width y height")
    ancho, alto = (float(m.group(1)) for m in medidas)
    return ancho, alto, svg[raiz.end():fin]


def acotar_css(contenido):
    """Limita los selectores globales del terminal para que no afecten a Galaga."""
    def acotar(estilo):
        return estilo.group(1) + SELECTOR_LIBRE.sub(r".ra-term \1", estilo.group(2)) + estilo.group(3)
    return re.sub(r"(<style\b[^>]*>)(.*?)(</style>)", acotar, contenido, flags=re.S)


def unir(galaga, terminal):
    g_ancho, g_alto, g_contenido = trocear(galaga)
    t_ancho, t_alto, t_contenido = trocear(terminal)
    titulo = TITULO.search(t_contenido)
    if (t_ancho, t_alto) != (ANCHO, ALTO_TERMINAL) or not titulo or CAPAS_CRT not in t_contenido or BORDE not in t_contenido:
        raise ValueError("el terminal no tiene la estructura esperada")

    extra = round(g_alto * ANCHO / g_ancho)
    total = ALTO_TERMINAL + extra
    capas = t_contenido.index(CAPAS_CRT)

    cabeza = acotar_css(t_contenido[:titulo.start()]).replace(
        'width="840" height="300"', f'width="840" height="{total}"')
    cuerpo = acotar_css(t_contenido[titulo.end():capas])
    cola = t_contenido[capas:].replace(
        'width="840" height="300"', f'width="840" height="{total}"').replace(
        'width="839" height="299"', f'width="839" height="{total - 1}"')

    pantalla = (f'<svg x="0" y="{ALTO_BARRA}" width="{ANCHO}" height="{extra}" '
                f'viewBox="0 0 {g_ancho:g} {g_alto:g}">{g_contenido}</svg>')
    salida = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{ANCHO}" height="{total}" viewBox="0 0 {ANCHO} {total}" fill="none" role="img" '
        f'aria-label="Ventana de terminal con Galaga sobre mi gráfico de contribuciones y mi perfil">'
        f'{cabeza}<g class="ra-term">{titulo.group(0)}</g>{pantalla}'
        f'<g class="ra-term" transform="translate(0 {extra})">{cuerpo}</g>{cola}</svg>'
    )
    ET.fromstring(salida)  # XML roto: mejor fallar que publicar una imagen rota.
    if "<script" in salida:
        raise ValueError("una entrada contiene <script>")
    return salida


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    galaga, terminal, destino = sys.argv[1:]
    with open(galaga, encoding="utf-8") as f:
        g = f.read()
    with open(terminal, encoding="utf-8") as f:
        t = f.read()
    salida = unir(g, t)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(salida)


if __name__ == "__main__":
    main()
