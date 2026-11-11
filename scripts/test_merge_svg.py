#!/usr/bin/env python3
"""Checks for merge_svg.py. Usage: test_merge_svg.py"""
from datetime import date
import xml.etree.ElementTree as ET

import coin_button
import mission_section as mission
import seasons
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

output = merge(GALAGA, TERMINAL, 42, 400, 7)
root = ET.fromstring(output)
assert root.get("height") == "515" and root.get("width") == "840", root.attrib
assert 'height="300"' not in output and 'height="299"' not in output
assert 'y="58"' in output and 'viewBox="0 0 1166 259"' in output
assert ".ra-term text{fill:red}" in output and ".ra-term *{animation:none}" in output
assert ".ra-fg{fill:green}" in output and ".ra-term .ra-fg" not in output
# Order: title bar, scoreboard, Galaga, end screen, shifted content and CRT layers on top of everything.
order = [output.index(t) for t in ("title", "SCORE", "Nov", "ALL BUGS CLEARED", 'translate(0 215)', "whoami", "url(#ra-scan)")]
assert order == sorted(order), order

# A single game: its last frame freezes, and unrelated animations keep looping.
assert 'dur="10000ms" repeatCount="1" fill="freeze"' in output and 'values="#0e4429;transparent" keyTimes="0;1"' in output
assert 'dur="5991ms" repeatCount="indefinite"' in output
# End screen: success when the last block falls, then the call to insert a coin stays.
assert 'keyTimes="0;0.714286;1"' in output and 'dur="14000ms" fill="freeze"' in output
assert '<set attributeName="opacity" to="1" begin="14000ms" fill="freeze"/>' in output
assert "INSERT COIN TO CONTINUE" in output and "DEPLOYING" not in output

# Scoreboard and credits.
assert ">42<" in output and ">400<" in output and "ENGINEER" in output and "HORDE" in output and "1UP" not in output
assert "COINS" in output and ">7<" in output
assert "Starring 392 commits" in output and "On GitHub since 2014" in output and "Donostia" in output
assert "Stars" not in output and "username" not in output and 'x="548" y="262"' in output

# Seasons: exact limits, forced preview and valid XML; nothing is added outside of them.
assert seasons.current(date(2030, 11, 30)) is None and seasons.current(date(2030, 12, 1)) == "winter"
assert seasons.current(date(2031, 1, 6)) == "winter" and seasons.current(date(2031, 1, 7)) is None
assert seasons.current(date(2030, 6, 20)) is None and seasons.current(date(2030, 6, 21)) == "summer"
assert seasons.current(date(2030, 6, 27)) == "summer" and seasons.current(date(2030, 6, 28)) is None
assert seasons.current(date(2030, 9, 14)) is None and seasons.current(date(2030, 9, 15)) == "zinemaldia"
assert seasons.current(date(2030, 10, 1)) is None
assert seasons.resolve("auto", date(2030, 6, 1)) is None and seasons.resolve("", date(2030, 12, 1)) == "winter"
assert seasons.resolve("winter", date(2030, 6, 1)) == "winter"
try:
    seasons.resolve("monsoon", date(2030, 6, 1))
    raise AssertionError("unknown season accepted")
except ValueError:
    pass
SNOW_MARK = 'id="season-flake"'
assert SNOW_MARK not in output and "ZINEMALDIA" not in output and "SUMMER IS HERE" not in output
for season, mark in (("winter", SNOW_MARK), ("summer", "SUMMER IS HERE"), ("zinemaldia", "ZINEMALDIA SEASON")):
    themed = merge(GALAGA, TERMINAL, 42, 400, 7, season)
    assert mark in themed and themed.index(mark) < themed.index("url(#ra-scan)\"/>"), season

# Age: changes exactly on the birthday.
assert mission.age("2000-06-15", date(2030, 6, 14)) == 29
assert mission.age("2000-06-15", date(2030, 6, 15)) == 30

for bad, reason in (("<g></g>", "not an SVG"),
                    ('<svg xmlns="http://www.w3.org/2000/svg"></svg>', "no sizes"),
                    ('<svg width="840" height="300"><text>no markers</text></svg>', "other structure")):
    try:
        merge(GALAGA, bad, 42, 400, 7)
    except ValueError:
        continue
    raise AssertionError(reason)
for bad, reason in (('<svg width="1" height="1"><b></svg>', "no cycle"),
                    ('<svg width="1" height="1"><script/></svg>', "no cycle"),
                    (GALAGA.replace("</svg>", "<b></svg>"), "broken XML"),
                    (GALAGA.replace("</svg>", "<script/></svg>"), "script"),
                    (GALAGA.replace('keyTimes="0;1"', 'keyTimes="0;0.5"'), "incomplete cycle")):
    try:
        merge(bad, TERMINAL, 42, 400, 7)
    except (ValueError, ET.ParseError):
        continue
    raise AssertionError(reason)

# Button: off until the given moment, then lit; the path of the text is shared by both states.
lit = coin_button.button(87400)
assert lit.count('<set attributeName="opacity" to="1" begin="87400ms" fill="freeze"/>') == 2
assert lit.index('fill="#6b5a2a"') < lit.index('fill="#febc2e"') and "<script" not in lit and 'role="img"' in lit
assert '<set attributeName="opacity" to="0" begin="87400ms" fill="freeze"/>' in lit
assert lit.count('fill="#febc2e"') == 1 and lit.count('fill="#6b5a2a"') == 1

print("ok")
