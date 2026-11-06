#!/usr/bin/env python3
"""Comprobaciones de unir_svg.py. Uso: test_unir_svg.py"""
import xml.etree.ElementTree as ET

from unir_svg import unir

GALAGA = '<svg width="1166" height="259" xmlns="http://www.w3.org/2000/svg"><text>Nov</text></svg>'
TERMINAL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="840" height="300" viewBox="0 0 840 300">'
    '<style>text{fill:red}.ra-fg{fill:green}@media x{*{animation:none}}</style>'
    '<defs><clipPath id="ra-clip"><rect width="840" height="300" rx="12"/></clipPath></defs>'
    '<g clip-path="url(#ra-clip)"><rect width="840" height="300" fill="#07090a"/>'
    '<text x="420" y="19.5">titulo</text><text x="28" y="66">whoami</text>'
    '<rect width="840" height="300" fill="url(#ra-scan)"/>'
    '<rect x=".5" y=".5" width="839" height="299" rx="11.5"/></g></svg>'
)

salida = unir(GALAGA, TERMINAL)
raiz = ET.fromstring(salida)
assert raiz.get("height") == "487" and raiz.get("width") == "840", raiz.attrib
assert 'height="300"' not in salida and 'height="299"' not in salida
assert 'y="30"' in salida and 'viewBox="0 0 1166 259"' in salida
assert ".ra-term text{fill:red}" in salida and ".ra-term *{animation:none}" in salida
assert ".ra-fg{fill:green}" in salida and ".ra-term .ra-fg" not in salida
# Orden: barra, Galaga, contenido bajado y capas CRT por encima de todo.
orden = [salida.index(t) for t in ("titulo", "Nov", 'translate(0 187)', "whoami", "url(#ra-scan)")]
assert orden == sorted(orden), orden

for malo, motivo in (("<g></g>", "no es SVG"),
                     ('<svg xmlns="http://www.w3.org/2000/svg"></svg>', "sin medidas"),
                     ('<svg width="840" height="300"><text>sin marcadores</text></svg>', "otra estructura")):
    try:
        unir(GALAGA, malo)
    except ValueError:
        continue
    raise AssertionError(motivo)
for malo, motivo in (('<svg width="1" height="1"><b></svg>', "XML roto"),
                     ('<svg width="1" height="1"><script/></svg>', "script")):
    try:
        unir(malo, TERMINAL)
    except (ValueError, ET.ParseError):
        continue
    raise AssertionError(motivo)

print("ok")
