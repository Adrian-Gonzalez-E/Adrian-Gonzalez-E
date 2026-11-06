#!/usr/bin/env python3
"""Comprobaciones de unir_svg.py. Uso: test_unir_svg.py"""
from datetime import date
import xml.etree.ElementTree as ET

import seccion_mision as mision
from unir_svg import unir

GALAGA = ('<svg width="1166" height="259" xmlns="http://www.w3.org/2000/svg"><text>Nov</text>'
          '<rect><animate attributeName="fill" calcMode="discrete" dur="10000ms" repeatCount="indefinite" '
          'values="#0e4429;transparent" keyTimes="0;1"/></rect>'
          '<circle><animate attributeName="cy" from="-2" to="261" dur="5991ms" repeatCount="indefinite"/></circle></svg>')
TERMINAL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="840" height="300" viewBox="0 0 840 300">'
    '<style>text{fill:red}.ra-fg{fill:green}@media x{*{animation:none}}</style>'
    '<defs><clipPath id="ra-clip"><rect width="840" height="300" rx="12"/></clipPath></defs>'
    '<g clip-path="url(#ra-clip)"><rect width="840" height="300" fill="#07090a"/>'
    '<text x="420" y="19.5">titulo</text><text x="28" y="66">whoami</text>'
    '<text x="548" y="66">usuario</text><text><tspan>Stars</tspan><tspan>: 0</tspan></text>'
    '<text><tspan>Commits</tspan><tspan>: 392 / 12mo</tspan></text><text><tspan>Since</tspan><tspan>: 2014</tspan></text>'
    '<rect x="548" y="262" width="30" height="14"/>'
    '<rect width="840" height="300" fill="url(#ra-scan)"/>'
    '<rect x=".5" y=".5" width="839" height="299" rx="11.5"/></g></svg>'
)

salida = unir(GALAGA, TERMINAL, 42, 400)
raiz = ET.fromstring(salida)
assert raiz.get("height") == "515" and raiz.get("width") == "840", raiz.attrib
assert 'height="300"' not in salida and 'height="299"' not in salida
assert 'y="58"' in salida and 'viewBox="0 0 1166 259"' in salida
assert ".ra-term text{fill:red}" in salida and ".ra-term *{animation:none}" in salida
assert ".ra-fg{fill:green}" in salida and ".ra-term .ra-fg" not in salida
# Orden: barra, marcador, Galaga, pantalla final, contenido bajado y capas CRT por encima de todo.
orden = [salida.index(t) for t in ("titulo", "SCORE", "Nov", "ALL BUGS CLEARED", 'translate(0 215)', "whoami", "url(#ra-scan)")]
assert orden == sorted(orden), orden

# Ciclo: el tablero se queda vacío durante la pausa y las animaciones ajenas no cambian.
assert 'dur="16000ms"' in salida and 'keyTimes="0;0.625;1"' in salida
assert 'values="#0e4429;transparent;transparent"' in salida and 'dur="5991ms"' in salida
assert 'keyTimes="0;0.625;0.875"' in salida and 'keyTimes="0;0.875"' in salida and "DEPLOYING TO PROD..." in salida

# Marcador y créditos.
assert ">42<" in salida and ">400<" in salida and "ENGINEER" in salida and "HORDE" in salida and "1UP" not in salida
assert "Starring 392 commits" in salida and "On GitHub since 2014" in salida and "Donostia" in salida
assert "Stars" not in salida and "usuario" not in salida and 'x="548" y="262"' in salida

# Edad: cambia justo el día del cumpleaños.
assert mision.edad("2000-06-15", date(2030, 6, 14)) == 29
assert mision.edad("2000-06-15", date(2030, 6, 15)) == 30

for malo, motivo in (("<g></g>", "no es SVG"),
                     ('<svg xmlns="http://www.w3.org/2000/svg"></svg>', "sin medidas"),
                     ('<svg width="840" height="300"><text>sin marcadores</text></svg>', "otra estructura")):
    try:
        unir(GALAGA, malo, 42, 400)
    except ValueError:
        continue
    raise AssertionError(motivo)
for malo, motivo in (('<svg width="1" height="1"><b></svg>', "sin ciclo"),
                     ('<svg width="1" height="1"><script/></svg>', "sin ciclo"),
                     (GALAGA.replace("</svg>", "<b></svg>"), "XML roto"),
                     (GALAGA.replace("</svg>", "<script/></svg>"), "script"),
                     (GALAGA.replace('keyTimes="0;1"', 'keyTimes="0;0.5"'), "ciclo incompleto")):
    try:
        unir(malo, TERMINAL, 42, 400)
    except (ValueError, ET.ParseError):
        continue
    raise AssertionError(motivo)

print("ok")
