#!/usr/bin/env python3
"""Mete Galaga dentro de la ventana del header terminal, bajo el marcador.

Uso: FECHA_NACIMIENTO=AAAA-MM-DD unir_svg.py galaga.svg terminal.svg calendario.json salida.svg
Falla sin escribir la salida si el formato de entrada cambia: se conserva la última imagen buena.
La estructura esperada es la de readme-atelier v1.0.0, fijada en el workflow.
"""
from datetime import date
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import seccion_mision as mision

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


def unir(galaga, terminal, lvl, score):
    galaga, ciclo, ciclo_nuevo = mision.alargar_ciclo(galaga)
    g_ancho, g_alto, g_contenido = trocear(galaga)
    t_ancho, t_alto, t_contenido = trocear(terminal)
    if TITULO.search(t_contenido) is None or (t_ancho, t_alto) != (ANCHO, ALTO_TERMINAL) or CAPAS_CRT not in t_contenido or BORDE not in t_contenido:
        raise ValueError("el terminal no tiene la estructura esperada")
    t_contenido = mision.creditos(t_contenido)
    titulo = TITULO.search(t_contenido)

    extra = round(g_alto * ANCHO / g_ancho)
    total = ALTO_TERMINAL + extra + mision.ALTO_MARCADOR
    capas = t_contenido.index(CAPAS_CRT)
    y_juego = ALTO_BARRA + mision.ALTO_MARCADOR

    cabeza = acotar_css(t_contenido[:titulo.start()]).replace(
        'width="840" height="300"', f'width="840" height="{total}"')
    cuerpo = acotar_css(t_contenido[titulo.end():capas])
    cola = t_contenido[capas:].replace(
        'width="840" height="300"', f'width="840" height="{total}"').replace(
        'width="839" height="299"', f'width="839" height="{total - 1}"')

    pantalla = (f'<svg x="0" y="{y_juego}" width="{ANCHO}" height="{extra}" '
                f'viewBox="0 0 {g_ancho:g} {g_alto:g}">{g_contenido}</svg>')
    salida = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{ANCHO}" height="{total}" viewBox="0 0 {ANCHO} {total}" fill="none" role="img" '
        f'aria-label="Ventana de terminal con Galaga sobre mi gráfico de contribuciones y mi perfil">'
        f'{cabeza}<g class="ra-term">{titulo.group(0)}</g>{mision.marcador(ALTO_BARRA, ANCHO, lvl, score)}{pantalla}'
        f'{mision.pantalla_final(y_juego, ANCHO, extra, ciclo, ciclo_nuevo)}'
        f'<g class="ra-term" transform="translate(0 {extra + mision.ALTO_MARCADOR})">{cuerpo}</g>{cola}</svg>'
    )
    ET.fromstring(salida)  # XML roto: mejor fallar que publicar una imagen rota.
    if "<script" in salida:
        raise ValueError("una entrada contiene <script>")
    return salida


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    galaga, terminal, calendario, destino = sys.argv[1:]
    with open(galaga, encoding="utf-8") as f:
        g = f.read()
    with open(terminal, encoding="utf-8") as f:
        t = f.read()
    with open(calendario, encoding="utf-8") as f:
        score = json.load(f)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    lvl = mision.edad(os.environ["FECHA_NACIMIENTO"], date.today())
    salida = unir(g, t, lvl, score)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(salida)


if __name__ == "__main__":
    main()
