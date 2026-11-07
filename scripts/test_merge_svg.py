#!/usr/bin/env python3
"""Checks for merge_svg.py. Usage: test_merge_svg.py"""
from datetime import date
import xml.etree.ElementTree as ET

import mission_section as mission
from merge_svg import merge

GALAGA = ('<svg width="1166" height="259" xmlns="http://www.w3.org/2000/svg"><text>Nov</text>'
          '<rect><animate attributeName="fill" calcMode="discrete" dur="10000ms" repeatCount="indefinite" '
          'values="#0e4429;transparent" keyTimes="0;1"/></rect>'
          '<circle><animate attributeName="cy" from="-2" to="261" dur="5991ms" repeatCount="indefinite"/></circle></svg>')
TERMINAL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="840" height="300" viewBox="0 0 840 300">'
    '<style>text{fill:red}.ra-fg{fill:green}@media x{*{animation:none}}</style>'
    '<defs><clipPath id="ra-clip"><rect width="840" height="300" rx="12"/></clipPath></defs>'
    '<g clip-path="url(#ra-clip)"><rect width="840" height="300" fill="#07090a"/>'
    '<text x="420" y="19.5">title</text><text x="28" y="66">whoami</text>'
    '<text x="548" y="66">username</text><text><tspan>Stars</tspan><tspan>: 0</tspan></text>'
    '<text><tspan>Commits</tspan><tspan>: 392 / 12mo</tspan></text><text><tspan>Since</tspan><tspan>: 2014</tspan></text>'
    '<rect x="548" y="262" width="30" height="14"/>'
    '<rect width="840" height="300" fill="url(#ra-scan)"/>'
    '<rect x=".5" y=".5" width="839" height="299" rx="11.5"/></g></svg>'
)

output = merge(GALAGA, TERMINAL, 42, 400)
root = ET.fromstring(output)
assert root.get("height") == "515" and root.get("width") == "840", root.attrib
assert 'height="300"' not in output and 'height="299"' not in output
assert 'y="58"' in output and 'viewBox="0 0 1166 259"' in output
assert ".ra-term text{fill:red}" in output and ".ra-term *{animation:none}" in output
assert ".ra-fg{fill:green}" in output and ".ra-term .ra-fg" not in output
# Order: title bar, scoreboard, Galaga, end screen, shifted content and CRT layers on top of everything.
order = [output.index(t) for t in ("title", "SCORE", "Nov", "ALL BUGS CLEARED", 'translate(0 215)', "whoami", "url(#ra-scan)")]
assert order == sorted(order), order

# Cycle: the board stays empty during the pause and unrelated animations do not change.
assert 'dur="16000ms"' in output and 'keyTimes="0;0.625;1"' in output
assert 'values="#0e4429;transparent;transparent"' in output and 'dur="5991ms"' in output
assert 'keyTimes="0;0.625;0.875"' in output and 'keyTimes="0;0.875"' in output and "DEPLOYING TO PROD..." in output

# Scoreboard and credits.
assert ">42<" in output and ">400<" in output and "ENGINEER" in output and "HORDE" in output and "1UP" not in output
assert "Starring 392 commits" in output and "On GitHub since 2014" in output and "Donostia" in output
assert "Stars" not in output and "username" not in output and 'x="548" y="262"' in output

# Age: changes exactly on the birthday.
assert mission.age("2000-06-15", date(2030, 6, 14)) == 29
assert mission.age("2000-06-15", date(2030, 6, 15)) == 30

for bad, reason in (("<g></g>", "not an SVG"),
                    ('<svg xmlns="http://www.w3.org/2000/svg"></svg>', "no sizes"),
                    ('<svg width="840" height="300"><text>no markers</text></svg>', "other structure")):
    try:
        merge(GALAGA, bad, 42, 400)
    except ValueError:
        continue
    raise AssertionError(reason)
for bad, reason in (('<svg width="1" height="1"><b></svg>', "no cycle"),
                    ('<svg width="1" height="1"><script/></svg>', "no cycle"),
                    (GALAGA.replace("</svg>", "<b></svg>"), "broken XML"),
                    (GALAGA.replace("</svg>", "<script/></svg>"), "script"),
                    (GALAGA.replace('keyTimes="0;1"', 'keyTimes="0;0.5"'), "incomplete cycle")):
    try:
        merge(bad, TERMINAL, 42, 400)
    except (ValueError, ET.ParseError):
        continue
    raise AssertionError(reason)

print("ok")
